from ...constants import ANALYTICS_SAMPLE_RATE_KEY
from ...ext import AppTypes, redis as redisx
from ...internal.import_hooks import hooks, register_module_hook
from ...pin import Pin
from ...settings import config
from ...vendor.wrapt import wrap_function_wrapper as _w
from .util import format_command_args, _extract_conn_tags


@register_module_hook('redis')
def patch_redis(redis):
    if redis.VERSION < (3, 0, 0):
        _w(redis, 'StrictRedis.execute_command', traced_execute_command)
        _w(redis, 'StrictRedis.pipeline', traced_pipeline)
        _w(redis, 'Redis.pipeline', traced_pipeline)
    else:
        _w(redis, 'Redis.execute_command', traced_execute_command)
        _w(redis, 'Redis.pipeline', traced_pipeline)

    Pin(service=redisx.DEFAULT_SERVICE, app=redisx.APP, app_type=AppTypes.db).onto(redis.StrictRedis)


@register_module_hook('redis.client')
def patch_redis_client(redis_client):
    pipeline = 'BasePipeline' if hasattr(redis_client, 'BasePipeline') else 'Pipeline'
    _w(redis_client, '{}.execute'.format(pipeline), traced_execute_pipeline)
    _w(redis_client, '{}.immediate_execute_command'.format(pipeline), traced_execute_command)


def unpatch():
    hooks.deregister('redis', patch_redis)
    hooks.deregister('redis.client', patch_redis_client)


#
# tracing functions
#
def traced_execute_command(func, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return func(*args, **kwargs)

    with pin.tracer.trace(redisx.CMD, service=pin.service, span_type=redisx.TYPE) as s:
        query = format_command_args(args)
        s.resource = query
        s.set_tag(redisx.RAWCMD, query)
        if pin.tags:
            s.set_tags(pin.tags)
        s.set_tags(_get_tags(instance))
        s.set_metric(redisx.ARGS_LEN, len(args))
        # set analytics sample rate if enabled
        s.set_tag(
            ANALYTICS_SAMPLE_RATE_KEY,
            config.redis.get_analytics_sample_rate()
        )
        # run the command
        return func(*args, **kwargs)


def traced_pipeline(func, instance, args, kwargs):
    pipeline = func(*args, **kwargs)
    pin = Pin.get_from(instance)
    if pin:
        pin.onto(pipeline)
    return pipeline


def traced_execute_pipeline(func, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return func(*args, **kwargs)

    # FIXME[matt] done in the agent. worth it?
    cmds = [format_command_args(c) for c, _ in instance.command_stack]
    resource = '\n'.join(cmds)
    tracer = pin.tracer
    with tracer.trace(redisx.CMD, resource=resource, service=pin.service) as s:
        s.span_type = redisx.TYPE
        s.set_tag(redisx.RAWCMD, resource)
        s.set_tags(_get_tags(instance))
        s.set_metric(redisx.PIPELINE_LEN, len(instance.command_stack))

        # set analytics sample rate if enabled
        s.set_tag(
            ANALYTICS_SAMPLE_RATE_KEY,
            config.redis.get_analytics_sample_rate()
        )

        return func(*args, **kwargs)


def _get_tags(conn):
    return _extract_conn_tags(conn.connection_pool.connection_kwargs)

