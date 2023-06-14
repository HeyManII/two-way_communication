# Using python 3.8.5
# Chu Ka Wai 22073291g
# COMP 5311 assginment

from socket import *
import threading
import select

# define the host is local host 127.0.0.1
serverName = '127.0.0.1'
UDPserverPort = 10000
TCPserverPort = 12000

# create UDP socket for server
UDPserverSocket = socket(AF_INET, SOCK_DGRAM)
UDPserverSocket.bind((serverName, UDPserverPort))


# create TCP socket for server
TCPserverSocket = socket(AF_INET, SOCK_STREAM)
TCPserverSocket.bind((serverName, TCPserverPort))
TCPserverSocket.listen(1)


class UDP_connection:
    # initial the UDP socket for server
    def __init__(self, serverName = '127.0.0.1', Port = 12000):
        UDPserverSocket.settimeout(1)
        self.expected_seq_num = 0
    
    # close the UDP connection
    def __close__(self):
        UDPserverSocket.close()

    # implement rdt 3.0 to receive message
    def rdt_receive(self):
        global UDPclientAddress
        while True:
            try:
                # Receive packet from client
                packet, UDPclientAddress = UDPserverSocket.recvfrom(2048)
                seq_num, receive_message = packet.decode().split('|')
                
                # If sequence number match expected sequence number, send ACK to client
                # return message for furthur action
                if int(seq_num) == self.expected_seq_num:
                    ack = str(self.expected_seq_num)
                    UDPserverSocket.sendto(ack.encode(), UDPclientAddress)
                    self.expected_seq_num = self.expected_seq_num + 1
                    return receive_message
                    
                # If sequence number is less than expected sequence number, send ACK for last in-order packet
                elif int(seq_num) < self.expected_seq_num:
                    ack = str(self.expected_seq_num - 1)
                    UDPserverSocket.sendto(ack.encode(), UDPclientAddress)

            # If timeout, stop and wait for packet
            except UDPserverSocket.timeout:
                continue

    # implement rdt 3.0 to send message
    def rdt_send(self, data):
        global UDPclientAddress
        seq_num = self.expected_seq_num
        while True:
            # send message with sequence number to the client
            packet = str(seq_num) + '|' + data
            UDPserverSocket.sendto(packet.encode(), UDPclientAddress)

            try:
                # Wait for ACK with matching sequence number
                ack, UDPclientAddress = UDPserverSocket.recvfrom(2048)
                ack_seq_num = int(ack.decode())

                # If ACK matches expected sequence number, break loop and return to the main program
                if ack_seq_num == self.expected_seq_num:
                    self.expected_seq_num = self.expected_seq_num + 1
                    break

            # If timeout, resend the packet
            except UDPserverSocket.timeout:
                continue

    # receive a message from client
    # if it is a lowercase message, change it to uppercase and send back to client
    # if it is a upperacse message, it is the reply from client
    def read_then_write(self):
        global UDPclientAddress
        while True:
            try:
                message = self.rdt_receive()
                modifiedMessage = message.upper()
                if message != modifiedMessage:
                    self.rdt_send(modifiedMessage)
                    print ('Connection from client(UDP):', UDPclientAddress, 'Received a message and return in uppercase:', modifiedMessage)
                    break
                else:
                    print ('Receive in Uppercase: ', message)
                    break

            except:
                pass

    # send a lowercase message to client and wait for uppercase reply
    def write_then_read(self):
        global UDPclientAddress
        while True:
            try:
                write_message = input()
                self.rdt_send(write_message)
                message = self.rdt_receive()
                modifiedMessage = message.upper()
                if message != modifiedMessage:
                    self.rdt_send(modifiedMessage)
                    print ('Connection from client(UDP):', UDPclientAddress, 'Received a message and return in uppercase:', modifiedMessage)
                    break
                else:
                    print ('Receive in Uppercase: ', message)
                    break

            except:
                pass


class TCP_connection:
    # create TCP socket for server
    def __init__(self, serverName = '127.0.0.1', port = 12000):
        global TCPconnectionSocket, TCPclientAddress
        TCPconnectionSocket, TCPclientAddress = TCPserverSocket.accept()
    
    # close the TCP connection
    def __close__(self):
        TCPconnectionSocket.close()

    # receive a message, if it is in lowercase, change it to uppercase and send back to client
    def read(self):
        global TCPconnectionSocket
        while True:
            try:
                receive_message = TCPconnectionSocket.recv(2048).decode()
                modifiedMessage = receive_message.upper()
                if receive_message != modifiedMessage:
                    TCPconnectionSocket.send(modifiedMessage.encode())
                    print ('Connection from client(TCP):', TCPclientAddress, 'Received a message and return in uppercase:', modifiedMessage)
                else:
                    print ('Receive in Uppercase: ', receive_message)
            except:
                pass
    
    # send message to client
    def write(self):
        global TCPconnectionSocket, TCPclientAddress
        while True:
            try:
                write_message = input()
                TCPconnectionSocket.send(write_message.encode())
            except:
                pass
    
    # use thread so that the program can keep sending message to client and receive message from client
    def run_server(self):
        threading.Thread(target=self.read).start()
        threading.Thread(target=self.write).start()


if __name__ == '__main__':
    print ('UDP/TCP server')
    inputs = [UDPserverSocket, TCPserverSocket]
    outputs = []

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        # s is a socket object
        for s in readable:
            # if there is a UDP connection
            # the client will first send a message to server, server will reply a uppercase message to client
            # then the server can send a lowercase message to client and wait for uppercase reply
            if s is UDPserverSocket:
                us = UDP_connection()
                us.read_then_write()
                us.write_then_read()

            # if there is a TCP connection
            # the server and client can interact with each other
            elif s is TCPserverSocket:
                ts = TCP_connection()
                ts.run_server()