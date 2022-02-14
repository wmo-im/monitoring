FROM alpine

RUN apk --update add git less openssh python3 && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

VOLUME /git
WORKDIR /git

PULL moni.py

ENTRYPOINT ["ls"]
CMD ["--help"]
