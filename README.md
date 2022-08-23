# WIS Monitoring

This project generates GeoJSON and OpenMetrics from TAC, BUFR or GRIB input. Also contained are Prometheus and Grafana for the monitoring of the metrics. This guide assumes you built a container from the Dockerfile. The commands are for singularity but should work with Docker similarly.

This shows the steps to setup two feeds from data -> GeoJSON. Then generate Openmetrics output. And finally start Prometheus and Grafana to monitor and visualize the results.

All available switches can be displayed with **singularity run moni.sif -h**

## Prepare docker container (only for docker)
1. Configure relevant variables in docker-ctl.sh  
2. Run docker-ctl.sh -b  

## Initialize monitoring for data feed 1
1. Create Configuration directory  
   mkdir feed1.cfg
2. Populate Configuration directory  
   singularity run -B feed1.cfg:/monicfg moni.sif -i  
   (docker-ctl.sh -i)
3. Configure the Process in feed1.cfg/moni/keys.cfg  
   The programm process data from the listed directories and stores output in the named file. Format can be one of TAC, BUFR or GRIB. After processing the data is moved to the path listed at done. keep is the time for which the information is contained in the GeoJSON output in hours and can be between 1 and 23
4. Start the first process  
   singularity run -B feed1.cfg:/monicfg moni.sif -g   
   (docker-ctl.sh -g)

## Initialize monitoring for data feed 2
1. Create Configuration directory  
   mkdir feed2.cfg
2. Populate Configuration directory  
   singularity run -B feed2.cfg:/monicfg moni.sif -i  
   (docker-ctl.sh -i)
3. Configure the Process in feed2.cfg/moni/keys.cfg  
   The programm process data from the listed directories and stores output in the named file. Format can be one of TAC, BUFR or GRIB. After processing the data is moved to the path listed at done. keep is the time for which the information is contained in the GeoJSON output in hours and can be between 1 and 23
4. Start the second process  
   singularity run -B feed2.cfg:/monicfg moni.sif -g
   (docker-ctl.sh -g)
   
 Note, that the first few runs with data can take a while depending on the amount of station data, because OSCAR is queried for each new station once.
   
## Initialize OpenMetrics Exporter and Prometheus
1. Create Configuration directory  
   mkdir prometheus.cfg
2. Populate Configuration directory  
   singularity run -B prometheus.cfg:/monicfg moni.sif -i  
   (docker-ctl.sh -i)
3. Configure the exporter in prometheus.cfg/moni/keys.cfg. Port is the port on which the metrics are exported. sensor is the name of the center providing the metrics for example "sensor": "Offenbach Met. Com. Center". baseline and data are the files generated for data feed 1 resp. data feed 2. 
4. Start the exporter  
   singularity run -B prometheus.cfg:/monicfg moni.sif -e  
   (docker-ctl.sh -e)

Note: This starts an http server at port 9877. To see if everything works you can use curl localhost:9877 for example

4. Configure Prometheus  
   You can now configure Prometheus in prometheus.cfg/prometheus/prometheus.yml. The configuration should include the Openmetrics exporter as follows  
    -job_name: Monitoring    
        static_configs:  
            - targets: ['localhost:9877']
5. Start Prometheus and Grafana  
  singularity run -B prometheus.cfg:/monicfg moni.sif -p  
  (docker-ctl.sh -p)
  
Note: You should now be able to access Prometheus at Port 9090 and Grafana at Port 3000. To initialize login to Grafana use admin:admin

6. Optionally you can start additional Prometheus exporters using  
  singularity run -B prometheus.cfg:/monicfg moni.sif -pe  
  (docker-ctl.sh -pe)
