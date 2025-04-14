import socket
import threading
import time
import json


class NetworkDiscovery:
    def __init__(self, broadcast_ip='255.255.255.255', udp_port=37020):
        self.broadcast_ip = broadcast_ip
        self.udp_port = udp_port
        self.running = False
        self.on_peer_found = None
        self.on_peer_removed = None

        # Configure UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self, local_ip, nickname, tcp_port):
        """Begin discovery service"""
        self.running = True
        threading.Thread(target=self._send_presence,
                         args=(local_ip, nickname, tcp_port)).start()
        threading.Thread(target=self._listen_presence).start()

    def stop(self):
        """Stop discovery service"""
        self.running = False
        self.socket.close()

    def _send_presence(self, ip, nickname, port):
        """Broadcast our presence periodically"""
        message = json.dumps({
            'type': 'presence',
            'nickname': nickname,
            'ip': ip,
            'port': port
        })

        while self.running:
            try:
                self.socket.sendto(message.encode(),
                                   (self.broadcast_ip, self.udp_port))
                time.sleep(5)
            except:
                break

    def _listen_presence(self):
        """Listen for peer broadcasts"""
        self.socket.bind(('', self.udp_port))

        while self.running:
            try:
                data, _ = self.socket.recvfrom(1024)
                message = json.loads(data.decode())

                if message['type'] == 'presence' and self.on_peer_found:
                    self.on_peer_found(
                        message['nickname'],
                        message['ip'],
                        message['port']
                    )
            except:
                if self.running:  # Expected closure during stop
                    pass