import socket


class ConnectivityService:

    @staticmethod
    def test(host: str, port: int, timeout: float = 2.0):

        try:
            with socket.create_connection(
                (host, port),
                timeout=timeout,
            ):
                return {
                    "reachable": True,
                    "host": host,
                    "port": port,
                }

        except (socket.timeout, ConnectionRefusedError, OSError):

            return {
                "reachable": False,
                "host": host,
                "port": port,
            }
