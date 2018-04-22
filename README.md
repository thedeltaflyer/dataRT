# dataRT Python Library

## About

### What does dataRT do?
dataRT is a drop-in replacement for the InfluxDBClient which writes data to InfluxDB while simultaneously echoing the points to a WebSocket. This allows you to view the data in real-time in a web browser or other client.

### What scenario would I need this for?
dataRT is designed to be used where the InfluxDBClient is already being used but constantly querying InfluxDB does not provide adequate real-time access to your data. By creating a client webpage you can display the data __in real time__ while simultaneously recording the points in InfluxDB for examination at a later date.

### What if I don't want to use InfluxDB?
No problem!
InfluxDB is __not__ a requirement to use dataRT. If the `influx_url` argument is set to `None`, dataRT will echo the data to a WebSocket, but not attempt to send data to an InfluxDB instance.

## Installation

### PyPi
```bash
> pip install dataRT
```

### Setuptools
```bash
> python setup.py install
```

## Usage
### Single-Thread Application
If you are constrained for resources, you can use the `CoreClient` object.

It is highly recommended that you [monkey-patch](http://www.gevent.org/intro.html#beyond-sockets) using gevent when using this technique.

To start, import the `CoreClient`:
```python
from dataRT import CoreClient
```

Then create a client:
```python
client = CoreClient(influx_url=None, debug=True)
```

The `CoreClient` takes these arguments, all are optional:

| Keyword | Default | Description |
| ------- | ------- | ----------- |
| `host` | `'0.0.0.0'` | Bind host for the WebSocket |
| `port` | `8080` | Bind port for the WebSocket |
| `influx_url` | `'localhost'` | URL for InfluxDB. Note: if this is set to `None` no attempt to connect to an InfluxDB instance will be made |
| `influx_port` | `8086` | Port for InfluxDB |
| `influx_user` | `None` | Username for InfluxDB |
| `influx_pass` | `None` | Password for InfluxDB |
| `influx_db` | `'example'` | Database for InfluxDB |
| `websocket_path` | `r'/ws'` | Base path for accessing WebSocket resources |
| `debug` | `False` | Show debug messages |

Define a "action" function then start the dataRT loop. This function will be constantly called as the dataRT runs through its maintenance loop:
```python
def action(possible_arg, possible_kwarg=100):
    print(possible_arg)
    print(possible_kwarg)

client.run_in_loop(action, 'possible_arg', possible_kwarg=1000)
```

Once `run_in_loop` is called, the client blocks until `client.stop()` is called or the program exits.

Available client functions:

| Method | Arguments | Description |
| ------ | --------- | ----------- |
| `write_points` | `points`, `*args`, `**kwargs` | Writes points to the WebSocket and InfluxDB instance. `points` are used for the WebSocket, all other args are passed to the InfluxDBClient |
| `query` | `*args`, `**kwargs` | Passes a query to the InfluxDBClient |
| `create_database` | `*args`, `**kwargs` | Passes a `create_database` to the InfluxDBClient |
| `serve_forever` | `None` | Blocks and serves the WebSocket forever |
| `start` | `None` | Starts the WebSocket server |
| `stop` | `None` | Stops the WebSocket server |
| `run_in_loop` | `actions`, `*args`, `**kwargs` | Blocks and serves the WebSocket forever, but calls the `actions` function every loop with the provided `*args` and `**kwargs` |

Available client properties:

| Property | Can be set? | Type | Description |
| -------- | ----------- | ---- | ----------- |
| `is_serving` | No | `bool` | Returns `True` if the WebSocket is currently being served |
| `influx_client` | No | `InfluxDBClient` | Returns the InfluxDBClient object to be used with more complex InfluxDB operations |
| `ws_on_message` | Yes | function | Function to call when the WebSocket receives a new message. Should accept 2 args for the WebSocket client and the message (string) |
| `ws_on_connect` | Yes | function | Function to call when the WebSocket connects. Should accept 1 arg for the WebSocket client |
| `ws_on_disconnect` | Yes | function | Function to call when the WebSocket disconnects. Should accept 1 arg for the WebSocket client |

### Multi-Process Application
If you need more reliability or want to avoid your code possibly blocking dataRT background tasks, use the `Client` object.

To start, import the `Client`:
```python
from dataRT import Client
```

Then create a client:
```python
client = Client(influx_url=None, debug=True)
```

The `Client` takes these arguments, all are optional:

| Keyword | Default | Description |
| ------- | ------- | ----------- |
| `host` | `'0.0.0.0'` | Bind host for the WebSocket |
| `port` | `8080` | Bind port for the WebSocket |
| `influx_url` | `'localhost'` | URL for InfluxDB. Note: if this is set to `None` no attempt to connect to an InfluxDB instance will be made |
| `influx_port` | `8086` | Port for InfluxDB |
| `influx_user` | `None` | Username for InfluxDB |
| `influx_pass` | `None` | Password for InfluxDB |
| `influx_db` | `'example'` | Database for InfluxDB |
| `websocket_path` | `r'/ws'` | Base path for accessing WebSocket resources |
| `debug` | `False` | Show debug messages |

Once the client is defined, you can start it:
```python
client.start()
```

Once `start` is called, the client will start in another process and continue serving until `client.stop()` is called or the program exits.

Available client functions:

| Method | Arguments | Description |
| ------ | --------- | ----------- |
| `write_points` | `points` | Writes points to the WebSocket and InfluxDB instance |
| `start` | `None` | Starts the WebSocket server |
| `stop` | `None` | Stops the WebSocket server |

### Where is my WebSocket?
The WebSocket associates itself with the `client` route on the WebSocket path: `ws:\\<host>:<port>\<ws route>\client`.

For the default settings, this would be `ws:\\0.0.0.0:8080\ws\client`

## Examples
Examples can be found in the [examples](examples) directory.

### Library Usage

* [gevent_example.py](examples/gevent_example.py) shows how to integrate the dataRT client in a single-threaded application using gevent. (Note: using this method you must be careful not to block the process from running maintenance for the WebSocket connection otherwise you may encounter issues)
* [multiprocess_example.py](examples/multiprocess_example.py) shows how to use the dataRT client as a drop-in-place replacement for the InfluxDBClient by leveraging a separate process (Note: This does consume more system resources, use the gevent method if you are working in a resource-constrained environment)

### HTML/JS

* [view_data.html](examples/view_data.html) uses basic jQuery to write each piece of data that is received onto the page in a table.
* [plot_data.html](examples/plot_data.html) uses the [Chart.js](http://www.chartjs.org) library to plot each point onto a line graph in real time.

## Licensing
This project is licensed under the MIT license.
No warranty is provided, use at your own risk.
