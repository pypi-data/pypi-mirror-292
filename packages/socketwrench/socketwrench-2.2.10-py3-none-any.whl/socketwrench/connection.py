from socketwrench.standardlib_dependencies import (
    logging,
    socket,
)

from socketwrench.types import Request, Response, InternalServerError, BadRequest

logger = logging.getLogger("socketwrench")


class Connection:
    default_chunk_size: int = 1024
    timeout = 5

    def __init__(self,
                 handler,
                 connection_socket: socket.socket,
                 client_address: tuple,
                 cleanup_event,
                 chunk_size: int = default_chunk_size,
                 origin: str = ""):
        self.socket = connection_socket
        self.client_addr = client_address
        self.chunk_size = chunk_size
        self.cleanup_event = cleanup_event
        self.handler = handler
        self.origin = origin

        self._rep = None

    def handle(self):
        try:
            request = self.receive_request(self.socket)
            if request is None:
                return None, None, False
            if self.check_cleanup():
                return request, None, False
            logger.debug(str(request))
            response = self.handler(request)
            logger.log(9, f"\t\t{response}")
            if self.check_cleanup():
                return request, response, False
            self.send_response(self.socket, response)
            return request, response, True
        except BadRequest as b:
            logger.error(f"Error handling request: {b}")
            logger.exception(b)
            try:
                self.send_response(self.socket, b)
            except Exception as e2:
                logger.error(f"Error sending response: {e2}")
            self.close()
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.exception(e)
            try:
                self.send_response(self.socket, InternalServerError())
            except Exception as e2:
                logger.error(f"Error sending response: {e2}")
            self.close()
            # raise e

    def receive_request(self, connection_socket: socket.socket, chunk_size: int = None) -> Request:
        connection_socket.settimeout(self.timeout)
        if chunk_size is None:
            chunk_size = self.chunk_size

        new_line = b'\r\n'
        end_of_header = 2 * new_line

        request_data = b''
        while not self.cleanup_event or not self.cleanup_event.is_set():
            chunk = connection_socket.recv(chunk_size)
            request_data += chunk
            if end_of_header in request_data:
                break
            if not chunk:
                break

        if end_of_header not in request_data:
            raise BadRequest(b"Received empty chunk before end of header. Potential client issue or disconnection.")

        # Extract headers
        pre_body_bytes, body = request_data.split(end_of_header, 1)

        # Parsing Content-Length if present for requests with body
        lower = pre_body_bytes.lower()
        if b'content-length: ' in lower:
            length = int(lower.split(b'content-length: ')[1].split(new_line)[0])
            while len(body) < length and ((not self.cleanup_event) or (not self.cleanup_event.is_set())):
                body += connection_socket.recv(chunk_size)
        else:
            body = b''

        r = Request.from_components(pre_body_bytes, body, self.client_addr, self.socket, origin=self.origin)
        return r

    def send_response(self, connection_socket: socket.socket, response: Response):
        connection_socket.sendall(bytes(response))
        connection_socket.shutdown(socket.SHUT_WR) # seems to be needed for linux?
        connection_socket.close()

    def check_cleanup(self):
        if self.cleanup_event and self.cleanup_event.is_set():
            self.close()
            return True
        return False

    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_WR) # seems to be needed for linux?
        except Exception as e:
            logger.warning(f"Error shutting down socket: {e}")

        try:
            self.socket.close()
        except Exception as e:
            logger.warning(f"Error closing socket: {e}")

    def __repr__(self):
        if self._rep is None:
            r = ""
            if self.chunk_size != self.default_chunk_size:
                r += f", chunk_size={self.chunk_size}"

            self._rep = f'<{self.__class__.__name__}({self.socket}, {self.client_addr}, {self.cleanup_event}{r})>'
        return self._rep

