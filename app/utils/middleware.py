class FixWSGIMiddleware:
    """wsgi.url_scheme нужен на Cloud Functions, иначе Flask падает."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ.setdefault("wsgi.url_scheme", "http")
        return self.app(environ, start_response)