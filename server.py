import os
import socket
import logging
from argparse import ArgumentParser
import mimetypes

DEFAULT_HEADERS = {
    "Access-Control-Allow-Origin": "https://my-cool-site.com",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

HTTP_STATUS_MESSAGES = {
    200: "OK",
    204: "No Content",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def create_response(status_code, headers=None, body=b""):
    headers = headers or {}
    status_line = f"HTTP/1.1 {status_code} {HTTP_STATUS_MESSAGES.get(status_code, 'Unknown')}"
    header_lines = "\r\n".join([f"{key}: {value}" for key, value in headers.items()])
    return f"{status_line}\r\n{header_lines}\r\n\r\n".encode("utf-8") + body


def handle_request(request, base_dir, log):
    try:
        # Разбираем запрос
        lines = request.split("\r\n")
        method, path, _ = lines[0].split(" ")
        log.info(f"Received {method} request for {path}")

        # Обрабатываем OPTIONS-запрос
        if method == "OPTIONS":
            log.info(f"Received OPTIONS request for {path}")
            headers = {"Content-Length": "0"}
            headers.update(DEFAULT_HEADERS)
            return create_response(204, headers)

        # Обрабатываем GET-запрос
        if method == "GET":
            file_path = os.path.join(base_dir, path.strip("/"))
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, "index.html")

            if not os.path.exists(file_path):
                return create_response(404, DEFAULT_HEADERS, b"File not found")

            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"

            with open(file_path, "rb") as f:
                body = f.read()

            headers = {
                "Content-Type": mime_type,
                "Content-Length": str(len(body)),
            }
            headers.update(DEFAULT_HEADERS)
            return create_response(200, headers, body)

        # Обрабатываем POST-запрос
        if method == "POST":
            body_start = request.find("\r\n\r\n") + 4
            body = request[body_start:]
            # Логируем тело запроса
            log.info(f"POST body: {body}")

            # Пример обработки
            response_body = f"POST received with body: {body}".encode("utf-8")
            headers = {"Content-Type": "text/plain", "Content-Length": str(len(response_body))}
            headers.update(DEFAULT_HEADERS)
            return create_response(200, headers, response_body)

        # Метод не поддерживается
        return create_response(405, DEFAULT_HEADERS, b"Method Not Allowed")

    except Exception as e:
        log.error(f"Error handling request: {e}")
        return create_response(500, DEFAULT_HEADERS, b"Internal Server Error")


def start_server(host, port, base_dir, log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    log = logging.getLogger("HTTPServer")
    log.info(f"Starting server on {host}:{port}, serving {base_dir}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server running on http://{host}:{port}")
    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(4096).decode("utf-8", errors="ignore")
        if not request:
            log.warning(f"Empty request from {client_address}")
            client_socket.close()
            continue

        print(f"Received request from {client_address}: {request.splitlines()[0]}")  # Вывод в консоль
        response = handle_request(request, base_dir, log)
        client_socket.sendall(response)
        client_socket.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="HTTP 1.1 Server")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Server host")
    parser.add_argument("-P", "--port", type=int, default=8080, help="Server port")
    parser.add_argument("-d", "--dir", default="./static", help="Base directory for serving files")
    parser.add_argument("-l", "--log", default="server.log", help="Log file")
    args = parser.parse_args()
    start_server(args.host, args.port, args.dir, args.log)
