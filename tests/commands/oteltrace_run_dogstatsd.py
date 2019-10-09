from __future__ import print_function

from oteltrace import tracer

if __name__ == '__main__':
    assert tracer._dogstatsd_client.host == '172.10.0.1'
    assert tracer._dogstatsd_client.port == 8120
    print('Test success')
