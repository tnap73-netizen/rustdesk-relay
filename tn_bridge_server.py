"""
TN Bridge Server — runs on TN Windows machine
Listens on localhost ONLY (127.0.0.1), only reachable via RustDesk TCP tunnel
Run: python tn_bridge_server.py
"""
import subprocess
import socket
import json
import threading
import os

HOST = '127.0.0.1'
PORT = 8765
SECRET = os.environ.get('BRIDGE_SECRET', 'changeme')

def handle_client(conn, addr):
    try:
        data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            # Accept message when we have valid JSON
            try:
                msg = json.loads(data.decode().strip())
                break
            except json.JSONDecodeError:
                continue

        if not data:
            return

        msg = json.loads(data.decode().strip())

        if msg.get('secret') != SECRET:
            response = json.dumps({'error': 'unauthorized'})
            conn.sendall(response.encode() + b'\n')
            return

        cmd = msg.get('cmd', '')
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        response = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        conn.sendall(json.dumps(response).encode() + b'\n')

    except Exception as e:
        try:
            conn.sendall(json.dumps({'error': str(e)}).encode() + b'\n')
        except:
            pass
    finally:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f'TN Bridge Server listening on {HOST}:{PORT}')
    print('Only reachable via RustDesk TCP tunnel')

    while True:
        conn, addr = server.accept()
        print(f'Connection from {addr}')
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    main()
