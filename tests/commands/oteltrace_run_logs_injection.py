import logging

if __name__ == '__main__':
    # Ensure if module is patched then default log formatter is set up for logs
    if getattr(logging, '_opentelemetry_patch'):
        assert '[otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s]' in \
            logging.root.handlers[0].formatter._fmt
    else:
        assert '[otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s]' not in \
            logging.root.handlers[0].formatter._fmt
    print('Test success')
