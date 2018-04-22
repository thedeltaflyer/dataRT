#!/user/bin/env python3
"""dataRT gEvent Example
This example uses the CoreClient object in a single process to write 10 pieces of data to the WebSocket
It will do this every 10 seconds, then exit after 100 seconds.
"""
from gevent import monkey  # For best performance, it is recommended that you monkey-patch!
monkey.patch_all()  # This will make all non-IO bound tasks non-blocking.

from random import SystemRandom

# Use the gevent sleep to allow yielding to other IO actions, especially if you are not monkey patching
from gevent import sleep

from dataRT import CoreClient as Client


def random_data(random=None):
    random = random or SystemRandom()
    test_data = [{
        'measurement': 'test',
        'fields': {
            'value': random.randint(0, 1000)
        },
        'tags': {
            'tester': 'basic_example'
        }
    }]
    return test_data


def main():
    random = SystemRandom()

    # Set up the client, set influx_url to None if there is no InfluxDB instance
    client = Client(influx_url=None, debug=True)
    count = {'counter': 1}  # By using a dict, we can continue to mutate the same counter

    # Start the WebSocket client
    # client.serve_forever()
    def actions(counter):
        # Wait a bit before sending the data
        sleep(10)

        # Send the data in the InfluxDB client style
        print('writing!')
        client.write_points(random_data(random))
        # Note that you have direct access to the InfluxDBClient object from the CoreClient
        # Also shortcuts such as "query" and "create_database" are forwarded.

        if counter['counter'] < 10:  # Have it repeat 10 times before exiting
            counter['counter'] += 1
        else:
            # Close the WebSocket server down.
            print('stopping!')
            client.stop()
            # We could alternatively use client.serve_forever() to listen for WebSocket events forever!

    print('starting!')
    client.run_in_loop(actions, counter=count)


if __name__ == '__main__':
    main()
