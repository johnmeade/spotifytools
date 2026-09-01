#!/bin/sh
# tmux kill-session sends SIGHUP, which gunicorn treats as "reload workers",
# not "shut down" -- it survives as an orphan still holding the port (see
# run.sh). This finds the actual gunicorn arbiter for this app and sends it
# SIGTERM instead, which is gunicorn's documented "quick shutdown".
cd "$(dirname "$0")"

pids=$(pgrep -f 'gunicorn.*:9224 spotifytools\.app:app')
if [ -z "$pids" ]; then
    echo "spotifytools is not running"
    exit 0
fi

# workers share the arbiter's comm ("gunicorn"); the arbiter is the one
# gunicorn process whose parent isn't itself a gunicorn process
gpids=""
for pid in $pids; do
    [ "$(ps -o comm= -p "$pid" 2>/dev/null)" = "gunicorn" ] && gpids="$gpids $pid"
done

arbiter=""
for pid in $gpids; do
    ppid=$(ps -o ppid= -p "$pid" | tr -d ' ')
    is_worker=false
    for other in $gpids; do
        [ "$ppid" = "$other" ] && is_worker=true
    done
    [ "$is_worker" = false ] && arbiter="$pid"
done

if [ -z "$arbiter" ]; then
    echo "could not identify the gunicorn arbiter among pids:$gpids" >&2
    exit 1
fi

echo "stopping spotifytools (arbiter pid $arbiter)"
kill -TERM "$arbiter"
