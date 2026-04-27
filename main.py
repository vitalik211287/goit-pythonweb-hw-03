from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


jinja_env = Environment(
    loader=FileSystemLoader("."),
    autoescape=select_autoescape()
)

class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == "/":
            self.send_html_file("index.html")

        elif pr_url.path == "/message.html":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)


    def _render_template(self):
        template = jinja_env.get_template("index.html")
        return template.render()


    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself

        data = post_data.decode("utf-8")
        data_dict = dict(urllib.parse.parse_qsl(data))
        print(data_dict)

        with open("storage/data.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        messages[str(datetime.now())] = data_dict

        with open("storage/data.json", "w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
        

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler, port=3000):
    print("Starting the  server...")
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping the  server...")
    httpd.server_close()




if __name__ == "__main__":
    run(port=3000)
