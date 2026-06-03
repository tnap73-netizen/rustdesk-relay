"""
TN Relay Server — runs on Railway
- Agent calls POST /cmd with JSON {secret, cmd}
- Relay forwards to TN client via persistent WebSocket
- TN client executes cmd and returns result
"""
import asyncio
import json
import os
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

SECRET = os.environ.get('BRIDGE_SECRET', 'BGSM2024')
TN_SECRET = os.environ.get('TN_SECRET', 'BGSM2024')

# Active TN WebSocket connection
tn_ws = None
pending_commands = {}  # cmd_id -> asyncio.Future

class CommandRequest(BaseModel):
    secret: str
    cmd: str
    timeout: int = 30

@app.get('/health')
async def health():
    return {'status': 'ok', 'tn_connected': tn_ws is not None}

@app.post('/cmd')
async def run_command(req: CommandRequest):
    global tn_ws
    if req.secret != SECRET:
        raise HTTPException(status_code=403, detail='Unauthorized')
    if tn_ws is None:
        raise HTTPException(status_code=503, detail='TN not connected')
    
    cmd_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    pending_commands[cmd_id] = future
    
    try:
        await tn_ws.send_text(json.dumps({'id': cmd_id, 'cmd': req.cmd}))
        result = await asyncio.wait_for(future, timeout=req.timeout)
        return JSONResponse(result)
    except asyncio.TimeoutError:
        pending_commands.pop(cmd_id, None)
        raise HTTPException(status_code=504, detail='Command timed out')
    except Exception as e:
        pending_commands.pop(cmd_id, None)
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket('/tn')
async def tn_endpoint(ws: WebSocket):
    global tn_ws
    # Authenticate TN client
    await ws.accept()
    auth = await ws.receive_text()
    auth_msg = json.loads(auth)
    if auth_msg.get('secret') != TN_SECRET:
        await ws.close(code=4003)
        return
    
    tn_ws = ws
    print(f'TN connected')
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            cmd_id = msg.get('id')
            if cmd_id and cmd_id in pending_commands:
                future = pending_commands.pop(cmd_id)
                if not future.done():
                    future.set_result(msg.get('result', {}))
    except WebSocketDisconnect:
        print('TN disconnected')
    finally:
        tn_ws = None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
