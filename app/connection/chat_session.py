import threading

class ChatSession:
    def __init__(self, socket, nickname):
        self.socket = socket
        self.nickname = nickname
        self.running = True
        self.message_handler = None
        self.error_handler = None

    def register_message_handler(self, handler):
        self.message_handler = handler

    def register_error_handler(self, handler):
        self.error_handler = handler

    def send_message(self, text):
        """Called by GUI to send messages"""
        try:
            self.socket.send(text.encode())
        except Exception as e:
            if self.error_handler:
                self.error_handler(str(e))
            self.close()

    def start(self):
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while self.running:
            try:
                message = self.socket.recv(1024).decode()
                if message and self.message_handler:
                    self.message_handler(message)
                else:
                    self.close()
            except Exception as e:
                if self.error_handler:
                    self.error_handler(str(e))
                self.close()

    def close(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass