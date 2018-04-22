import json
import queue

from influxdb import InfluxDBClient
from logging import (DEBUG, WARNING)
from multiprocessing import (Process, Queue)

from .logs import logger
from .http import FlaskApp
from .websocket import FlaskWebSocket


class Client(object):
    def __init__(self,
                 host='0.0.0.0',
                 port=8080,
                 influx_url='localhost',
                 influx_port=8086,
                 influx_user=None,
                 influx_pass=None,
                 influx_db='example',
                 websocket_path=r'/ws',
                 debug=False):
        # self._message_queue = SimpleQueue()
        self._message_queue = Queue()
        self._settings = dict()
        self._settings['host'] = host
        self._settings['port'] = port
        self._settings['influx_url'] = influx_url
        self._settings['influx_port'] = influx_port
        self._settings['influx_user'] = influx_user
        self._settings['influx_pass'] = influx_pass
        self._settings['influx_db'] = influx_db
        self._settings['websocket_path'] = websocket_path
        self._settings['debug'] = debug
        self._client = self._spawn()

    @staticmethod
    def _spawn_process(settings, message_queue):
        client = CoreClient(settings['host'],
                            settings['port'],
                            settings['influx_url'],
                            settings['influx_port'],
                            settings['influx_user'],
                            settings['influx_pass'],
                            settings['influx_db'],
                            settings['websocket_path'],
                            settings['debug'],
                            message_queue)
        client.run_async()

    def _spawn(self):
        return Process(
            target=self._spawn_process,
            kwargs={'settings': self._settings, 'message_queue': self._message_queue}
        )

    def start(self):
        self._client.start()

    def stop(self):
        self._message_queue.put({'task': 'stop', 'data': None})
        self._client.join()

    def write_points(self, points):
        self._message_queue.put({'task': 'write_points', 'data': points})


class CoreClient(object):
    def __init__(self,
                 host='0.0.0.0',
                 port=8080,
                 influx_url='localhost',
                 influx_port=8086,
                 influx_user=None,
                 influx_pass=None,
                 influx_db='example',
                 websocket_path=r'/ws',
                 debug=False,
                 message_queue=None):
        if debug:
            logger.setLevel(DEBUG)
        else:
            logger.setLevel(WARNING)
        self._message_queue = message_queue
        self._http = FlaskApp(host, port)
        self._web_socket = FlaskWebSocket(self._http.app, url_prefix=websocket_path)
        self._http.socket_app = self._web_socket
        if influx_url is None:
            self._influx = None
        else:
            self._influx = InfluxDBClient(influx_url, influx_port, influx_user, influx_pass, influx_db)

    def write_points(self, points, *args, **kwargs):
        try:
            assert isinstance(points, list)
        except AssertionError:
            raise TypeError('write_points only accepts lists!')
        for point in points:
            try:
                assert isinstance(point, dict)
            except AssertionError:
                raise TypeError('write_points was expected a list of dicts, received "{}" instead'.format(type(point)))
            self._web_socket.send_all(json.dumps(point))
        if self._influx is not None:
            self.influx_client.write_points(points, *args, **kwargs)

    def query(self, *args, **kwargs):
        if self._influx is not None:
            return self._influx.query(*args, **kwargs)
        else:
            return None

    def create_database(self, *args, **kwargs):
        if self._influx is not None:
            return self._influx.create_database(*args, **kwargs)
        else:
            return None

    @property
    def ws_on_connect(self):
        return self._web_socket.on_connect

    @ws_on_connect.setter
    def ws_on_connect(self, on_connect):
        self._web_socket.on_connect = on_connect

    @property
    def ws_on_disconnect(self):
        return self._web_socket.on_disconnect

    @ws_on_disconnect.setter
    def ws_on_disconnect(self, on_disconnect):
        self._web_socket.on_disconnect = on_disconnect

    @property
    def ws_on_message(self):
        return self._web_socket.on_message

    @ws_on_message.setter
    def ws_on_message(self, on_message):
        self._web_socket.on_connect = on_message

    @property
    def influx_client(self):
        return self._influx

    @property
    def is_serving(self):
        return self._http.is_serving

    def serve_forever(self):
        self._http.serve_forever()

    def start(self):
        self._http.start()

    def stop(self):
        self._http.stop()

    def run_in_loop(self, actions, *args, **kwargs):
        self._http.run_in_loop(actions, *args, **kwargs)

    def run_async(self):
        try:
            assert self._message_queue is not None
        except AssertionError:
            raise RuntimeError('run_async should only be run via the "Client" object!')

        def actions(message_queue, write_points, stop):
            # # If gevent is causing problems, maybe switch to a SimpleQueue?
            # if message_queue.empty():
            #     return
            # else:
            #     xtodo = message_queue.get()
            try:
                todo = message_queue.get(True, 1)
            except queue.Empty:
                return
            if isinstance(todo, dict):
                task = todo.get('task', '')
                data = todo.get('data', None)
                if task == 'stop':
                    stop()
                elif task == 'write_points':
                    write_points(data)

        self._http.run_in_loop(actions,
                               message_queue=self._message_queue,
                               write_points=self.write_points,
                               stop=self.stop)
