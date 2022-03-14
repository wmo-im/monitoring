FROM debian

COPY moni.py /home
COPY exporter.py /home
COPY bufr.py /home
COPY grib.py /home
COPY oscar.py /home
COPY tac.py /home

RUN apt-get update && apt-get -y install git less gcc python3 python3-pip libeccodes-dev libeccodes-tools && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /var/cache/apk/* && \
    echo "Done"

RUN pip install eccodes-python prometheus_client requests countrycode
RUN chmod gou+x /home/moni.py
RUN chmod gou+x /home/exporter.py

ENTRYPOINT ["/home/moni.py"]
CMD ["-f keys.json"]
