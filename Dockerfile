FROM debian

RUN mkdir /home/moni
RUN mkdir /home/exporter
COPY moni.py /home/moni
COPY reader.py /home/moni
COPY bufr.py /home/moni
COPY grib.py /home/moni
COPY oscar.py /home/moni
COPY tac.py /home/moni
COPY exporter.py /home/exporter
COPY entrypoint.sh /home
COPY keys.json /home/moni

RUN apt-get update && apt-get install -y gnupg apt-transport-https software-properties-common wget
RUN wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
RUN echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list

RUN apt-get update && apt-get -y install git jq less gcc python3 python3-pip libeccodes-dev libeccodes-tools prometheus grafana 
RUN apt-get -y install prometheus-alertmanager prometheus-apache-exporter prometheus-blackbox-exporter prometheus-mqtt-exporter prometheus-nginx-exporter prometheus-node-exporter

RUN pip install eccodes-python prometheus_client requests countrycode
RUN chmod gou+x /home/moni/moni.py
RUN chmod gou+x /home/exporter/exporter.py
RUN chmod gou+x /home/entrypoint.sh

RUN grafana-cli plugins install grafana-worldmap-panel

ENTRYPOINT ["/home/entrypoint.sh"]
CMD ["-h"]
