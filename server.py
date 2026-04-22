import http.server
import socketserver
import json
import os

PORT = 8000
DIRECTORY = "."

class RegistrationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS for all domains (e.g. Live Server on 5500, file:///, etc.)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_GET(self):
        # Clean URLs: map / to home.html and /path to /path.html if it exists
        if self.path == '/':
            self.path = '/home.html'
        elif self.path in ['/reg', '/student', '/ui']:
            self.path += '.html'
        return super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # Allow requests to /register specifically
        if self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                new_record = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response(400, 'Invalid JSON')
                return
            
            file_path = 'studentreg.json'
            current_data = []
            
            # Read existing data
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                        if content:
                            current_data = json.loads(content)
                except Exception as e:
                    print("Could not read existing json data:", e)

            # Check for existing USN
            exists = any(r.get('usn').lower() == new_record.get('usn').lower() for r in current_data)
            
            if exists:
                self.send_error_response(400, 'USN is already registered')
                return

            current_data.append(new_record)
            
            # Persist data to the actual studentreg.json
            try:
                with open(file_path, 'w') as f:
                    json.dump(current_data, f, indent=4)
                
                # Send Success Response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                print(f"Successfully registered student: {new_record.get('usn')} and saved to studentreg.json!")
                
            except Exception as e:
                self.send_error_response(500, f'Server file write error: {str(e)}')
        else:
            # For other POST requests, or if someone tries to POST to a file
            self.send_response(404)
            self.end_headers()
            
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode('utf-8'))

# Setup gracefully
try:
    with socketserver.TCPServer(("", PORT), RegistrationHandler) as httpd:
        print(f"==================================================")
        print(f" SERVER RUNNING SAFELY AT: http://localhost:{PORT}")
        print(f"==================================================")
        print("Registration / POST endpoints are active.")
        print("Use Ctrl+C here to stop the server when done.")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer gracefully shut down.")
