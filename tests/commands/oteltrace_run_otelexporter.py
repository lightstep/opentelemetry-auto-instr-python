from oteltrace import tracer

if __name__ == '__main__':
    assert tracer.writer.api._exporter.key == '0x9812892467541'
    assert tracer.writer.api._exporter.url == 'opentelemetry.io'
    print('Test success')
