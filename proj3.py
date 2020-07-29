import random
import select
import threading
from socket import *
import socket

serverHost = socket.gethostname()  # get local machine name
PORT = 55555


class Client:

    def __init__(self):
        self.__clientsocket = tcp_clientSocket

    def clientReceiveThread(self):
        while True:
            try:
                answer = self.__clientsocket.recv(1024).decode()
                print("S :", answer)  # Server says
                if answer == "Bye" or answer == "bye":  # server wants to end the connection
                    break
            except Exception:
                print('Connection closed by client.')
                break
        self.__clientsocket.close()

    def clientSendThread(self):
        while True:
            try:
                msg = input()  # Client says
                self.__clientsocket.send(msg.encode())
                if msg == "Bye" or msg == "bye":  # client wants to end the connection
                    break
            except Exception:
                print('Connection closed by Server.')
                break
        self.__clientsocket.close()

    def runClient(self):
        rcvthread = threading.Thread(target=self.clientReceiveThread)
        sendthread = threading.Thread(target=self.clientSendThread)
        rcvthread.start()
        sendthread.start()


class Server:

    def __init__(self):
        self.__serversocket = connectionSocket

    def serverReceiveThread(self):
        while True:
            try:
                answer = self.__serversocket.recv(1024).decode()
                print("C :", answer)  # Client says
                if answer == "Bye" or answer == "bye":  # client wants to end the connection
                    break
            except Exception:
                print('Connection closed by Server.')
                break
        self.__serversocket.close()

    def serverSendThread(self):
        while True:
            try:
                msg = input()  # Server says
                self.__serversocket.send(msg.encode())
                if msg == "Bye" or msg == "bye":  # server wants to end the connection
                    break
            except Exception:
                print('Connection closed by client.')
                break
        self.__serversocket.close()

    def runServer(self):
        rcvthread = threading.Thread(target=self.serverReceiveThread)
        sendthread = threading.Thread(target=self.serverSendThread)
        rcvthread.start()
        sendthread.start()


if __name__ == '__main__':

    workingMode = input('Enter mode:\n')  # broadcast or listen

    # Do in proper mode
    if workingMode == 'broadcast':

        # underlying network is using IPV4 & creating UDP socket
        udp_clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        # using select to send broadcast request every 2.0 seconds
        while True:
            udp_clientSocket.sendto('Hello'.encode(), ('<broadcast>', PORT))
            print("Hello to all listeners!")
            udp_clientSocket.setblocking(0)
            ready = select.select([udp_clientSocket], [], [], 2.0)
            if ready[0]:
                acceptedPort, serverAddress = udp_clientSocket.recvfrom(1024)
                print("Connection accepted with port " + str(int(acceptedPort)))
                break

        # underlying network is using IPV4 & creating TCP socket
        tcp_clientSocket = socket.socket(AF_INET, SOCK_STREAM)
        tcp_clientSocket.connect((serverHost, int(acceptedPort)))

        # chat initiation
        print("Chat initiation request sent...")
        tcp_clientSocket.send("Chat initiation".encode())
        response = tcp_clientSocket.recv(1024).decode()
        # chat started
        p = Client()
        p.runClient()

    elif workingMode == 'listen':
        # underlying network is using IPV4 & creating UDP socket
        udp_serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)  # to enable using one port again
        udp_serverSocket.bind(('', PORT))  # '' instead of serverHost
        recievedmsg, clientAddress = udp_serverSocket.recvfrom(1024)
        print("Hello received from a broadcaster...")
        serverPort = random.randint(2000, 60000)  # port can be a number between 1024-65535
        udp_serverSocket.sendto(str(serverPort).encode(), clientAddress)
        print("I am ready on port " + str(serverPort))

        # underlying network is using IPV4 & creating TCP socket
        tcp_serverSocket = socket.socket(AF_INET, SOCK_STREAM)
        tcp_serverSocket.bind((serverHost, serverPort))
        tcp_serverSocket.listen(1)  # wait for client connection
        connectionSocket, addr = tcp_serverSocket.accept()

        # chat initiation
        request = connectionSocket.recv(1024).decode()
        print(request + " request received!")
        print("Let's chat...")
        connectionSocket.send("Let's chat".encode())
        # chat started
        p = Server()
        p.runServer()
