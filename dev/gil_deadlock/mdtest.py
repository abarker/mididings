"""Engine under test.  A Process handler sleeps (holds the engine's
process mutex, releases the GIL) while another thread calls
output_event in a loop.  Exits 0 after RUN_S seconds if no deadlock;
a deadlock freezes every Python thread, so the caller's timeout fires."""
import os, sys, threading, time
from mididings import *
from mididings import engine as E
from mididings.event import CtrlEvent

backend, run_s = sys.argv[1], float(sys.argv[2])
config(backend=backend, client_name='mdtest')
handled = [0]
sent = [0]

def handler(ev):
    time.sleep(0.01)
    handled[0] += 1
    return ev

def spam():
    ev = CtrlEvent(1, 1, 7, 64)
    while True:
        E.output_event(ev)
        sent[0] += 1

def watchdog():
    time.sleep(run_s)
    sys.stderr.write(f"OK: {handled[0]} events handled, "
                     f"{sent[0]} output_event calls, no deadlock\n")
    sys.stderr.flush()
    os._exit(0)

threading.Timer(1.5, lambda: threading.Thread(target=spam, daemon=True).start()).start()
threading.Thread(target=watchdog, daemon=True).start()
run(Process(handler))
