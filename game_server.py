"""Run the game locally: python game_server.py, then open http://localhost:8000"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

if __name__ == "__main__":
    server = ThreadingHTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
    print("Iron Horizon is running at http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
