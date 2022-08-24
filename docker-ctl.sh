#!/bin/sh
#ToDo Get Ports from Config

#BUILD="docker build --tag moni.py:latest https://github.com/wmo-im/wismonitoring.git"
BUILD="docker build --tag moni.py:latest moni"
DIR=/root/monitoring/moni

arg1=$1
arg2=$2
arg3=$3
shift
shift

if [ -z $arg1 ] || [ $arg1 == "-h" ]; then 
  echo "Monitoring Container"
  echo "Possible commands:"
  echo "-b: Build Containers"
  echo "-h: This help text"
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

if [ $arg1 == "-b" ]; then
   $BUILD
fi

if [ $arg1 == "-e" ]; then
  if [ -f $DIR/moni/keys.json ]; then
    EXPORTER=$(cat $DIR/moni/keys.json | jq -r -e '.exporter.port')
    if [ $? -ne 0 ]; then
      EXPORTER=""
    fi
  else 
    echo "Exporter Configuration not found in $DIR/moni/keys.json"
    exit 1
  fi
  if [ -n "$EXPORTER" ]; then
    docker run --rm --name moni_exporter -d -p $EXPORTER:$EXPORTER -v $DIR:/monicfg moni.py $arg1
  else
    echo "Path exporter/port not found in $DIR/moni/keys.json"
    exit 1
  fi
fi

if [ $arg1 == "-i" ]; then
   docker run --rm -v $DIR:/monicfg moni.py $arg1
fi

if [ $arg1 == "-p" ]; then
   docker run --rm --name moni_prometheus -d -p 9090:9090 -p 3000:3000 -v $DIR:/monicfg moni.py $arg1
fi

if [ $arg1 == "-pe" ]; then
#ToDo Correct Port for other exporters
   docker run -d --rm --name moni_pe -p 9115:9115 -v $DIR:/monicfg moni.py $arg1 $arg2
fi

if [ $arg1 == "-g" ]; then
  docker run -d --rm --name moni_reader -v $DIR:/monicfg moni.py $arg1
fi

if [ $arg1 == "-s" ]; then
  for i in $(docker ps | grep moni.py | cut -d' ' -f1); do
    docker stop $i
  done
fi
