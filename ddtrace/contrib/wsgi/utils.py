from ...ext import http


def parse_status_code(status_code):
    code, _, _ = status_code.partition(' ')
    try:
        code = int(code)
    except ValueError:
        pass

    return code


def wrap_start_response(start_response, span, before_response=None):
    def _start_response(status_code, headers):
        # Parse response status code
        code = parse_status_code(status_code)

        # Add response status code tag
        span.set_tag(http.STATUS_CODE, code)

        # Mark the request as an error if it is a 5xx error
        if 500 <= code < 600:
            span.error = 1

        if before_response:
            before_response(span, code, headers)

        return start_response(status_code, headers)
    return _start_response
