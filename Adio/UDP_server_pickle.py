import socket
import pickle
import threading

class UDP_Server_Pickle:
    def __init__(self, ip, port, buffer_size=4096):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.buffer_size = buffer_size
        self.force_values = []

    def receive_start(self):
        udp_thread = threading.Thread(target=self.receive)
        udp_thread.setDaemon(True)
        udp_thread.start()

    def receive(self):
        print("Server is waiting for data...")
        while True:
            try:
                # データ受信
                data, addr = self.sock.recvfrom(self.buffer_size)
                # print(f"Received raw data: {data} from {addr}")
                
                # ！！注意！！デシリアライズpickleの変換
                self.received_data = pickle.loads(data)
                # print(f"Deserialized data: {received_data}")
                
                # データの処理
                self.x = self.received_data["x"]
                self.force_values = [
                    self.received_data["y1"],
                    self.received_data["y2"],
                    self.received_data["y3"],
                    self.received_data["y4"],
                    self.received_data["y5"],
                    self.received_data["y6"],
                ]
                # print(f"x: {self.x}, force_values: {self.force_values}")
            except pickle.UnpicklingError:
                print("Failed to deserialize data. The received data might not be pickled.")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    server = UDP_Server_Pickle("127.0.0.1", 5000)
    server.receive()
