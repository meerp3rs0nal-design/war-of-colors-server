import asyncio
import json
import random
import string
import websockets

# Store rooms: { room_code: { "players": [ws1, ws2], "player_count": X, "started": False, "current_turn_idx": 0 } }
ROOMS = {}

def generate_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if code not in ROOMS:
            return code

async def handler(websocket):
    room_code = None
    player_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "create_room":
                room_code = generate_room_code()
                ROOMS[room_code] = {
                    "players": [websocket],
                    "player_count": data["player_count"],
                    "started": False,
                    "current_turn_idx": 0
                }
                player_id = 1
                await websocket.send(json.dumps({"type": "room_created", "room_code": room_code, "player_id": player_id}))

            elif action == "join_room":
                code = data.get("room_code", "").upper()
                if code in ROOMS:
                    room = ROOMS[code]
                    if len(room["players"]) < room["player_count"] and not room["started"]:
                        room["players"].append(websocket)
                        room_code = code
                        player_id = len(room["players"])
                        
                        await websocket.send(json.dumps({"type": "joined_success", "room_code": room_code, "player_id": player_id}))
                        
                        if len(room["players"]) == room["player_count"]:
                            room["started"] = True
                            for idx, ws in enumerate(room["players"]):
                                await ws.send(json.dumps({"type": "start_game"}))
                    else:
                        await websocket.send(json.dumps({"type": "error", "message": "Room full or match already started."}))
                else:
                    await websocket.send(json.dumps({"type": "error", "message": "Invalid Room Code."}))

            elif action == "make_move":
                if room_code in ROOMS:
                    for ws in ROOMS[room_code]["players"]:
                        if ws != websocket:
                            await ws.send(json.dumps({
                                "type": "opponent_move",
                                "node_id": data["node_id"]
                            }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if room_code in ROOMS:
            if websocket in ROOMS[room_code]["players"]:
                ROOMS[room_code]["players"].remove(websocket)
            if not ROOMS[room_code]["players"]:
                del ROOMS[room_code]
            else:
                for ws in ROOMS[room_code]["players"]:
                    await ws.send(json.dumps({"type": "opponent_disconnected"}))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future() # run forever

if __name__ == "__main__":
    print("Starting server on port 8765...")
    asyncio.run(main())
