FROM alpine

COPY moni.py /home

RUN apk --update add git less openssh python3 py3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

RUN pip add eccodes-python

ENTRYPOINT ["/home/moni.py"]
CMD ["-f"]
