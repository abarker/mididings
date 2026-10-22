"""The same deadlock through output_event(), the usual way to send from a
timer or OSC thread.  Needs the ALSA sequencer (no connections needed).

Expected with stock mididings: faulthandler prints both stacks after 5 s
and exits.  With the fix: prints "no deadlock".
"""
import faulthandler
import threading
import time

from mididings import Process, config, engine, setup
from mididings.event import CtrlEvent

faulthandler.dump_traceback_later(5, exit=True)


def slow(ev):
    time.sleep(0.1)
    return ev


config(backend='alsa', client_name='gil_deadlock_test')
e = engine.Engine()
e.setup({setup.get_config('data_offset'): Process(slow)}, None, None, None)
ev = CtrlEvent(1, 1, 7, 64)

a = threading.Thread(target=e.process_event, args=(ev,))
a.start()
time.sleep(0.05)        # thread A is now inside slow()
e.output_event(ev)
a.join()
print("no deadlock")
