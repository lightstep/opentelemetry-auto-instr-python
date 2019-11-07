from unittest import mock

_EXPORTER = mock.Mock()


def build_exporter(**kwargs):
    for k, v in kwargs.items():
        setattr(_EXPORTER, k, v)
    return _EXPORTER
