"""Minimal reproduction: Engine.process_event() / output_event() called from
one thread deadlock against a Python unit running in another, once that
unit releases the GIL (time.sleep, I/O, or simply running long enough for
the interpreter to hand the GIL to a waiting thread).  No MIDI system is
needed: the dummy backend, as in tests/helpers.py.

Thread A runs an event through Process(slow): the engine locks its process
mutex, and slow() releases the GIL while sleeping.  The main thread then
calls process_event(), which waits for that mutex while holding the GIL, so
slow() can never resume.  output_event() has the same lock order (see
minimal_output_event.py; the dummy backend can't output).  With a real
backend the engine's own thread plays thread A's part.

Expected with stock mididings: faulthandler prints both stacks after 5 s
and exits.  With the fix: prints "no deadlock".
"""
import faulthandler
import threading
import time

from mididings import Process, engine, setup
from mididings.event import CtrlEvent

faulthandler.dump_traceback_later(5, exit=True)


def slow(ev):
    time.sleep(0.1)
    return ev


setup._config_impl(backend='dummy')     # as tests/helpers.py does
e = engine.Engine()
e.setup({setup.get_config('data_offset'): Process(slow)}, None, None, None)
ev = CtrlEvent(1, 1, 7, 64)

a = threading.Thread(target=e.process_event, args=(ev,))
a.start()
time.sleep(0.05)        # thread A is now inside slow()
e.process_event(ev)
a.join()
print("no deadlock")
