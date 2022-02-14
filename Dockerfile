FROM alpine

COPY moni.py /home

RUN apk --update add git less openssh gcc python3 py3-pip libssp_nonshared && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

RUN pip install eccodes-python

ENTRYPOINT ["/home/moni.py"]
CMD ["-f"]
