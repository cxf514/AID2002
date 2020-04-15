"""
    html web服务器后端实现
"""
from socket import socket
from select import select
import re


class HTTPServer:
    def __init__(self, host, port, html=None):
        self.host = host
        self.port = port
        self.html = html
        self.socket = socket()
        self.socket_unblock()
        self.address = (self.host, self.port)
        self.socket_bind()
        self.rlist = [self.socket]
        self.wlist = []
        self.xlist = []
        self.response = ""

    def socket_unblock(self):
        self.socket.setblocking(False)

    def socket_bind(self):
        self.socket.bind(self.address)

    def supervise(self):
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.socket:
                    i, address = r.accept()
                    print(f"Connecting with {address}")
                    i.setblocking(False)
                    self.rlist.append(i)
                else:
                    request = r.recv(1024).decode()
                    print(request)
                    try:
                        pattern = r"[A-Z]+\s+(/\S*)"
                        request = re.match(pattern, request).group(1)
                    except:
                        self.rlist.remove(r)
                        r.close()
                    else:
                        self.get_html(r, request)

    def get_html(self, r, request):
        if request == "/":
            filename = self.html + "/index.html"
        else:
            filename = self.html + request
        try:
            f = open(filename, "rb")
        except:
            response_header = "HTTP1.1 404 NOT FOUND\r\n"
            response_header += "Content-Type:text/html\r\n"
            response_header += "\r\n"
            response_body = "<h1> Sorry....</h1>"
            self.response = (response_header + response_body).encode()
        else:
            response_body = f.read()
            response_header = "HTTP1.1 200 OK\r\n"
            response_header += "Content-Type:text/html\r\n"
            response_header += f"Content-Length:{len(response_body)}\r\n"
            response_header += "\r\n"
            self.response = response_header.encode() + response_body
        finally:
            r.send(self.response)

    def start(self):
        self.socket.listen(3)
        print(f"Listening to the port {self.port}")
        self.supervise()


if __name__ == "__main__":
    # 服务器配置
    host = "127.0.0.1"
    port = 8000
    html = "."
    # 服务实现
    httpd = HTTPServer(host=host, port=port, html=html)
    httpd.start()
