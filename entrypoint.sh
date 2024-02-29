#!/bin/bash
echo "Monitoring entrypoint. Got Parameters: $@" >&2
arg1=$1
arg2=$2
arg3=$3
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
  echo "-a: Start Alertmanager Prometheus"
  echo "-i: Install Configuration"
  echo "-p: Start Prometheus and Grafana"
  echo "-pe [exporter] [params]: Start Prometheus Exporters. Without exporter show available exporters"
  echo "-e: Run exporter from configuration"
  echo "-g: Generate GeoJSON from configuration"
  echo "-s: Stop services"
  echo ""
  echo "The configuration needs to be mounted at /monicfg"
  exit 0
fi

if [ ! -d /monicfg ]; then
  echo "Please mount a configuration directory to /monicfg" ]
  exit 1
fi

if [ $arg1 == "-a" ]; then
  prometheus-alertmanager --config.file=/monicfg/prometheus/alertmanager.yml --web.config.file=/monicfg/prometheus/web.yml &
  EX=$!
  echo $EX > /monicfg/alertmanager.pid
  MYPID="$MYPID $EX"
  echo ""
  wait $(cat /monicfg/alertmanager.pid)
  echo "Alertmanager stopped: $?"
  exit 0
fi

if [ $arg1 == "-e" ]; then
  /home/exporter/exporter.py -f /monicfg/moni/keys.json &
  EX=$!
  echo $EX > /monicfg/exporter.pid
  MYPID="$MYPID $EX"
  echo ""
  wait $(cat /monicfg/exporter.pid)
  echo "Exporter stopped: $?"
  exit 0
fi

if [ $arg1 == "-i" ]; then
   cp -r /etc/prometheus /monicfg
   cp -r /usr/share/grafana/ /monicfg
   mkdir /monicfg/grafana/data
   cp -r /var/lib/grafana/plugins/ /monicfg/grafana/data
   mkdir /monicfg/moni
   cp /home/moni/keys.json /monicfg/moni/
   exit 0
fi

if [ $arg1 == "-p" ]; then
   prometheus --storage.tsdb.path=/monicfg/prometheus --config.file=/monicfg/prometheus/prometheus.yml &
   PR=$!
   cd /monicfg/grafana || exit 1
   grafana-server &
   GR=$!
   echo $PR > /monicfg/prometheus.pid
   echo $GR > /monicfg/grafana.pid
   MYPID="$MYPID $PR $GR"
   echo ""
   wait $(cat /monicfg/grafana.pid)
   echo "Grafana stopped: $?"
   wait $(cat /monicfg/prometheus.pid)
   echo "Prometheus stopped: $?"
   exit 0
fi

if [ $arg1 == "-pe" ]; then
  if [ -z $arg2 ]; then 
    echo "-pe requires an exporter (-pe [exporter])"
    echo "Available exporters for -pe are"
    echo "prometheus-alertmanager"
    echo "prometheus-apache-exporter" 
    echo "prometheus-blackbox-exporter" 
    echo "prometheus-mqtt-exporter" 
    echo "prometheus-nginx-exporter" 
    echo "prometheus-node-exporter"
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

if [ $arg1 == "-g" ]; then
  /home/moni/moni.py -f /monicfg/moni/keys.json &
  MN=$!
  echo $MN > /monicfg/moni.pid
  MYPID="$MYPID $MN"
  echo ""
  wait $(cat /monicfg/moni.pid)
  echo "moni stopped: $?"
  exit 0
fi

if [ $arg1 == "-s" ]; then
   if [ -f /.dockerenv ]; then
     echo "Please use docker stop to stop docker containers"
     exit 1
   else
     for p in /monicfg/*.pid; do
       echo "Stopping $p"
       kill $(cat $p)
       rm $p
     done 
     exit 0
   fi
fi
echo "Invalid Parameter: $arg1"
echo "Use -h for help"
exit 1
