import asyncio
import websockets
import http

# This function answers Render's health checks so it turns green
async def health_check(connection, request):
    # If Render pings the server normally, give it a clean "200 OK" response
    if request.path == "/":
        return http.HTTPStatus.OK, [("Content-Type", "text/plain")], b"Server is running"
    return None

async def handler(websocket):
    # Keep your existing game logic here inside your main handler loop!
    async for message in websocket:
        pass # (Leave your actual message handling code here)

async def main():
    # We add 'process_request=health_check' inside the server setup
    async with websockets.serve(handler, "0.0.0.0", 10000, process_request=health_check):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
