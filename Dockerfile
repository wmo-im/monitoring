FROM debian

COPY moni.py /home

RUN apt-get update && apt-get -y install git less gcc python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

RUN pip install eccodes-python

ENTRYPOINT ["/home/moni.py"]
CMD ["-f"]
