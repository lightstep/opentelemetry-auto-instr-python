import multiprocessing
import os
import threading

from ..compat import to_unicode


def format_log_message(msg, *args, **kwargs):
    if args:
        msg = msg % args

    pid = None
    pname = None
    tname = None
    tid = None
    try:
        pid = os.getpid()
        thread = threading.current_thread()
        tname = to_unicode(thread.name)
        tid = threading.get_ident()
        process = multiprocessing.current_process()
        pname = to_unicode(process.name)
    except Exception:
        pass

    return to_unicode('({}:{}) ({}:{}) {}').format(pname, pid, tname, tid, msg)
