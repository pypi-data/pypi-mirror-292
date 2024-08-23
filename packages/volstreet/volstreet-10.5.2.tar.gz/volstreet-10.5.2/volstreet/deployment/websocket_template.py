import zmq
from volstreet import PriceWebsocket, Client, Index, get_n_dte_indices
from volstreet.angel_interface.dummies import DummyManager
import os
from types import MethodType


def get_option_tokens(indices: list = None, dtes: list = None):
    # Setting up an indices list
    indices = (
        [
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
            "MIDCPNIFTY",
            "SENSEX",
        ]
        if indices is None
        else indices
    )
    indices = [Index(i) for i in indices]
    dtes = [0, 1] if dtes is None else dtes
    indices = get_n_dte_indices(*indices, dtes=dtes, safe=True)
    all_tokens = []
    for i in indices:
        tokens = i.get_available_strikes(expiry=i.current_expiry, with_tokens=True)
        tokens = list(zip(*tokens["CE"]))[1] + list(zip(*tokens["PE"]))[1]
        all_tokens += tokens
    return all_tokens


def start_master_price_websocket(
    port: str = "tcp://*:5555", tokens_to_subscribe: list = None
):
    tokens_to_subscribe = [] if tokens_to_subscribe is None else tokens_to_subscribe

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(port)
    try:

        manager = DummyManager()
        ws = PriceWebsocket.from_active_session(manager=manager, socket=socket)
        og_on_open = ws.on_open

        def on_open(self, wsapp):
            og_on_open(wsapp)
            self.subscribe(tokens_to_subscribe)

        ws.on_open = MethodType(on_open, ws)

        ws.run()

    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    route = "tcp://*:5555"
    # Setting up a websocket
    c = Client(
        os.getenv("{client_name}_USER"),
        os.getenv("{client_name}_PIN"),
        os.getenv("{client_name}_API_KEY_2"),
        os.getenv("{client_name}_AUTHKEY"),
    )
    c.login()

    # Getting tokens to subscribe
    tkns = get_option_tokens()
    start_master_price_websocket(tokens_to_subscribe=tkns)
