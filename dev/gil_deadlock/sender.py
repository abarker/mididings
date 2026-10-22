"""Sends one CC per JACK cycle into mdtest's input."""
import sys, time, jack
c = jack.Client('mdsender', no_start_server=True)
out = c.midi_outports.register('out')

@c.set_process_callback
def process(frames):
    out.clear_buffer()
    out.write_midi_event(0, (0xB0, 7, 64))

c.activate()
for _ in range(100):
    ports = c.get_ports('mdtest', is_midi=True, is_input=True)
    if ports:
        break
    time.sleep(0.1)
c.connect(out, ports[0])
time.sleep(float(sys.argv[1]))
