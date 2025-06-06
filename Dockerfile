FROM python:3.11-slim


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iproute2 \
        iputils-ping \
        net-tools \
        gcc \
        libssl-dev \
        libffi-dev \
        python3-dev \
        supervisor && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY . /app


RUN pip install --no-cache-dir cryptography


RUN echo '#!/bin/bash\n' \
         'exec /usr/bin/supervisord -c /app/supervisord.conf\n' \
    > /app/start.sh && chmod +x /app/start.sh


CMD ["/app/start.sh"]
