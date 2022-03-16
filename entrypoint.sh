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
fi

if [ ! -d /monicfg ]; then
  echo "Please mount a configuration directory to /monicfg" ]
  exit 1
fi

if [ $arg1 == "-e" ]; then
  /home/exporter/exporter.py -b $arg2 -d $arg3 &
  EX=$!
fi

if [ $arg1 == "-i" ]; then
   cp -r /etc/prometheus /monicfg
   cp -r /usr/share/grafana/ /monicfg
fi

if [ $arg1 == "-p" ]; then
   prometheus --storage.tsdb.path=/monicfg/prometheus --config.file=/monicfg/prometheus/prometheus.yml &
   PR=$!
   cd /monicfg/grafana || exit 1
   grafana-server &
   GR=$!
fi

if [ $arg1 == "-f" ]; then
  /home/moni/moni.py -f $arg2
fi

exit 0
