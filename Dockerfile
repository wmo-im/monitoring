FROM debian

COPY moni.py /home
COPY exporter.py /home
COPY bufr.py /home
COPY grib.py /home
COPY oscar.py /home
COPY tac.py /home

RUN apt-get update && apt-get install -y gnupg apt-transport-https software-properties-common wget
RUN wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
RUN echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list

RUN apt-get update && apt-get -y install git less gcc python3 python3-pip libeccodes-dev libeccodes-tools prometheus grafana 

RUN pip install eccodes-python prometheus_client requests countrycode
RUN chmod gou+x /home/moni.py
RUN chmod gou+x /home/exporter.py
RUN cp -r /usr/local/share/grafana /home
RUN cp -r /etc/prometheus /home

ENTRYPOINT ["/home/moni.py"]
CMD ["-f keys.json"]
