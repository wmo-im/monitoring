FROM debian

COPY moni.py /home

RUN apk --update add git less openssh gcc python3 py3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

RUN pip install eccodes-python

ENTRYPOINT ["/home/moni.py"]
CMD ["-f"]
