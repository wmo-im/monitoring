#!/bin/sh
arg1=$1
arg2=$2
arg3=$3

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
  source=$(grep "source=" $arg2 | cut -d"=" -f2)
  echo "Building $tag from $source"
  docker build --tag $tag $source
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
  docker run -u $MYUID --rm -v $dir:/monicfg $tag install
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
    name=$(echo $services | cut -d, -f1)
    if [ -z $arg3 ]; then
      sn=$name
    else
      sn=$arg3
    fi
    
    id=$(echo $services | cut -d, -f2)
    port=$(echo $services | cut -d, -f3)
    mounts=$(echo $services | cut -d, -f4 | sed -e 's/;/ /')
    args=$(echo $services | cut -d, -f5 | sed -e 's/;/ /')
    if [ -z $name ] || [ -z $id ]; then
      echo "Invalid entry for $services"
      exit 1
    fi
    MOUNT="-v $dir:/monicfg "
    for m in $mounts; do
      MOUNT="$MOUNT -v $m"
    done
    PORT=""
    if [ $name == "moni_exporter" ]; then PORT="-p $port:$EXPORTER"; fi
    if [ $name == "moni_reader" ]; then PORT=""; fi
    if [ $name == "moni_prometheus" ]; then PORT="-p $port:9090"; fi
    if [ $name == "moni_alertmanager" ]; then PORT="-p $port:9093"; fi
    if [ $name == "moni_grafana" ]; then PORT="-p $port:3000"; fi
    if [ $name == "moni_black" ]; then PORT="-p $port:9115"; fi
    if [ $name == "moni_node" ]; then PORT="-p $port:9100"; fi
    if [ -z $port ]; then PORT=""; fi
    if [ $name == $sn ]; then
      echo "docker run -u $id --rm --name $name -d $PORT $MOUNT $tag start $name $args"
      docker run -u $id --rm --name $name -d $PORT $MOUNT $tag start $name $args &
    else
      echo "$name != $arg3"
    fi
  done
fi

if [ $arg1 == "stop" ]; then
  if [ -z $arg3 ]; then
    arg3="moni"
  fi
  for i in $(docker ps | grep moni.py | grep $arg3 | cut -d' ' -f1); do
    docker stop $i
  done
fi

exit 0
