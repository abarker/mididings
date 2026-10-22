#!/bin/bash
# Usage: run.sh <python for engine> <python for sender> <backend> <run seconds>
export JACK_DEFAULT_SERVER=mdtest_srv JACK_NO_START_SERVER=1
D=$(dirname "$0")
"$2" "$D/sender.py" $(( $4 + 10 )) 2>/dev/null &
SP=$!
timeout -s KILL $(( $4 + 8 )) "$1" "$D/mdtest.py" "$3" "$4" 2>&1 >/dev/null | grep -E "^OK|Error|error" | head -3
rc=${PIPESTATUS[0]}
kill $SP 2>/dev/null; wait $SP 2>/dev/null
[ "$rc" = 137 ] && echo "DEADLOCK (killed after $(( $4 + 8 )) s)"
