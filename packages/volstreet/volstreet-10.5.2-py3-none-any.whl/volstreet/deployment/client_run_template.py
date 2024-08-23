from volstreet import (
    Client,
    run_client,
    Manager,
    set_price_limit_buffer,
    fetch_book,
    load_combine_save_json_data,
)

if __name__ == "__main__":
    client = Client.from_name("{client_name}")
    price_manager = Manager()
    order_manager = Manager()
    set_price_limit_buffer(0.1)
    run_client(
        client,
        True,
        price_socket_manager=price_manager,
        order_socket_manager=order_manager,
    )
    todays_orderbook = fetch_book("orderbook")
    load_combine_save_json_data(todays_orderbook, f"{client.user}\\orderbook.json")
    client.terminate()
    price_manager.shutdown()
    order_manager.shutdown()
