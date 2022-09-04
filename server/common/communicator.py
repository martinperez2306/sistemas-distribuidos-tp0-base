import socket
import logging

from .utils import Contestant
from .utils import is_winner, parse_contestant_message

PREPARE_MSG_SIZE = 4

class Communicator:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None

    def handle_communication(self):
        self._client_socket = self.__accept_new_connection()
        self.__handle_client_connection()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        try:
            c, addr = self._server_socket.accept()
            logging.info('Got connection from {}'.format(addr))
            return c
        except OSError:
            logging.info("Error while accept connection in server socket {}".format(self._server_socket))
            self._server_socket.close()

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            if(self._client_socket is not None):
                msg_size = self.__receive(PREPARE_MSG_SIZE)
                logging.info(
                    'Message Size received from connection {}. MsgSize: {}'
                    .format(self._client_socket.getpeername(), msg_size))
                self.__send(msg_size)

                msg = self.__receive(int(msg_size))
                logging.info(
                    'Message received from connection {}. Msg: {}'
                    .format(self._client_socket.getpeername(), msg))
                
                contestant = parse_contestant_message(msg)
                is_contstant_winner = is_winner(contestant)
                logging.info(
                    'Send is winner to connection {}. Is Winner: {}'
                    .format(self._client_socket.getpeername(), is_contstant_winner))
                self.__send(is_contstant_winner)
        except ValueError:
            logging.info("Error while reading client message {}".format(self._client_socket))
        except OSError:
            logging.info("Error while reading client socket {}".format(self._client_socket))
        finally:
            self.end_communication()

    def __receive(self, bufsize):
        """
            Receive a message.
            Read client socket specific buffsize and returns the message of communication
        """
        if(self._client_socket is not None):
            return self._client_socket.recv(bufsize).rstrip().decode('utf-8')

    def __send(self, msg):
        """
            Send a message.
            Write client socket specific the message of communication
        """
        if(self._client_socket is not None):
            self._client_socket.send("{}".format(msg).encode('utf-8'))

    def end_communication(self):
        """
            Finish the communication.
            Release socket resources and close it
        """
        if(self._client_socket is not None):
            self._client_socket.close()
        self._client_socket = None

    def turn_off(self):
        """
            Turn off Communicator.
        """
        self.end_communication()
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()