#!/usr/bin/env python3
# coding: utf-8

# region Lincense
# Assignment Done by: AY Abdalla email: ayabdall@ualberta.ca
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# endregion

# region imports
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
# endregion

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def get_host_port(self,url):
        host = ""
        port = 80
        http_slash = url.find("://")+3 #oh how I wish I knew how to use regex
        if url.find(":",5) != -1:
            host_loc = url.find(":",5)
            last_slash = url.rfind("/",0,host_loc)
            host = url[last_slash+1:host_loc]
            port = url[host_loc+1:url.find("/",host_loc) if url.find("/",host_loc)!=-1 else None]
            path = url[url.find("/",host_loc):]
        else:
            host_loc = url.find("/",http_slash) if url.find("/",http_slash) != -1 else None 
            host = url[http_slash:host_loc]
            path = url[url.find("/",host_loc):]
        return host, int(port), path

        # host = ""
        # port = 80
        # http_slash = url.find("://") #oh how I wish I knew how to use regex
        # host_loc = url.find(":",5) if url.find(":",5) != -1 else url.find("/",http_slash)
        # last_slash = url.rfind("/",0,host_loc)
        # host = url[last_slash+1:host_loc]
        # port = url[host_loc+1:url.find("/",host_loc) if url.find("/",host_loc)!=-1 else None]
        # path = url[url.find("/",host_loc):]
        # return host, int(port), path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        first_space = data.find(" ")+1
        second_space = data.find(" ",first_space,-1)
        code = data[first_space: second_space]
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        if data.rfind("\n\n\n") != -1 : first_enter = data.rfind("\n\n\n") +3
        else: first_enter = data.find("\r\n\r\n")+4         
        data = data[first_enter:]
        return data
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        x = 0
        prev_part = None
        part = 0
        buffer = bytearray()
        buffer_size = 1024
        done = False
        while not done:
            if part: prev_part = part
            part = sock.recv(buffer_size)
            part_len = len(part)
            buffer_size_check = len(part)>=buffer_size
            x_check = not(x > 0)
            if (len(part)<=buffer_size):
                buffer.extend(part)
                return buffer.decode('utf-8')
            elif(x!=0):
                if prev_part != part: buffer.extend(part) 
                done = True
            elif(part):
                buffer.extend(part)
            x+=1
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        request = "GET "+ path + " HTTP/1.1\r\n"
        self.sendall(request)
        self.sendall("Host: "+ host+ "\r\n")
        self.sendall("Connection: Keep-Alive\r\n")

        self.sendall("\r\n")
        data = self.recvall(self.socket)
        code = self.get_code(data)
        code = int(code)
        body = self.get_body(data)
        self.close()
        print(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        request = "POST "+ path + " HTTP/1.1\r\n"
        self.sendall(request)
        Host_bit = "Host: "+ str(host)+":"+ str(port) +"\r\n"
        self.sendall(Host_bit)
        args_len = 0


        if args != None:
            for i, v in args.items():
                body+= str(i)+ "="+ str(v) +"&"
            body = body[:-1]
            args_len = len(body)

        cnt_type_len = len("Content-Type: application/json\r\n")
        self.sendall("Content-Type: application/json\r\n")
        cntnt_len= args_len+len(request)+cnt_type_len+len(Host_bit)+ len("Content-length: \r\n\r\n")
        self.sendall("Content-length: "+ str(len(body))+ "\r\n")
        self.sendall("\r\n")

        self.sendall(body)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        code = int(code)
        body = self.get_body(data)
        self.close()
        print(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
