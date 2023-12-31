import asyncio
import json
import websockets

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

                    if message_data.get("type") == "bid_increment":
                        add_amount = int(message_data.get("number", 0))
                        latest_price += add_amount
                        print(f"Add Amount: {add_amount}")
                        print(f"Latest price: {latest_price}")

                        # Broadcast latest price to all connected clients
                        broadcast_message = json.dumps({"type": "latest_price", "number": latest_price})
                        await asyncio.wait([client.send(broadcast_message) for client in connected_clients])
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
    loop.run_forever()
