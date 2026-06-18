import asyncio
import http
from websockets.asyncio.server import serve
from websockets.http11 import Response

# 1. This function intercepts Render's HTTP health checks so it turns green
def health_check(connection, request):
    # If Render pings the server root, give it a clean "200 OK" HTTP response
    if request.path == "/":
        return Response(
            status_code=http.HTTPStatus.OK,
            reason_phrase="OK",
            headers=[("Content-Type", "text/plain")],
            body=b"Server is running",
        )
    return None  # Let normal WebSocket game connections pass through seamlessly

async def handler(websocket):
    # This is your main game connection handler
    async for message in websocket:
        # Put your game messages handling logic here
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    # 2. We pass 'process_request=health_check' inside the server setup
    async with serve(handler, "0.0.0.0", 10000, process_request=health_check):
        print("Server started successfully on port 10000...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
