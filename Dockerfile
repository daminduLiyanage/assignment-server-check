FROM python:3

WORKDIR /root

# COPY requirements.txt start.py task.py task2.py lseg-keypair-2.pem create_empty_bucket_log.py ./
COPY requirements.txt *.py lseg-keypair-2.pem ./
RUN pip install -r requirements.txt && \
    chmod +x *.py  && \
    rm /etc/localtime && \
    ln -s /usr/share/zoneinfo/Asia/Colombo /etc/localtime

