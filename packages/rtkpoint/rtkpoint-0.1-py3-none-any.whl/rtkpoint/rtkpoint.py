### 6. **Testing and Distribution:**

# - **Testing:** Before distribution, ensure your module works by installing it locally using `pip install .` in your project directory.
# - **Distribution:** You can distribute your package via [PyPI](https://pypi.org/) if you want others to use it.

### Example of Refactored Code (`client.py`):

import socket
import ssl
import base64
from pyrtcm import RTCMReader

class RTKPOINT:
    def __init__(self, key, mountpoint = ''):
        self.host = "rtkpoint.com"
        self.port = 2102
        self.mountpoint = mountpoint
        self.key = key
        # self.username = username
        # self.password = password
        self.sock = None

    def connect(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        raw_sock = socket.create_connection((self.host, self.port))
        self.sock = context.wrap_socket(raw_sock, server_hostname=self.host)

        # auth = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
        headers = (
            f'GET /{self.mountpoint} HTTP/1.1\r\n'
            f'Host: {self.host}\r\n'
            f'Ntrip-Version: Ntrip/2.0\r\n'
            f'User-Agent: NTRIP PythonClient/1.0\r\n'
            f'Authorization: Bearer {self.key}\r\n'
            f'\r\n'
        ).encode()

        self.sock.sendall(headers)

        response = self.sock.recv(1024).decode()

        if '200 OK' in response:
            print('Connected to NTRIP caster')
        elif '403 Forbidden' in response:
            raise PermissionError('Unauthorized access. Please check your credentials.')
        elif '404 Not Found' in response:
            raise FileNotFoundError('Mountpoint not found. Please check the mountpoint URL.')
        elif '400 Bad Request' in response:
            raise ValueError('Invalid request.')
        else:
            raise ConnectionError(f'Failed to connect to NTRIP caster. Server response: {response}')

    def receive_data(self):
        stream = self.sock.makefile('rb')
        rtcm_reader = RTCMReader(stream)

        while True:
            try:
                raw_data, parsed_data = next(rtcm_reader)
                yield raw_data, parsed_data  # Use yield instead of return
                    
            except StopIteration:
                print("End of data stream.")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                break