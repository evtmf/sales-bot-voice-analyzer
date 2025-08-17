from io import BytesIO
from app.main import app  # ← импортируем Flask‑приложение из пакета

def handler(event, context):
    """Yandex Cloud Functions HTTP → WSGI адаптер."""
    environ = {
        "REQUEST_METHOD": event.get("httpMethod", "POST"),
        "PATH_INFO":      event.get("path", "/"),
        "QUERY_STRING":   "",
        "SERVER_NAME":    "localhost",
        "SERVER_PORT":    "80",
        "wsgi.version":   (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input":     BytesIO(event.get("body", "").encode() if event.get("body") else b""),
        "wsgi.errors":    None,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once":    False,
        "CONTENT_LENGTH":   str(len(event.get("body", "") or "")),
        "CONTENT_TYPE":     event.get("headers", {}).get("content-type", ""),
    }

    status_headers_body = []

    def start_response(status, headers):
        status_headers_body.append((status, headers))

    body_iter = app.wsgi_app(environ, start_response)
    body      = b"".join(body_iter)
    status, headers = status_headers_body[0]

    return {
        "statusCode": int(status.split()[0]),
        "headers": dict(headers),
        "body": body.decode("utf-8"),
    }