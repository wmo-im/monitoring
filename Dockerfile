FROM debian

COPY moni.py /home

RUN apt-get update && apt-get -y install git less gcc python3 python3-pip libeccodes-dev libeccodes-tools && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /var/cache/apk/* && \
    echo "Done"

RUN pip install eccodes-python
RUN chmod gou+x /home/moni.py

ENTRYPOINT ["/home/moni.py"]
CMD ["-f keys.json"]
