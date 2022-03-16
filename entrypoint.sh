#!/bin/bash
arg1=$1
arg2=$2
arg3=$3

echo "Monitoring entrypoint. Got Parameters: $@"
if [ -z $arg1 ] || [ $arg1 == "-h" ]; then 
  echo "Monitoring Container"
  echo "Possible commands:"
  echo "-h: This help text"
  echo "-i: Install Configuration"
  echo "-p: Start Prometheus and Grafana"
  echo "-e [basefile] [datafile]: Start exporter"
  echo "-f: Generate metrics from configuration"
  echo "-s: Stop services"
fi

if [ ! -d /monicfg ]; then
  echo "Please mount a configuration directory to /monicfg" ]
  exit 1
fi

if [ $arg1 == "-e" ]; then
  /home/exporter/exporter.py -b $arg2 -d $arg3 &
  EX=$!
  echo $EX > /monicfg/exporter.pid
fi

if [ $arg1 == "-i" ]; then
   cp -r /etc/prometheus /monicfg
   cp -r /usr/share/grafana/ /monicfg
   cp -r /var/lib/grafana/plugins /monicfg/grafana/data
fi

if [ $arg1 == "-p" ]; then
   prometheus --storage.tsdb.path=/monicfg/prometheus --config.file=/monicfg/prometheus/prometheus.yml &
   PR=$!
   cd /monicfg/grafana || exit 1
   grafana-server &
   GR=$!
   echo $PR > /monicfg/prometheus.pid
   echo $GR > /monicfg/grafana.pid
fi

if [ $arg1 == "-f" ]; then
  /home/moni/moni.py -f $arg2
fi

if [ $arg1 == "-s" ]; then
   for p in /monicfg/*.pid; do
     echo "Stopping $p"
     kill $(cat $p)
     rm $p
   done 
fi
exit 0
