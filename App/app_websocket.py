import asyncio
import json
import websockets

latest_price = 500


async def handler(websocket, path):
    global latest_price

    if path == '/api/1.0/update_bid':
        try:
            async for message in websocket:
                message_data = json.loads(message)

                if message_data.get("type") == "bid_increment":
                    add_amount = int(message_data.get("number", 0))
                    latest_price += add_amount
                    print(f"Add Amount: {add_amount}")
                    print(f"Latest price: {latest_price}")
                    await websocket.send(json.dumps({"type": "latest_price", "number": latest_price}))
                else:
                    print({"Error": "Wrong Payload"})

        except websockets.ConnectionClosed:
            print("Connection with client closed")
    else:
        print({"Error": "Wrong URL"})

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = websockets.serve(handler, "0.0.0.0", 9000)
    loop.run_until_complete(server)
    print("WebSocket server started")
    loop.run_forever()
