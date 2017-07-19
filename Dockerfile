FROM python

MAINTAINER ilectra "ilektra.christidi@ucl.ac.uk"

RUN git clone https://github.com/UCL-CloudLabs/docker-sample -b levine

WORKDIR /docker-sample

RUN pip install -r requirements.txt

COPY YLR422W.0.ssw11.hhr /docker-sample/

EXPOSE 5006

CMD bokeh serve lolliplotServer.py --allow-websocket-origin=$AZURE_URL:5006
