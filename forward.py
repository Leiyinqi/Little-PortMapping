import argparse
import sys
from threading import Thread
import socket
from typing import List
import time


parser = argparse.ArgumentParser()
parser.add_argument("--server",help="local stream exchange")
parser.add_argument("-r",help="send end",type=int)
parser.add_argument("-l",help="receieve end",type=int)
parser.add_argument("--client",help="two ends stream exchange")
parser.add_argument("--host",help='remote host ip address')
arg = parser.parse_args()


class PortMapping():
    def __init__(self, arg:argparse.ArgumentParser):
        self.threadList = []
        self.ports = []
        self.streams:List[socket.socket] = []
        if arg.server:
            self.host = "0.0.0.0"
            self.ports.append(arg.r)
            self.ports.append(arg.l)
        elif arg.client:
            self.host = ["0.0.0.0",arg.host]
            self.ports.append(arg.r)
            self.ports.append(arg.l)
        else:
            # arg.print_usage()
            print("please use -h")
            sys.exit()
        
    def getAnotherSocket(self,conn):
        while True:
            if len(self.streams)<=1:
                time.sleep(1.5)
                continue
            else:
                for i in self.streams:
                    if i!= conn:
                        return i 

    def client(self,host,port):
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sk.connect((host,port))
        self.streams.append(sk)
        connAnother = self.getAnotherSocket(sk)

        while True:
            buff = sk.recv(1024)
            if not buff:
                break
            else:
                connAnother.sendall(buff)
        
    def server(self,port):
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sk.bind((self.host,port))
        sk.listen(1)
        conn , addr = sk.accept()
        self.streams.append(conn)
        print(f"Conection from {addr}")
        connAnother = self.getAnotherSocket(conn)

        while True:
            buff = conn.recv(1024)
            if not buff:
                break
            else:
                connAnother.sendall(buff)

    def main(self):
        if self.host == "0.0.0.0":
            for port in self.ports:
                self.threadList.append(Thread(target=self.server,args=(port,)))
            
        else:
            for (host,port) in zip(self.host,self.ports):
                print(f"connecting :{host}:{port}")
                self.threadList.append(Thread(target=self.client,args=(host,port,)))

        for i in self.threadList:
            i.start()
        for i in self.threadList:
            i.join()
    



if __name__ == "__main__":
    # main()
    ssh = PortMapping(arg)
    ssh.main()
