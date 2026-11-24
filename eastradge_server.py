from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
server = ThreadingHTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)

print("Eastradge MedInvest is running!")
print("Open: http://127.0.0.1:8080")
print("Press CTRL+C to stop.")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
finally:
    server.server_close()
