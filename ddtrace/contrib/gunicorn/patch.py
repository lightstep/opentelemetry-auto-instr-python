import functools

import gunicorn
from wrapt import wrap_function_wrapper as _w
from wrapt import ObjectProxy

from ...ext import AppTypes
from ...ext import http
from ...pin import Pin
from ...utils.importlib import func_name
from ...utils.wrappers import unwrap as _u


def _get_root_span(pin):
    ctx = pin.tracer.get_call_context()
    if not ctx:
        return None

    span = ctx.get_current_root_span()
    if not span:
        return None

    return span


def _parse_req_resource(pin, req):
    if not pin or not pin.enabled():
        return

    if not req:
        return

    span = _get_root_span(pin)
    if not span:
        return

    resource = ''
    if hasattr(req, 'path'):
        span.set_tag(http.URL, req.path)
        resource = req.path

    if hasattr(req, 'method'):
        span.set_tag(http.METHOD, req.method)
        if resource:
            resource = '{} {}'.format(req.method, resource)
        else:
            resource = req.method
    span.resource = resource


def patch():
    if getattr(gunicorn, '_datadog_patch', False):
        return
    setattr(gunicorn, '_datadog_patch', True)

    # Application
    _w('gunicorn.app.base', 'BaseApplication.__init__', _w_app_init)
    _w('gunicorn.app.base', 'BaseApplication.wsgi', _w_app_wsgi)

    # HTTP
    _w('gunicorn.http.parser', 'Parser.__init__', _w_parser_init)
    _w('gunicorn.http.parser', 'Parser.__next__', _w_parser_next)

    # Utils
    _w('gunicorn.util', 'write_error', _w_util_write_error)

    # Workers
    _w('gunicorn.workers.base', 'Worker.handle_error', _w_worker_handle_error)
    _w('gunicorn.workers.base_async', 'AsyncWorker.handle_request', _w_worker_handle_request)
    _w('gunicorn.workers.gthread', 'ThreadWorker.handle_request', _w_worker_handle_request)
    _w('gunicorn.workers.sync', 'SyncWorker.handle', _w_worker_handle)
    _w('gunicorn.workers.sync', 'SyncWorker.handle_request', _w_worker_handle_request)

    # geventlet inherits from gunicorn.workers.base_async.AsyncWorker
    # ggevent inherits from gunicorn.workers.base_async.AsyncWorker
    # gtornado is not traced at this time
    # gaiohttp is not traced at this time


def unpatch():
    if not getattr(gunicorn, '_datadog_patch', False):
        return
    setattr(gunicorn, '_datadog_patch', False)

    # Application
    _u('gunicorn.app.base', 'BaseApplication.__init__')
    _u('gunicorn.app.base', 'BaseApplication.wsgi')

    # Config
    _u('gunicorn.config', 'Config.__init__')

    # HTTP
    _u('gunicorn.http.parser', 'Parser.__init__')
    _u('gunicorn.http.parser', 'Parser.__next__')

    # Utils
    _u('gunicorn.util', 'write_error')

    # Workers
    _u('gunicorn.workers.base_async', 'AsyncWorker.handle_request')
    _u('gunicorn.workers.gthread', 'ThreadWorker.handle_request')
    _u('gunicorn.workers.sync', 'SyncWorker.handle')
    _u('gunicorn.workers.sync', 'SyncWorker.handle_request')


