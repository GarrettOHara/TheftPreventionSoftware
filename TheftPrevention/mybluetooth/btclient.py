import sys
import pickle
import threading
import bluetooth # pip pybluez22
import zlib

EOF = b'\xFF'

class BTClient:
    def __init__(self, uuid='e4399be5-b392-4490-a842-cc5abce72cb9'):
        self.lock = threading.Condition()
        self.uuid = uuid
        # Create the client socket

        self.retry_connection = False
        self.connected = False
        self.async_thread = None
        self.data_received_listeners = []
        self.connect_listeners = []
        self.disconnect_listeners = []
        self.retry_listeners = []

    def start(self):
        self.async_thread = threading.Thread(target=self.__accpet_connections, args=())
        self.async_thread.start()

    def wait_for_connection(self):
        if not self.connected:
            self.lock.acquire()
            # thread stops here until notified
            self.lock.wait()
            self.lock.release()

            if not self.connected:
                raise RuntimeError("Couldn't establish Bluetooth connection.")

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        compressed_data = zlib.compress(serialized_data)
        self.sock.send(compressed_data)
        self.sock.send(EOF)
        
    def __accpet_connections(self):
        while True:
            service_matches = bluetooth.find_service(uuid=self.uuid)
            #print(service_matches)
            if len(service_matches) == 0:
                if self.retry_connection:
                    for func in self.retry_listeners:
                        func()
                    continue
                else:
                    # notify threads waiting for connection
                    self.lock.acquire()
                    try:
                        self.lock.notify()
                    finally:
                        self.lock.release()

                    break

            first_match = service_matches[0]
            self.port = first_match["port"]
            self.name = first_match["name"]
            self.host = first_match["host"]

            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            # client connected
            for func in self.connect_listeners:
                func()

            # notify threads waiting for connection
            self.lock.acquire()
            try:
                self.lock.notify()
            finally:
                self.lock.release()

            # start receiving data
            self.__recv_data()
            self.connected = False

            # client disconnected
            for func in self.disconnect_listeners:
                func()

            if not self.retry_connection:
                break

    def __recv_data(self):
        try:
            sum_data = b""
            while True:
                data = self.sock.recv(1024)

                if data == b'':
                    break
                elif data == EOF:
                    decompressed_data = zlib.decompress(sum_data)
                    deserialized_data = pickle.loads(decompressed_data)
                    sum_data = b""
                    for func in self.data_received_listeners:
                        func(deserialized_data)
                else:
                    sum_data += data
        except OSError:
            pass
        finally:
            self.disconnect()

    def add_data_recv_listener(self, func):
        self.data_received_listeners.append(func)

    def remove_data_recv_listener(self, func):
        self.data_received_listeners.remove(func)

    def add_connect_listener(self, func):
        self.connect_listeners.append(func)

    def remove_connect_listener(self, func):
        self.connect_listeners.remove(func)

    def add_disconnect_listener(self, func):
        self.disconnect_listeners.append(func)

    def remove_disconnect_listener(self, func):
        self.disconnect_listeners.remove(func)

    def add_retry_listener(self, func):
        self.retry_listeners.append(func)

    def remove_rety_listener(self, func):
        self.retry_listeners.remove(func)

    def shutdown(self):
        self.retry_connection = False
        try:
            self.disconnect()
            self.sock.close()
        except OSError:
            pass

    def disconnect(self):
        try:
            self.sock.close()
        except OSError:
            pass
        self.connected = False

    def is_connected(self):
        return self.connected

    def will_rety_connection(self):
        return self.retry_connection

    def set_rety_connection(self, b):
        self.retry_connection = b


######################
#### EXAMPLE CODE ####
######################

if __name__ == '__main__':

    client = BTClient()
    client.set_rety_connection(True)
    client.add_retry_listener(lambda: print("Failed to connect. retrying..."))
    client.add_data_recv_listener(lambda data: print(data))
    client.add_connect_listener(lambda: print("connected."))
    client.add_disconnect_listener(lambda: print("disconnected."))
    client.start()
    print("BT client attempting connection...")
    client.wait_for_connection()

    while True:
        data = input()
        if data == "exit()":
            client.shutdown()
            break
        elif data == "disconnect()":
            client.disconnect()

        if client.is_connected():
            client.send_data(data)
        else:
            print("BT connection.")