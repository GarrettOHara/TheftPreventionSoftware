import sys
import threading
import bluetooth # pip pybluez22
import pickle
import zlib

EOF = b'\xFF'

class BTServer:
    def __init__(self, uuid='e4399be5-b392-4490-a842-cc5abce72cb9'):
        self.lock = threading.Condition()
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)

        port = self.server_sock.getsockname()[1]

        bluetooth.advertise_service(self.server_sock, "AntiTheftServer", service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                    # protocols=[bluetooth.OBEX_UUID]
                                    )

        self.online = False
        self.client_sock = None
        self.client_info = None
        self.async_thread = None
        self.data_received_listeners = []
        self.connect_listeners = []
        self.disconnect_listeners = []

    def start(self):
        self.online = True
        self.async_thread = threading.Thread(target=self.__accpet_connections, args=())
        self.async_thread.start()

    def wait_for_connection(self):
        if self.client_sock is None:
            self.lock.acquire()
            # thread stops here until notified
            self.lock.wait()
            self.lock.release()

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        compressed_data = zlib.compress(serialized_data)
        self.sock.send(compressed_data)
        self.client_sock.send(EOF)
        
    def __accpet_connections(self):
        while self.online:
            try:
                self.client_sock, self.client_info = self.server_sock.accept()
            except OSError:
                self.shutdown()
                break;

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

            # client disconnected
            for func in self.disconnect_listeners:
                func()

    def __recv_data(self):
        try:
            sum_data = b""
            while self.online:
                data = self.client_sock.recv(1024)
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
            self.disconnect_client()

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

    def shutdown(self):
        self.online = False
        try:
            self.disconnect_client()
            self.server_sock.close()
        except OSError:
            pass

    def disconnect_client(self):
        try:
            if self.client_sock is not None:
                self.client_sock.close()
                self.client_sock = None
        except OSError:
            pass

    def is_connected(self):
        return self.client_sock is not None

    def is_online(self):
        return self.online


######################
#### EXAMPLE CODE ####
######################

if __name__ == '__main__':

    server = BTServer()
    server.add_data_recv_listener(lambda data: print(data))
    server.add_connect_listener(lambda: print("Client connected."))
    server.add_disconnect_listener(lambda: print("Client disconnected."))
    server.start()
    print("BT server waiting for client")
    #server.wait_for_connection()

    while True:
        data = input()
        if data == "exit()":
            break
        elif data == "close()":
            server.shutdown()
            break

        if server.is_connected():
            server.send_data(data)
        else:
            print("No client connected.")