def _w_app_init(wrapper, instance, args, kwargs):
    wrapper(*args, **kwargs)

    Pin(
        service='gunicorn',
        app='gunicorn',
        app_type=AppTypes.web,
    ).onto(instance)

    if instance.cfg is None:
        return

    def _wrap_hook(name, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    if 'pre_request' in instance.cfg.settings:
        instance.cfg.settings['pre_request'] = _wrap_hook('pre_request', instance.cfg.pre_request)

    if 'post_request' in instance.cfg.settings:
        instance.cfg.settings['post_request'] = _wrap_hook('post_request', instance.cfg.post_request)


def _w_wsgi(app, wsgi):
    @functools.wraps(wsgi)
    def wrapper(environ, start_response, *args, **kwargs):
        pin = Pin.get_from(app)
        if not pin or not pin.enabled():
            return wsgi(environ, start_response)

        span = _get_root_span(pin)
        if not span:
            return wsgi(environ, start_response)

        def _start_response(status, headers):
            code, _, _ = status.partition(' ')
            try:
                code = int(code)
            except ValueError:
                pass

            span.set_tag(http.STATUS_CODE, code)
            if 500 <= code < 600:
                span.error = 1

            return start_response(status, headers)

        return wsgi(environ, _start_response, *args, **kwargs)
    return wrapper


def _w_app_wsgi(wrapper, instance, args, kwargs):
    return _w_wsgi(instance, wrapper(*args, **kwargs))


def _w_parser_init(wrapper, instance, args, kwargs):
    wrapper(*args, **kwargs)

    source = None
    if len(args) > 1:
        source = args[1]
    elif 'source' in kwargs:
        source = kwargs['source']
    if not source:
        return

    pin = Pin.get_from(source)
    if not pin:
        return

    pin.onto(instance)


def _w_parser_next(wrapper, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return wrapper(*args, **kwargs)

    with pin.tracer.trace('gunicorn.parse_request', service=pin.service) as span:
        span.set_tag('gunicorn.request.count', instance.req_count)

        req = None
        try:
            req = wrapper(*args, **kwargs)
            return req
        finally:
            _parse_req_resource(pin, req)


def _w_worker_handle(wrapper, instance, args, kwargs):
    pin = Pin.get_from(instance.app)
    if not pin or not pin.enabled():
        return wrapper(*args, **kwargs)

    if not len(args) > 2:
        return wrapper(*args, **kwargs)

    listener, client = args[:2]
    client = PinnedObjectProxy(client)
    pin.onto(client)
    with pin.tracer.trace('gunicorn.request', service=pin.service, span_type=http.TYPE) as span:
        span.set_tag('gunicorn.worker.pid', instance.pid)
        span.set_tag('gunicorn.worker.parent_pid', instance.ppid)
        span.set_tag('gunicorn.worker.class', instance.cfg.worker_class_str)
        span.set_tag('gunicorn.version', gunicorn.__version__)
        span.set_tag('http.ssl', instance.cfg.is_ssl)
        return wrapper(listener, client, *args[2:], **kwargs)


def _w_worker_handle_request(wrapper, instance, args, kwargs):
    pin = Pin.get_from(instance.app)
    if not pin or not pin.enabled():
        return wrapper(*args, **kwargs)

    with pin.tracer.trace('gunicorn.handle_request', service=pin.service):
        req = None
        if len(args) > 2:
            req = args[1]
        elif 'req' in kwargs:
            req = kwargs['req']

        try:
            return wrapper(*args, **kwargs)
        finally:
            _parse_req_resource(pin, req)


def _w_worker_handle_error(wrapper, instance, args, kwargs):
    pin = Pin.get_from(instance.app)
    if not pin or not pin.enabled():
        return wrapper(*args, **kwargs)

    span = _get_root_span(pin)
    if not span:
        return wrapper(*args, **kwargs)

    span.set_traceback()
    with pin.tracer.trace('gunicorn.handle_error', service=pin.service):
        return wrapper(*args, **kwargs)


def _w_util_write_error(wrapper, instance, args, kwargs):
    client = None
    status_int = None
    if len(args) > 2:
        client = args[0]
        status_int = args[1]
    else:
        return wrapper(*args, **kwargs)

    pin = Pin.get_from(client)
    if not pin or not pin.enabled():
        return wrapper(*args, **kwargs)

    span = _get_root_span(pin)
    if not span:
        return wrapper(*args, **kwargs)

    span.set_tag(http.STATUS_CODE, status_int)


class PinnedObjectProxy(ObjectProxy):
    __slots__ = ('_datadog_pin', )
