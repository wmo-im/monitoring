# WIS Monitoring

This project generates GeoJSON and OpenMetrics from TAC, BUFR or GRIB input. Also contained are Prometheus and Grafana for the monitoring of the metrics. 

Naming of the metrics for WIS2 is documented here https://github.com/wmo-im/wis2-metric-hierarchy

There are two control scripts. docker-ctl.sh for docker. singularity-ctl.sh for singularity/apptainer. The control scripts can be used to build, install, start and stop the different components on the respective plattform. 

This guide shows the steps to setup two seperate feeds from data -> GeoJSON. Then howto setup and generate Openmetrics output. The third section shows how to start and stop Prometheus and Grafana to monitor and visualize the results.

All available switches can be displayed with **docker-ctl.sh -h** resp. **singularity-ctl.sh -h**. In the following we only use docker-ctl.sh. The steps are the same for singularity-ctl.sh.

## Configure the control scripts
. The config.txt file contains the relevant settings for the control scripts. 
. The first line defines the source from which to build the container. This can either be a local directory, or a URL pointing to a container registry. The source needs to be accessbile for docker build resp. singularity build.
. The second line contains the build tag for docker resp. the target filename for singularity.
. The third line contains the directory in which the configuration files for the moni components will be stored.
. The following lines list the components that should be started together with the user id under which they should run (available for docker only) and the port on which they listen
. In the following use 
. Run docker-ctl.sh build <path to config.txt> 

## Initialize monitoring for data feed 1
. Copy config.txt to config1.txt and adjust the settings for a configuration directory for the first data feed for example by setting config=feed1.cfg
. Create and populate Configuration directory  
   Run docker-ctl.sh install config1.txt
. Configure the Process in feed1.cfg/moni/keys.cfg
   The programm processes data from the listed directories and stores output in the named file. Format can be one of TAC, BUFR or GRIB. After processing the data is moved to the path listed at done. keep is the time for which the information is contained in the GeoJSON output in hours and can be between 1 and 23
.   Disable all services except for moni\_reader in config1.txt
. Start the first process  
   docker-ctl.sh start config1.txt

## Initialize monitoring for data feed 2
. Follow the steps from above and setup a config2.txt with Configuration Directory feed2.cfg  
. Populate and configure the second data feed similar to the steps above  
. Start the second process  
   
 Note, that the first few runs with data can take a while depending on the amount of station data, because OSCAR is queried for each new station once.
   
## Initialize OpenMetrics Exporter and Prometheus
. Create Configuration directory  
   mkdir prometheus.cfg
. Adjust the settings in config.txt by setting config=prometheus.cfg
. Create and populate Configuration directory  
   Run docker-ctl.sh install config.txt
. Configure the exporter in prometheus.cfg/moni/keys.cfg. Port is the port on which the metrics are exported. centre-id is the name of the center providing the metrics for example "centre-id": "dwd-offenbach". baseline and data are the files generated for data feed 1 resp. data feed 2. 
. Configure Prometheus  
   You can now configure Prometheus in prometheus.cfg/prometheus/prometheus.yml. The configuration should include the Openmetrics exporter as follows  
    -job_name: Monitoring    
        static_configs:  
            - targets: ['localhost:9877']
. Select the required services in config.txt. Note, the moni\_reader is not required at this stage as it already has been started.
. Start the services with  
  docker-ctl.sh start config.txt
  
Note: This starts server processes on the configured ports. To see if everything works you can use curl localhost:<port> for example
Note: You should now also be able to access Prometheus at Port 9090 and Grafana at Port 3000. To initialize login to Grafana use admin:admin

## Initialize OpenMetrics Exporter and Prometheus
To stop all services use
docker-ctl stop <Config File>
