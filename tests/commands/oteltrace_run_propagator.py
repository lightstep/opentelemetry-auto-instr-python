from oteltrace.propagation.http import HTTPPropagator
from oteltrace.propagation.b3 import B3HTTPPropagator

if __name__ == '__main__':
    assert isinstance(HTTPPropagator(), B3HTTPPropagator)
    print('Test success')
