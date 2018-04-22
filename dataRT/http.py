from flask import (Flask, jsonify)
from gevent import (pywsgi, sleep)
from geventwebsocket.handler import WebSocketHandler

from . import __version__
from .logs import logger


class FlaskApp(object):
    def __init__(self, host='', port=8080):
        self.app = Flask(__name__)
        self._register_routes()
        self._socket_app = None
        self._host = host
        self._port = port
        self._server = pywsgi.WSGIServer((self._host, self._port), self.app, handler_class=WebSocketHandler)
        self._serving = False

    @property
    def socket_app(self):
        return self._socket_app

    @socket_app.setter
    def socket_app(self, socket_app):
        self._socket_app = socket_app

    @property
    def socket_clients(self):
        if self._socket_app is not None:
            return len(self._socket_app)
        else:
            return 0

    @property
    def is_serving(self):
        return self._serving

    def _register_routes(self):
        @self.app.route("/", methods=['GET'])
        def root():
            return "200 OK", 200

        # Tesseract requires at least a /status endpoint to verify that the app is running.
        @self.app.route("/status", methods=['GET'])
        def status():
            return jsonify({
                "status": "up",
                "version": __version__,
                "clients": self.socket_clients
            }), 200

    def serve_forever(self):
        logger.debug('Serving Forever!')
        try:
            print(str(self._port))
            print(str(self._host))
            self._server.serve_forever()
        except KeyboardInterrupt:
            print("Keyboard Interrupt, Exiting...")
            exit(0)

    def start(self):
        logger.debug('Starting Server...')
        self._serving = True
        self._server.start()

    def stop(self):
        logger.debug('Stopping Server...')
        self._server.stop()
        self._serving = False

    def run_in_loop(self, actions, *args, **kwargs):
        if not self._serving:
            self.start()
        while self._serving:
            actions(*args, **kwargs)
            sleep(0)
