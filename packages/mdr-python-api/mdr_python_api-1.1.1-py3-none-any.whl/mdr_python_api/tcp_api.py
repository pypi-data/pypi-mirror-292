from typing import Tuple
import json

HOST = "localhost"  # Standard loopback interface address (localhost)
PORT = 9393  # Port to listen on (non-privileged ports are > 1023)
NUM_PROTOCOL_START_BYTES = 4


class ApiImpl:

    def init(new_host, new_port = 9393):
        global HOST
        global PORT
        HOST = new_host
        PORT = new_port

    def is_json(myjson):
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True

    def send_data(raw_data):
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            b = bytearray()
            b.extend(map(ord, raw_data))
            n = len(raw_data)
            nb = (n).to_bytes(NUM_PROTOCOL_START_BYTES, byteorder="big")
            s.send(nb)
            s.sendall(b)

    def read_string():
        result_string = ""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while 1:
                data = s.recv(100)
                if not data:
                    break
                result_string += data.decode("utf-8")
            s.close()
            print(f"read string {ApiImpl.read_string}")
        return result_string

    def add_dependencies(
        label: str, version: str, dependencies: list[Tuple[str, str]], input_dep: bool
    ):
        deps = ""
        for name, version in dependencies:
            deps += f"{name}:{version}"
        command = "INPUT" if input_dep else "OUTPUT"
        raw_data = f"{command}:{label}:{version}:{deps}"
        ApiImpl.send_data(raw_data)

    def register_meta_data(
        label: str, version: str, owner: str, url: str, md: str
    ) -> str:
        import socket

        raw_data = f"UPDATE:{label}:{version}:{owner}:{url}:{md}"
        result_string = ""


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            b = bytearray()
            b.extend(map(ord, raw_data))
            n = len(raw_data)
            nb = (n).to_bytes(NUM_PROTOCOL_START_BYTES, byteorder="big")
            s.send(nb)
            s.sendall(b)
            while 1:
                data = s.recv(100)
                if not data:
                    break
                result_string += data.decode("utf-8")
            s.close()
        print(f"obj id {ApiImpl.read_string}")
        return result_string

    def search_MD(search_string, dependencies):
        import socket

        raw_send_req_data = f"SEARCH:label:{search_string}::"
        if dependencies:
            raw_send_req_data = f"DEPENDENCY:label:{search_string}::"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            b = bytearray()
            b.extend(map(ord, raw_send_req_data))
            n = len(raw_send_req_data)
            nb = (n).to_bytes(NUM_PROTOCOL_START_BYTES, byteorder="big")
            s.send(nb)

            s.sendall(b)
            result_string = ""
            while 1:
                data = s.recv(1024)
                if not data:
                    break
                result_string += data.decode("utf-8")
            s.close()
        delimiter = chr(0xFF)
        results = result_string.split(delimiter)
        print(f"search size {len(results)}")
        return results

    def search_meta_data(search_string: str):
        return ApiImpl.search_MD(search_string, False)

    def search_dependencies(search_string: str):
        return ApiImpl.search_MD(search_string, True)

    def transfer_data(
        source_label, source_version, source_path, dest_label, dest_version, dest_path
    ):

        raw_data = (
            f"TRANSFER:{source_label}:{source_version}:{source_path}:"
            f"{dest_label}:{dest_version}:{dest_path}"
        )
        ApiImpl.send_data(raw_data)
