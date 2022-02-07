FROM python:3.10

COPY . .

RUN pip3 install -r requirements.txt --index-url http://nexus.prod.uci.cu/repository/pypi-proxy/simple/ --trusted-host nexus.prod.uci.cu

CMD make run FILE="$FILE"
