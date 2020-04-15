from socket import socket
from select import select
import re


# 主题功能
class HTTPServer:
    def __init__(self, host="0.0.0.0", port=80, html=None):
        self.host = host
        self.port = port
        self.html = html
        self.sockfd = socket()
        self.unblock_socket()
        self.address = (self.host, self.port)
        self.bind()
        self.rlist = [self.sockfd]
        self.wlist = []
        self.xlist = []
        self.response = ""

    def unblock_socket(self):
        self.sockfd.setblocking(False)

    def bind(self):
        self.sockfd.bind(self.address)

    def supervise(self):
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for i in rs:
                if i is self.sockfd:
                    c, address = i.accept()
                    print(f"Connecting with {address}")
                    c.setblocking(False)
                    self.rlist.append(c)
                else:
                    self.response_request(i)

    def response_request(self, i):
        # 中途测试
        request = i.recv(1024).decode()
        print(request)
        pattern = r"[A-Z]+\s+(/\S*)"
        try:
            # 获取请求内容
            info = re.match(pattern, request).group(1)
            print(info)
        except:
            # 客户端断开了
            self.rlist.remove(i)
            i.close()
        else:
            self.get_html(i, info)

    def get_html(self, socket, info):
        if info == "/":
            filename = self.html + '/index.html'
        else:
            filename = self.html + info
        # 打开网页
        try:
            f = open(filename,"rb")
        except:
            response_headers = "HTTP/1.1 404 NOT FOUND\r\n"
            response_headers += "Content-Type:text/html\r\n"
            response_headers += "\r\n"
            response_content = "<h1> Sorry....</h1>"
            self.response = (response_headers + response_content).encode()
        else:
            response_content = f.read()
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Content-Type:text/html\r\n"
            # 必不可少 否则图片无法打开
            response_headers += f"Content-Length:{len(response_content)}\r\n"
            response_headers += "\r\n"
            self.response = response_headers.encode() + response_content
        finally:
            # 将http响应发送给浏览器
            socket.send(self.response)

    # 启动服务
    def start(self):
        self.sockfd.listen(3)
        print("Listen the port %s" % self.port)
        self.supervise()


if __name__ == "__main__":
    """
    通过HTTPServer类累快速搭建服务
    """
    # 3. 有什么需要使用者提供：网络地址 网页路径
    my_host = "0.0.0.0"
    my_port = 8001
    my_html = "."

    # 1. 实例化对象
    httpd = HTTPServer(host=my_host, port=my_port, html=my_html)

    # 2.4. 调用方法启动服务
    httpd.start()
