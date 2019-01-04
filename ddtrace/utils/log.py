import multiprocessing
import os
import threading


def format_log_message(msg, *args, **kwargs):
    if args:
        msg = msg % args

    pid = os.getpid()
    thread = threading.current_thread()
    process = multiprocessing.current_process()

    return '({}:{}) ({}:{}) {}'.format(process.name, pid, thread.name, threading.get_ident(), msg)
