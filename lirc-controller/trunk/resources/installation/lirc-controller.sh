#!/bin/sh

### BEGIN INIT INFO
# Provides:          lirc-controller
# Required-Start:    $all
# Required-Stop:     mpd
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Extended remote controller daemon 
# Description:       Extended remote controller daemon
### END INIT INFO

. /lib/lsb/init-functions

PATH=/sbin:/bin:/usr/sbin:/usr/bin
NAME=lirc-controllerd
DESC="Extended remote controller daemon"
DAEMON="/path/to/python"
ARGS="/path/to/run.py --conf /path/to/configuration.cfg --xml /path/to/configuration.xml"
PIDFILE=/var/run/contollerd/pid

start() {
	log_daemon_msg "Starting $DESC" "$NAME"
	PIDDIR=$(dirname "$PIDFILE")
	if [ ! -d "$PIDDIR" ]; then
		mkdir -m 0755 $PIDDIR
	fi
	# start deamon
	start-stop-daemon --start --background --make-pidfile --quiet --oknodo --pidfile "$PIDFILE" \
        --exec "$DAEMON" "$ARGS"	
}

stop() {
	log_daemon_msg "Stopping $DESC" "$NAME"	
	start-stop-daemon --stop --quiet --oknodo --pidfile "$PIDFILE"
	log_end_msg $? 
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 2
        ;;
esac