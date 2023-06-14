# Using python 3.8.5

from socket import *
import threading

# define the host is local host 127.0.0.1
serverName = '127.0.0.1'
UDPserverPort = 10000
TCPserverPort = 12000

# define a global variable for connection selection
global selection

class UDP_connection:
    # connect to UDP server
    def __init__(self, serverName = '127.0.0.1', Port = 12000):
        global UDPclientSocket
        self.expected_seq_num = 0
        UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
        UDPclientSocket.settimeout(1)
    
    # close the UDP connection
    def __close__(self):
        UDPclientSocket.close()

    # implement rdt 3.0 to receive message
    def rdt_receive(self):
        global UDPclientSocket
        while True:
            try:
                # Receive packet from server
                packet, UDPserverAddress = UDPclientSocket.recvfrom(2048)
                seq_num, receive_message = packet.decode().split('|')

                # If sequence number match expected sequence number, send ACK to client
                # return message for furthur action
                if int(seq_num) == self.expected_seq_num:
                    ack = str(self.expected_seq_num)
                    UDPclientSocket.sendto(ack.encode(), (serverName, UDPserverPort))
                    self.expected_seq_num = self.expected_seq_num + 1
                    return receive_message
                
                # If sequence number is less than expected sequence number, send ACK for last in-order packet
                elif int(seq_num) < self.expected_seq_num:
                    ack = str(self.expected_seq_num - 1)
                    UDPclientSocket.sendto(ack.encode(), (serverName, UDPserverPort))
            
            # If timeout, resend packet
            except UDPclientSocket.timeout:
                continue

    # implement rdt 3.0 to send message
    def rdt_send(self, data):
        global UDPclientSocket
        seq_num = self.expected_seq_num
        while True:
            # send message with sequence number to the client
            packet = str(seq_num) + '|' + data
            UDPclientSocket.sendto(packet.encode(), (serverName, UDPserverPort))

            try:
                # Wait for ACK with matching sequence number
                ack, UDPserverAddress = UDPclientSocket.recvfrom(2048)
                ack_seq_num = int(ack.decode())

                # If ACK matches expected sequence number, break loop and return to the main program
                if ack_seq_num == self.expected_seq_num:
                    self.expected_seq_num = self.expected_seq_num + 1
                    break

            # If timeout, resend packet
            except UDPclientSocket.timeout:
                continue

    # receive a message from server
    # if it is a lowercase message, change it to uppercase and send back to server
    # if it is a upperacse message, it is the reply from server
    def read_then_write(self):
        global UDPclientSocket
        while True:
            try:
                message = self.rdt_receive()
                modifiedMessage = message.upper()
                if message != modifiedMessage:
                    self.rdt_send(modifiedMessage)
                    print ('Connection from server(UDP):', serverName, 'Received a message and return in uppercase:', modifiedMessage)
                    break
                else:
                    print ('Receive in Uppercase: ', message)
                    break

            except:
                pass

    # send a lowercase message to server and wait for uppercase reply
    def write_then_read(self):
        global UDPclientSocket
        while True:
            try:
                write_message = input()
                self.rdt_send(write_message)
                message = self.rdt_receive()
                modifiedMessage = message.upper()
                if message != modifiedMessage:
                    self.rdt_send(modifiedMessage)
                    print ('Connection from client(UDP):', serverName, 'Received a message and return in uppercase:', modifiedMessage)
                    break
                else:
                    print ('Receive in Uppercase: ', message)
                    break
            except:
                pass


class TCP_connection:
    # create TCP socket for server
    def __init__(self, serverName = '127.0.0.1', port = 12000):
        global TCPclientSocket
        TCPclientSocket = socket(AF_INET, SOCK_STREAM)
        TCPclientSocket.connect((serverName, TCPserverPort))
    
    # close the TCP connection
    def __close__(self):
        TCPclientSocket.close()

    # send a message to server
    def read(self):
        global TCPclientSocket
        while True:
            try:
                receive_message = TCPclientSocket.recv(2048).decode()
                modifiedMessage = receive_message.upper()
                if receive_message != modifiedMessage:
                    TCPclientSocket.send(modifiedMessage.encode())
                    print ('Connection from server(TCP): (', serverName, ', ', TCPserverPort, ') .', 'Received a message and return in uppercase:', modifiedMessage)
                else:
                    print ('Receive in Uppercase: ', receive_message)
            except:
                pass
    
    # receive message from server
    def write(self):
        global TCPclientSocket, selection
        while True:
            try:
                write_message = input()
                TCPclientSocket.send(write_message.encode())
            except:
                pass
    
    # use thread so that the program can keep sending message to server and receive message from server
    def run(self):
        while True:
            threading.Thread(target=self.read).start()
            threading.Thread(target=self.write).start()


if __name__ == '__main__':
    selection = ''
    print ('UDP/TCP client')
    print ('Choose TCP connection or UDP connection (TCP / UDP):')
    selection = input()

    while selection !='TCP' and selection !='UDP' and selection != 'tcp' and selection != 'udp':
        print ('Please choose TCP or UDP connection')
        selection = input()

    # if the connection is UDP
    # the client will first send a message to server, server will reply a uppercase message to client
    # then the server can send a lowercase message to client and wait for uppercase reply
    if selection == 'UDP' or selection =='udp':
        uc = UDP_connection()
        uc.write_then_read()
        uc.read_then_write()

    # if the connection is TCP
    # the server and client can interact with each other
    if selection == 'TCP' or selection=='tcp':
        tc = TCP_connection()
        tc.run()
