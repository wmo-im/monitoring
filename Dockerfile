FROM alpine

PULL moni.py

RUN apk --update add git less openssh python3 && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/*

VOLUME /git
WORKDIR /git

ENTRYPOINT ["ls"]
CMD ["--help"]
