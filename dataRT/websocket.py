from flask import (Blueprint, request)
from flask_sockets import Sockets

from .clients import Clients
from .logs import logger


class FlaskWebSocket(object):
    def __init__(self, flask_app, on_message=None, on_connect=None, on_disconnect=None, url_prefix=r'/ws'):
        self._sockets = Sockets(flask_app)
        self._ws_bp = Blueprint(url_prefix, __name__)
        self._url_prefix = url_prefix
        self._clients = Clients()
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self._register_routes()

    def _do_on_message(self, client, message):
        # Perform any custom message actions
        if self.on_message is not None:
            self.on_message(client, message)
        else:
            logger.info('Got message')

    def _do_on_connect(self, client):
        # Register client and perform any custom connection actions
        self._clients.add(client)
        if self.on_connect is not None:
            self.on_connect(client)

    def _do_on_disconnect(self, client):
        # Unregister client and perform any custom message actions
        self._clients.remove(client)
        if self.on_disconnect is not None:
            self.on_disconnect(client)

    def _register_routes(self):
        # This is here to test that the websocket is working properly while troubleshooting.
        @self._ws_bp.route('/echo')
        def echo(socket):
            logger.debug('Client Connected! {}'.format(request.remote_addr))
            while not socket.closed:
                message = socket.receive()
                logger.debug('Got Message: {}'.format(message))
                socket.send('got: {}'.format(message))

        @self._ws_bp.route('/client')
        def client(socket):
            logger.debug('Client Connected! {}'.format(request.remote_addr))
            self._do_on_connect(socket)
            while not socket.closed:
                message = socket.receive()
                logger.debug('Got Message: {}'.format(message))
                if message is not None:
                    self._do_on_message(socket, message)
            self._do_on_disconnect(socket)

        self._sockets.register_blueprint(self._ws_bp, url_prefix=self._url_prefix)

    def send_all(self, message):
        assert isinstance(message, str)
        self._clients.send_all(message)

    def __len__(self):
        return len(self._clients)
