from multiprocessing import Semaphore
import socket
import logging
import threading

from .winner_service import WinnerService

PREPARE_MSG_SIZE = 12
RESPONSE_MSG_SIZE = 13
CLOSE_CONN_SIZE = 13

RESPONSE_MSG_CODE = "0000000000000"
SEND_RESPONSE_MSG_CODE = "0000000000001"
CLOSE_CONN_CODE = "9999999999999"

BUFF_SIZE = 4096

class Communicator:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._winner_service = WinnerService()
        self._client_socket_semaphore = Semaphore(1)
        self._client_sockets = list()

    def handle_communication(self):
        client_socket = self.__accept_new_connection()
        client_connection_thread = threading.Thread(target=self.__handle_client_connection, args=(client_socket,))
        client_connection_thread.setDaemon(True)
        client_connection_thread.start()

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
        except OSError as error:
            logging.info("Error while accept connection in server socket {}. Error: {}".format(self._server_socket, error))
            self._server_socket.close()

    def __handle_client_connection(self, client_socket: socket):
        """
        Read message from a specific client socket and respond to it.

        Closes the socket when client request the end of communication

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        if(client_socket is not None):
            logging.info("Handling client connection {}".format(client_socket))
            try:
                self.__init_connection(client_socket)
                request = self.__receive(client_socket, PREPARE_MSG_SIZE)
                self.__respond(client_socket, request, None)
            except ValueError as error:
                logging.info("Error while reading client message {}. Error: {}".format(client_socket, error))
                self.__end_connection(client_socket)
            except OSError as error:
                logging.info("Error while reading client socket {}. Error: {}".format(client_socket, error))
                self.__end_connection(client_socket)
            finally:
                self.__end_connection(client_socket)

    def __init_connection(self, client_socket: socket):
        if(client_socket is not None):
            logging.info('Init Connection: {}'.format(client_socket.getpeername()))
            self._client_socket_semaphore.acquire()
            self._client_sockets.append(client_socket)
            self._client_socket_semaphore.release()

    def __respond(self, client_socket: socket, request: bytes, response: bytes):
        request_msg: str = request.decode('utf-8')
        response_msg: str = None
        if (response is not None):
            response_msg = response.decode('utf-8')

        try:
            int(request_msg)
            req_is_number = True
        except ValueError:
            req_is_number = False
            
        if (req_is_number):
            request_size = int(request)
            if (request_msg == CLOSE_CONN_CODE):
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Its time to close connection'
                        .format(client_socket.getpeername(), request_size))
                self.__respond_and_continue(client_socket, request, response)

            elif (request_msg == RESPONSE_MSG_CODE):
                winners_size = len(response)
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Telling client response size.'
                        .format(client_socket.getpeername(), request_size))
                logging.debug(
                            'Send winners size to connection {}. Winners Size: {}'
                            .format(client_socket.getpeername(), winners_size))
                winners_size_req = str(winners_size).zfill(RESPONSE_MSG_SIZE).encode('utf-8')
                self.__respond_and_wait(client_socket, winners_size_req, response, RESPONSE_MSG_SIZE)

            elif (request_msg == SEND_RESPONSE_MSG_CODE):
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Im ok to response data.'
                        .format(client_socket.getpeername(), request_size))
                logging.debug(
                            'Send winners to connection {}. Winners: {}'
                            .format(client_socket.getpeername(), response_msg))
                self.__respond_and_wait(client_socket, request, response, CLOSE_CONN_SIZE)

            else:
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Im ok to receive data.'
                        .format(client_socket.getpeername(), request_size))
                self.__respond_and_wait(client_socket, request, response, request_size)
                
        else:
            if not request_msg:
                return
            recived_len = str(len(request))
            logging.info(
                        'Data received from connection {}.'
                        .format(client_socket.getpeername()))
            logging.debug(
                        'Data received from connection {}. Data: {}'
                        .format(client_socket.getpeername(), request_msg))
            logging.info(
                        'Send recv ok to client {}. Recived: {}'
                        .format(client_socket.getpeername(), recived_len))
            winners_msg = self._winner_service.get_winners_response(request_msg)
            winners = winners_msg.encode('utf-8')
            self.__respond_and_wait(client_socket, request, winners, RESPONSE_MSG_SIZE)
            
    def __respond_and_wait(self, client_socket: socket, request: bytes, response: bytes, expected_response_size: int):
        """
            Responde with a message and waits for other response.
            If request is SEND_RESPONSE_MSG_CODE send the response.
            Else send the request.
        """
        request_msg = request.decode('utf-8')
        msg = request
        if(request_msg == SEND_RESPONSE_MSG_CODE):
            msg = response
        logging.info('Respond to client {} with {} and wait.'
                    .format(client_socket.getpeername(), msg))
        self.__send(client_socket, msg)

        client_response = self.__receive(client_socket, expected_response_size)
        self.__respond(client_socket, client_response, response)

    def __respond_and_continue(self, client_socket: socket, request: bytes, response: bytes):
        """
            Responde with a message and continue.
            If request is SEND_RESPONSE_MSG_CODE send the response.
            Else send the request.
        """ 
        request_msg = request.decode('utf-8')
        msg = request
        if(request_msg == SEND_RESPONSE_MSG_CODE):
            msg = response
        logging.info('Respond to client {} with {} and continue.'
                    .format(client_socket.getpeername(), msg))
        self.__send(client_socket, msg)

    def __receive(self, client_socket: socket, buffsize: int):
        """
            Receive a message.
            Read client socket specific buffsize and returns the message of communication
            It wait for first data recieved and return when all data has been readed.
        """
        logging.info('Recieving by client {} data with size: {}'
                    .format(client_socket.getpeername(), buffsize))
        data = b''
        if(client_socket is not None):
            client_socket.setblocking(True)
            while len(data) < buffsize:
                try:
                    data += client_socket.recv(BUFF_SIZE)
                    client_socket.setblocking(False)
                except socket.error:
                    pass
            logging.info('Recived len data {}: {}'
                    .format(client_socket.getpeername(), len(data)))
            return data

    def __send(self, client_socket, msg: bytes):
        """
            Send a message.
            Write client socket specific the message of communication
        """
        logging.info('Sending len data: {}'.format(len(msg)))
        if(client_socket is not None):
            client_socket.setblocking(True)
            client_socket.sendall(msg)

    def __end_connection(self, client_socket):
        """
            Finish the connection with client.
            Release client socket resources and close it
        """
        if(client_socket is not None):
            logging.info('End connection: {}'.format(client_socket.getpeername()))
            self._client_socket_semaphore.acquire()
            self._client_sockets = list(filter(lambda c: c.getpeername()[0] != client_socket.getpeername()[0] and c.getpeername()[1] != client_socket.getpeername()[1], self._client_sockets))
            client_socket.close()
            self._client_socket_semaphore.release()

    def turn_off(self):
        """
            Turn off Communicator.
            Release client and server resources and close it
        """
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()