#!/bin/sh
arg1=$1
arg2=$2

if [ -z $arg2 ] || [ $arg1 == "-h" ]; then 
  echo "Monitoring Container"
  echo "usage $0 <command> <path to config.txt>"
  echo "Possible commands:"
  echo "build: Build Containers"
  echo "-h: This help text"
  echo "install: Install Configuration"
  echo "start: Start all components"
  echo "stop: Stop all components"
  echo ""
  exit 0
fi

if ! [ -f $arg2 ]; then
  echo  "Configuration not found in $arg2"
  echo ""
  exit 1
fi
  
tag=$(grep "tag=" $arg2 | cut -d"=" -f2)
dir=$(grep "config=" $arg2 | cut -d"=" -f2)
if [ -z $dir ] || [ -z $tag ]; then 
  echo "Configuration direcotry not found in config"
  exit 1
fi

if [ $arg1 == "build" ]; then
  export MALLOC_ARENA_MAX=2
  source=$(grep "source=" $arg2 | cut -d"=" -f2)
  echo "Building $tag from $source"
  singularity build $tag $source
  exit $?
fi

if [ $arg1 == "install" ]; then
  MYUID=$(id -u)
  if ! [ -d $dir ]; then 
    mkdir $dir
    if [ $? -ne 0 ]; then
      echo "Failed to mkdir $dir"
      exit 1
    fi
  fi
  singularity run -B $dir:/monicfg $tag install
fi

if [ $arg1 == "start" ]; then
  if [ -f $dir/moni/keys.json ]; then
    EXPORTER=$(cat $dir/moni/keys.json | jq -r -e '.exporter.port')
    if [ $? -ne 0 ]; then
      EXPORTER=""
    fi
  else 
    echo "Exporter Configuration not found in $dir/moni/keys.json"
    exit 1
  fi
  if ! [ -n "$EXPORTER" ]; then
    echo "Path exporter/port not found in $dir/moni/keys.json"
    exit 1
  fi
  for services in $(cat $arg2 | grep -v "#" | grep -v source= | grep -v tag= | grep -v config=); do
    echo "Starting $services"
    #docker run -u $MYUID --rm --name moni_exporter -d -p $EXPORTER:$EXPORTER -v $DIR:/monicfg moni.py $arg1
  done
fi

if [ $arg1 == "stop" ]; then
  singularity run -B $dir:/monicfg $tag stop
fi

exit 0
