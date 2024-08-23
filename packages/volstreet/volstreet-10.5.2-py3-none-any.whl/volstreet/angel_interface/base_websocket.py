from abc import ABC, abstractmethod
import time
import threading
import websocket
import ssl
import os
from volstreet.config import logger
from volstreet.utils.core import current_time
from volstreet.utils.communication import notifier
from volstreet.angel_interface.active_session import ActiveSession


class BaseWebsocket(ABC):
    HEART_BEAT_MESSAGE = "ping"
    MAX_RETRY_ATTEMPT = 3
    RETRY_DELAY = 10
    NOTIFICATION_URL = os.getenv("WEBSOCKET_URL")

    def __init__(
        self,
        auth_token,
        api_key,
        client_code,
        feed_token,
        manager,
        **kwargs,
    ):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.wsapp = None
        self.last_pong_timestamp = None
        self.connected = manager.Value("b", False)
        self.intentionally_closed = manager.Value("b", False)
        self.data_bank = manager.dict()
        self.periodic_tasks = []

    @classmethod
    def from_active_session(cls, manager, **kwargs):
        auth_token = ActiveSession.login_data["data"]["jwtToken"]
        feed_token = ActiveSession.obj.getfeedToken()
        api_key = ActiveSession.obj.api_key
        client_code = ActiveSession.obj.userId
        return cls(auth_token, api_key, client_code, feed_token, manager, **kwargs)

    @property
    @abstractmethod
    def root_uri(self):
        pass

    @property
    @abstractmethod
    def heart_beat_interval(self):
        pass

    @property
    @abstractmethod
    def websocket_type(self):
        pass

    @abstractmethod
    def on_data(self, wsapp, message, data_type, continue_flag):
        pass

    def on_open(self, wsapp):
        self.connected.value = True
        notifier(
            f"{self.client_code} - {self.websocket_type} connected.",
            self.NOTIFICATION_URL,
        )
        self.start_periodic_tasks()

    def on_error(self, wsapp, error):
        notifier(
            f"{self.client_code} - {self.websocket_type} connection has faced an error: {error}",
            self.NOTIFICATION_URL,
        )

    def on_close(self, wsapp, close_status_code, close_msg):
        self.connected.value = False
        self.stop_periodic_tasks()
        if self.intentionally_closed.value:
            logger.info(
                f"{self.websocket_type} intentionally closed. Status code: {close_status_code}, Message: {close_msg}"
            )
        elif close_status_code not in [1000, 1001]:  # Normal closure status codes
            notifier(
                f"{self.client_code} - {self.websocket_type} connection closed for unknown reason. Status code: {close_status_code}, Message: {close_msg}",
                self.NOTIFICATION_URL,
            )

    def on_ping(self, wsapp, data):
        logger.info(
            f"{self.websocket_type} on_ping function ==> {data}, Timestamp: {current_time()}"
        )

    def on_pong(self, wsapp, data):
        self.last_pong_timestamp = current_time()

    def start_periodic_tasks(self):
        self.periodic_tasks.extend(
            [
                threading.Thread(target=self.periodically_send_heart_beat, daemon=True),
            ]
        )
        for task in self.periodic_tasks:
            task.start()

    def stop_periodic_tasks(self):
        for task in self.periodic_tasks:
            task.join(timeout=11)
        if any(task.is_alive() for task in self.periodic_tasks):
            notifier(
                f"{self.client_code} - {self.websocket_type} periodic tasks did not stop after 10 seconds.",
                self.NOTIFICATION_URL,
            )
        self.periodic_tasks.clear()

    def periodically_send_heart_beat(self):
        while self.connected.value:
            self.wsapp.send(self.HEART_BEAT_MESSAGE)
            time.sleep(self.heart_beat_interval)

    def connect(self):
        headers = {
            "Authorization": self.auth_token,
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token,
        }
        self.wsapp = websocket.WebSocketApp(
            self.root_uri,
            header=headers,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close,
            on_data=self.on_data,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
        )
        self.wsapp.run_forever(
            sslopt={"cert_reqs": ssl.CERT_NONE},
            ping_interval=self.heart_beat_interval,
            ping_payload=self.HEART_BEAT_MESSAGE,
        )

    def run(self):
        self.intentionally_closed.value = False
        retry_count = 0
        while not self.intentionally_closed.value:
            if retry_count >= self.MAX_RETRY_ATTEMPT:
                logger.warning(
                    f"{self.websocket_type} connection retry limit exceeded. Max attempts: {self.MAX_RETRY_ATTEMPT}"
                )
                break

            try:
                self.connect()
            except Exception as e:
                notifier(
                    f"{self.client_code} - Retrying {self.websocket_type} connection. Error: {e}"
                )
            finally:
                self.connected.value = False

            if not self.intentionally_closed.value:
                retry_count += 1
                logger.info(
                    f"{self.websocket_type} reconnecting. Attempt: {retry_count}"
                )
                time.sleep(self.RETRY_DELAY)
            else:
                break

    def close_connection(self):
        self.intentionally_closed.value = True
        if self.wsapp:
            self.wsapp.close()
        logger.info(f"{self.websocket_type} wsapp closed")
