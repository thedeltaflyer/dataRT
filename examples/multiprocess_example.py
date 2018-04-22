#!/user/bin/env python3
"""dataRT gEvent Example
This example uses the CoreClient object in a separate process to write 10 pieces of data to the WebSocket
It will do this every 10 seconds, then exit after 100 seconds.
"""
from random import SystemRandom
from time import sleep

from dataRT import Client


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

    # Start the WebSocket client
    print('starting!')
    client.start()

    for i in range(10):  # Send 10 messages then exit
        # Wait a bit before sending the data
        sleep(10)

        # Send the data in the InfluxDB client style
        print('writing!')
        client.write_points(random_data(random))
        # Note that the Client object does not have direct access to the InfluxDBClient
        # "write_points" is the only available InfluxDBClient function
        # To perform other InfluxDB actions you will need to import and use the InfluxDBClient library

    # Close the WebSocket server down.
    print('stopping!')
    client.stop()


if __name__ == '__main__':
    main()
