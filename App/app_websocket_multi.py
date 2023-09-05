import asyncio
import json
import websockets
import redis
from server.utils.util import dir_last_updated
from message_q import prepare_data_to_message_queue

latest_price = 500
connected_clients = set()


async def handler(websocket, path):
    global latest_price
    global connected_clients

    # Add newly connected client to the set
    connected_clients.add(websocket)

    try:
        if path == '/api/1.0/update_bid':
            try:
                async for message in websocket:
                    message_data = json.loads(message)

                    if message_data.get("type") == "initialize":
                        print(f"Latest price: {latest_price}")
                        print('-' * 50)

                        # Broadcast latest price to the specific client entering auction page at first time
                        broadcast_message = json.dumps({"type": "latest_price", "number": latest_price})
                        await websocket.send(broadcast_message)

                    elif message_data.get("type") == "bid_increment":
                        add_amount = int(message_data.get("number", 0))
                        email = str(message_data.get("email"))
                        latest_price += add_amount
                        print(f"Add Amount: {add_amount}")
                        print(f"Latest price: {latest_price}")
                        print('-' * 50)

                        # Broadcast latest price to all connected clients
                        broadcast_message = json.dumps({"type": "latest_price", "number": latest_price})
                        await asyncio.wait([client.send(broadcast_message) for client in connected_clients])
                        
                        prepare_data_to_message_queue(latest_price, email)

                    elif message_data.get("type") == "trigger_notify_winner":
                        print('Notifying Winner')
                        print('-' * 50)
                        email = message_data.get("email")

                        # Internal response
                        internal_message = 'Notify Successfully'
                        # Broadcast notification info to the winner
                        broadcast_message = json.dumps({
                            "type": "broadcast_winner",
                            "email": email,
                            "auction_id": "test_auction_id",
                            "product_id": "test_product_id",
                            "final_bid_price": "test_final_bid_price"
                        })

                        await websocket.send(internal_message)
                        await asyncio.wait([client.send(broadcast_message) for client in connected_clients])
                        latest_price = 0
                    else:
                        print({"Error": "Wrong Payload"})

            except websockets.ConnectionClosed:
                print("Connection with client closed")
        else:
            print({"Error": "Wrong URL"})

    finally:
        # Remove client from the set when disconnected
        connected_clients.remove(websocket)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = websockets.serve(handler, "0.0.0.0", 9000)
    loop.run_until_complete(server)
    print("WebSocket server started")
    print('-' * 50)
    loop.run_forever()