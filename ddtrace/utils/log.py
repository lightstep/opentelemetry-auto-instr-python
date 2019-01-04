import multiprocessing
import os
import threading


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
        tname = thread.name
        tid = threading.get_ident()
        process = multiprocessing.current_process()
        pname = process.name
    except Exception:
        pass

    return '({}:{}) ({}:{}) {}'.format(pname, pid, tname, tid, msg)
