FROM debian

COPY moni.py /home
COPY exporter.py /home
COPY bufr.py /home
COPY grib.py /home
COPY oscar.py /home
COPY tac.py /home

RUN apt-get install -y gnupg curl
RUN curl https://packages.grafana.com/gpg.key | sudo apt-key add -k
RUN apt-get update && apt-get -y install git less gcc python3 python3-pip libeccodes-dev libeccodes-tools prometheus grafana 

RUN pip install eccodes-python prometheus_client requests countrycode
RUN chmod gou+x /home/moni.py
RUN chmod gou+x /home/exporter.py

ENTRYPOINT ["/home/moni.py"]
CMD ["-f keys.json"]
