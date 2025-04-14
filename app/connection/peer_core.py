from utils.network_discovery import NetworkDiscovery
from utils.tcp_server import TCPServer
from utils.peer_manager import PeerManager
from chat_session import ChatSession
import socket


class PeerCore:
    def __init__(self):
        self.nickname = None
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.tcp_port = 5555

        # Components
        self.discovery = NetworkDiscovery()
        self.tcp_server = TCPServer(self.tcp_port)
        self.peer_manager = PeerManager()

        # Setup callbacks
        self.discovery.on_peer_found = self._handle_peer_found
        self.tcp_server.on_connection = self._handle_new_connection

        # Event handlers for GUI
        self.on_peer_list_updated = None
        self.on_message_received = None
        self.on_connection_error = None

    def start(self, nickname):
        """Initialize all services"""
        self.nickname = nickname
        self.discovery.start(self.local_ip, nickname, self.tcp_port)
        self.tcp_server.start()
        self.peer_manager.start_cleanup()

    def stop(self):
        """Shutdown all services"""
        self.discovery.stop()
        self.tcp_server.stop()

    def _handle_peer_found(self, nickname, ip, port):
        """Callback from NetworkDiscovery"""
        self.peer_manager.add_peer(nickname, ip, port)
        if self.on_peer_list_updated:
            self.on_peer_list_updated()

    def _handle_new_connection(self, client_socket):
        """Callback from TCPServer for new connections"""
        session = ChatSession(client_socket, self.nickname)
        session.register_message_handler(
            lambda msg: self.on_message_received(session.nickname, msg)
        )
        session.start()

    def connect_to_peer(self, nickname):
        """Initiate connection to another peer"""
        peer_info = self.peer_manager.get_peer_info(nickname)
        if not peer_info:
            return None

        ip, port, _ = peer_info
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            session = ChatSession(sock, self.nickname)
            session.register_message_handler(
                lambda msg: self.on_message_received(nickname, msg)
            )
            session.start()
            return session
        except Exception as e:
            if self.on_connection_error:
                self.on_connection_error(str(e))
            return None