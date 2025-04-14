import time
import threading


class PeerManager:
    def __init__(self, cleanup_interval=15):
        self.peers = {}  # {nickname: (ip, port, last_seen)}
        self.lock = threading.Lock()
        self.cleanup_interval = cleanup_interval
        self.cleanup_thread = None

    def add_peer(self, nickname, ip, port):
        """Add/update a peer"""
        with self.lock:
            self.peers[nickname] = (ip, port, time.time())

    def remove_peer(self, nickname):
        """Remove a peer"""
        with self.lock:
            if nickname in self.peers:
                del self.peers[nickname]

    def get_peers(self):
        """Get list of active peers"""
        with self.lock:
            return list(self.peers.keys())

    def get_peer_info(self, nickname):
        """Get detailed info for a specific peer"""
        with self.lock:
            return self.peers.get(nickname)

    def start_cleanup(self):
        """Start automatic peer cleanup"""
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()

    def _cleanup_loop(self):
        """Remove inactive peers periodically"""
        while True:
            current_time = time.time()
            with self.lock:
                to_remove = [nick for nick, (_, _, last) in self.peers.items()
                             if current_time - last > self.cleanup_interval]

                for nick in to_remove:
                    del self.peers[nick]

            time.sleep(5)