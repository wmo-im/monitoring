#!/bin/bash
echo "Monitoring entrypoint. Got Parameters: $@" >&2
arg1=$1
arg2=$2
shift
shift
MYPID=""

trap stop SIGTERM SIGINT SIGQUIT SIGHUP

stop(){
  trap - SIGTERM SIGINT SIGQUIT SIGHUP
  for p in $MYPID; do
    kill $p;
  done
  exit 0
}

if [ -z $arg1 ] || [ $arg1 == "-h" ]; then 
  echo "Monitoring Container"
  echo "Possible commands:"
  echo "-h: This help text"
  echo "install: Install Configuration"
  echo "start: Start Services"
  echo "stop: Stop services"
  echo ""
  echo "The configuration needs to be mounted at /monicfg"
  exit 0
fi

if [ ! -d /monicfg ]; then
  echo "Please mount a configuration directory to /monicfg" ]
  exit 1
fi

if [ $arg1 == "start" ]; then
  if [ -z $arg2 ]; then
    echo "start requires the service to start as second parameter"
    exit 1
  fi
  if [ $arg2 == "moni_alertmanager" ]; then
    prometheus-alertmanager --config.file=/monicfg/prometheus/alertmanager.yml --web.config.file=/monicfg/prometheus/web.yml &
    EX=$!
    echo $EX > /monicfg/alertmanager.pid
    MYPID="$MYPID $EX"
    echo ""
    wait $(cat /monicfg/alertmanager.pid)
    echo "Alertmanager stopped: $?"
    exit 0
  fi
  if [ $arg2 == "moni_exporter" ]; then
    /home/exporter/exporter.py -f /monicfg/moni/keys.json &
    EX=$!
    echo $EX > /monicfg/exporter.pid
    MYPID="$MYPID $EX"
    echo ""
    wait $(cat /monicfg/exporter.pid)
    echo "Exporter stopped: $?"
    exit 0
  fi
  if [ $arg2 == "moni_prometheus" ]; then
    prometheus --storage.tsdb.path=/monicfg/prometheus --config.file=/monicfg/prometheus/prometheus.yml &
    PR=$!
    echo $PR > /monicfg/prometheus.pid
    wait $(cat /monicfg/prometheus.pid)
    echo "Prometheus stopped: $?"
    exit 0
  fi
  if [ $arg2 == "moni_grafana" ]; then
    cd /usr/share/grafana || exit 1
    grafana-server &
    GR=$!
    echo $GR > /monicfg/grafana.pid
    MYPID="$MYPID $PR $GR"
    echo ""
    wait $(cat /monicfg/grafana.pid)
    echo "Grafana stopped: $?"
    exit 0
  fi
  if [ $arg2 == "moni_reader" ]; then
    /home/moni/moni.py -f /monicfg/moni/keys.json &
    MN=$!
    echo $MN > /monicfg/moni.pid
    MYPID="$MYPID $MN"
    echo ""
    wait $(cat /monicfg/moni.pid)
    echo "moni stopped: $?"
    exit 0
  fi

  if [ $(which $arg2) ]; then
    cd /monicfg/prometheus || exit 1
    $arg2 $@&
    EX=$!
    echo $EX > /monicfg/$arg2.pid
    MYPID="$MYPID $EX"
    echo ""
    wait $(cat /monicfg/$arg2.pid)
    echo "$arg2 stopped: $?"
    exit 0
  else
    echo "$arg2 not found"
    exit 1
  fi

fi

if [ $arg1 == "install" ]; then
   cp -r /etc/prometheus /monicfg
   mkdir /monicfg/grafana
   mkdir /monicfg/grafana/data
   cp -r /var/lib/grafana/plugins/ /monicfg/grafana/data
   mkdir /monicfg/moni
   cp /home/moni/keys.json /monicfg/moni/
   exit 0
fi

if [ $arg1 == "stop" ]; then
   if [ -f /.dockerenv ]; then
     echo "Please use docker stop to stop docker containers"
     exit 1
   else
     for p in /monicfg/*.pid; do
       echo "Stopping $p"
       kill $(cat $p)
       sleep 1
       kill -s 0 $(cat $p)
       if [ $? -eq 0 ]; then
         sleep 1
         kill $(cat $p)
         sleep 2
         kill -9 $(cat $p)
       fi
       rm $p
     done 
     exit 0
   fi
fi
echo "Invalid Parameter: $arg1"
echo "Use -h for help"
exit 1
