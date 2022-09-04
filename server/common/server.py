import socket
import logging
import signal

from .communicator import Communicator

class Server:

    def __init__(self, port, listen_backlog):
        self.running = True
        # Initialize communicator
        self.communicator = Communicator(port, listen_backlog)
        # Set signals to catch
        signal.signal(signal.SIGINT, self.__exit_gracefully)
        signal.signal(signal.SIGTERM, self.__exit_gracefully)

    # graceful shutdown the server
    def __exit_gracefully(self, *args):
        logging.info("Proceed to shutdown server gracefully")
        self.running = False

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self.running:
            self.communicator.handle_communication()

        logging.info("Server stop running")
