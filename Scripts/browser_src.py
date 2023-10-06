from transcribe_pipeline import StreamingPlugin, TranscriptCommit
from urllib.parse import urlparse

import copy
import json
import http.server
import os
import socketserver
import threading
import time
import transcribe_pipeline
import typing

class HTTPServer:
    def __init__(self, port: int):
        self.port = port
        self.route_map = {}
        self.httpd = None

    def register_file_handler(self, http_method: str, path: str, file_path: str):
        print(f"File handler registered at {os.getcwd()}")
        def handler():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return 200, f.read().replace('%PORT%', str(self.port)), 'text/html'
            else:
                return 404, {'error': 'file not found'}, 'application/json'
        self.route_map[(http_method, path)] = handler

    def register_json_handler(self, http_method: str, path: str, handler):
        self.route_map[(http_method, path)] = handler

    def run(self):
        def handler(*args, **kwargs):
            MyHandler(http_server_instance=self, *args, **kwargs)

        with socketserver.TCPServer(("", self.port), handler) as httpd:
            self.httpd = httpd
            print(f"Webserver running at port {self.port}")
            httpd.serve_forever()
        print(f"Webserver exiting")
        self.httpd = None

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()


class MyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, http_server_instance=None, **kwargs):
        self.http_server_instance = http_server_instance
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        # TODO log if cfg["debug_mode_enabled"] is set
        return

    def do_GET(self):
        self.handle_request('GET')

    def handle_request(self, method: str):
        parsed_path = urlparse(self.path)
        if (method, parsed_path.path) in self.http_server_instance.route_map:
            status_code, response_content, content_type = \
                    self.http_server_instance.route_map[(method, parsed_path.path)]()
            self.send_response(status_code)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            if content_type == 'application/json':
                self.wfile.write(json.dumps(response_content).encode('utf-8'))
            else:
                self.wfile.write(response_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'not found'}).encode('utf-8'))


class BrowserSource(StreamingPlugin):
    def __init__(self, cfg: typing.Dict):
        port = cfg["browser_src_port"]
        print(f"Browser source running on port {port}")
        self.commits = []
        self.preview_commit = None
        self.http_server = HTTPServer(port)
        self.http_server.register_json_handler('GET', '/api/v0/transcript', self.get_transcript_json)

        index_html_path = os.path.join("Resources", "BrowserSource", "index.html")
        self.http_server.register_file_handler('GET', '/', index_html_path)
        self.http_server.register_file_handler('GET', '/index.html', index_html_path)

        # Start the HTTP server in a new thread
        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.start()

    def transform(self, commit: TranscriptCommit) -> TranscriptCommit:
        original_commit = commit
        commit = copy.deepcopy(original_commit)
        del commit.audio
        if commit.delta:
            self.commits.append(commit)
        # Limit commits to last N.
        now = time.time()
        self.commits = [commit for commit in self.commits]
        max_commits = 10
        if len(self.commits) > max_commits:
            self.commits = self.commits[-int(max_commits/2):]
        self.preview_commit = commit
        return original_commit

    # return (http_code, body, content_type)
    def get_transcript_json(self) -> typing.Tuple[int, str, str]:
        processed_commits = [vars(commit) for commit in self.commits]
        transcript_data = {
                'commits': processed_commits,
                'preview': vars(self.preview_commit) if self.preview_commit else None,
                'ts': time.time()
                }
        return 200, json.dumps(transcript_data), 'text/json'

    def run(self):
        self.http_server.run()

    def stop(self):
        self.http_server.stop()
        self.server_thread.join()


# Example usage
def my_callback() -> typing.Tuple[int, typing.Dict[str, str]]:
    return 200, {'message': 'Hello, world!'}, 'text/json'

if __name__ == '__main__':
    server = HTTPServer(port=8080)
    server.register_json_handler('GET', '/api/v0/transcript', my_callback)
    server.run()

