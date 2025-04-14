import socket
import threading


class TCPServer:
    def __init__(self, port=5555):
        self.port = port
        self.running = False
        self.on_connection = None  # Callback for new connections
        self.socket = None

    def start(self):
        """Start listening for connections"""
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)

        threading.Thread(target=self._accept_connections).start()

    def stop(self):
        """Stop listening and clean up"""
        self.running = False
        if self.socket:
            self.socket.close()

    def _accept_connections(self):
        """Accept incoming connection attempts"""
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                if self.on_connection:
                    self.on_connection(client_socket)
            except:
                pass