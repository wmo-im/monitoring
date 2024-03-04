FROM debian

RUN mkdir /home/moni
RUN mkdir /home/exporter
COPY moni.py /home/moni
COPY reader.py /home/moni
COPY bufr.py /home/moni
COPY grib.py /home/moni
COPY oscar.py /home/moni
COPY tac.py /home/moni
COPY exporter.py /home/exporter
COPY entrypoint.sh /home
COPY keys.json /home/moni

RUN apt-get update && apt-get install -y gnupg apt-transport-https software-properties-common wget
RUN wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
RUN echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list

RUN apt-get update && apt-get -y install git jq less gcc python3 python3-pip python3-venv libeccodes-dev libeccodes-tools prometheus grafana 
RUN apt-get -y install prometheus-alertmanager prometheus-apache-exporter prometheus-blackbox-exporter prometheus-mqtt-exporter prometheus-nginx-exporter prometheus-node-exporter python3-requests python3-eccodes python3-prometheus-client curl

RUN python3 -m venv /venv
RUN /venv/bin/pip install countrycode eccodes prometheus_client requests

RUN chmod gou+x /home/moni/moni.py
RUN chmod gou+x /home/exporter/exporter.py
RUN chmod gou+x /home/entrypoint.sh
RUN ln -s /home/moni/moni.py /bin/moni_reader
RUN ln -s /home/exporter/exporter.py /bin/moni_exporter
RUN ln -s $(which prometheus) /bin/moni_prometheus
RUN ln -s $(which prometheus-alertmanager) /bin/moni_alertmanager
RUN ln -s $(which grafana-server) /bin/moni_grafana
RUN ln -s $(which prometheus-blackbox-exporter) /bin/moni_black
RUN ln -s $(which prometheus-node-exporter) /bin/moni_node

RUN grafana-cli plugins install grafana-worldmap-panel
RUN ln -s /monicfg/grafana/data /usr/share/grafana/data


#Install alertmanager.ui
#Source in /usr/share/prometheus/alertmanager/generate-ui.sh
RUN apt-get install -y libjs-bootstrap4 fonts-font-awesome curl uglifyjs golang-github-prometheus-alertmanager-dev
RUN mkdir /home/elm
RUN cd /home/elm &&  curl --location https://github.com/elm/compiler/releases/download/0.19.0/binaries-for-linux.tar.gz | tar xz -C /home/elm
RUN cd /usr/share/gocode/src/github.com/prometheus/alertmanager/ui/app && /home/elm/elm make src/Main.elm --optimize --output ./app.js
RUN mkdir -p /usr/share/prometheus/alertmanager/ui
RUN mkdir -p /usr/share/prometheus/alertmanager/ui/lib

RUN uglifyjs /usr/share/gocode/src/github.com/prometheus/alertmanager/ui/app/app.js --compress 'pure_funcs="F2,F3,F4,F5,F6,F7,F8,F9,A2,A3,A4,A5,A6,A7,A8,A9",pure_getters,keep_fargs=false,unsafe_comps,unsafe' --mangle --output /usr/share/prometheus/alertmanager/ui/script.js
RUN cp /usr/share/gocode/src/github.com/prometheus/alertmanager/ui/app/index.html /usr/share/gocode/src/github.com/prometheus/alertmanager/ui/app/favicon.ico /usr/share/prometheus/alertmanager/ui
RUN ln -s /usr/share/fonts-font-awesome /usr/share/prometheus/alertmanager/ui/lib/font-awesome
RUN ln -s /usr/share/nodejs/bootstrap/dist /usr/share/prometheus/alertmanager/ui/lib/bootstrap4

ENTRYPOINT ["/home/entrypoint.sh"]
CMD ["-h"]
