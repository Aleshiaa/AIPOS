import socket
from argparse import ArgumentParser
import os
from urllib.parse import urlparse


def create_request(method, path, headers, body=""):
    request_line = f"{method} {path} HTTP/1.1"
    headers["Host"] = headers.get("Host", "127.0.0.1")
    header_lines = "\r\n".join(f"{key}: {value}" for key, value in headers.items())
    return f"{request_line}\r\n{header_lines}\r\n\r\n{body}"


def send_request(host, port, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request.encode("utf-8"))
        response = s.recv(4096).decode("utf-8")
    return response


def read_template(template_file):
    with open(template_file, "r") as f:
        return f.read()


if __name__ == "__main__":
    parser = ArgumentParser(description="HTTP 1.1 Client")
    parser.add_argument("-m", "--method", required=True, help="HTTP method")
    parser.add_argument("-u", "--url", required=True, help="URL path")
    parser.add_argument("-H", "--headers", nargs="+", help="Headers as key:value")
    parser.add_argument("-b", "--body", help="Request body or path to file")
    parser.add_argument("-t", "--template", help="Template file for request")
    args = parser.parse_args()

    url = args.url
    parsed_url = urlparse(f'http://{url}')  # Добавляем http://, чтобы urlparse мог корректно разобрать строку
    host = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else 8080  # Если порт не указан, используем 8080
    path = parsed_url.path if parsed_url.path else "/"

    headers = {}
    if args.headers:
        headers = dict(h.split(":", 1) for h in args.headers)

    body = args.body
    if body and os.path.exists(body):
        with open(body, "r") as f:
            body = f.read()

    # Используем шаблон, если он указан
    if args.template:
        body = read_template(args.template)
        print(f"Using template from {args.template} for body.")  # Выводим в консоль, что используем шаблон

    request = create_request(args.method, path, headers, body or "")
    response = send_request(host, port, request)
    print(f"Response:\n{response}")
