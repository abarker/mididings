Deadlock reproduction for the GIL / engine-mutex fix.

Minimal, no JACK needed (each deadlocks with stock mididings and prints
"no deadlock" with the fix; faulthandler prints both stacks on a hang):

    python minimal.py               # dummy backend, process_event
    python minimal_output_event.py  # ALSA sequencer, output_event

stock_output_minimal_output_event.txt is the stock output of the second.

Under real load, with a running JACK engine:

Needs a private JACK server and JACK-Client (pip install JACK-Client):

    JACK_NO_START_SERVER=1 jackd -n mdtest_srv -d dummy -r 48000 -p 1024 &
    ./run.sh <python with mididings> <python with JACK-Client> jack-rt 10
    ./run.sh <python with mididings> <python with JACK-Client> jack 10

mdtest.py runs Process(handler), where the handler sleeps 10 ms (holds
the engine's process mutex with the GIL released), while another thread
calls output_event in a loop; sender.py feeds one CC per cycle.  Before
the fix this deadlocks on the first overlap (run.sh prints DEADLOCK after
its timeout); after it, the script reports the event and call counts.
