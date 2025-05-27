#!/bin/sh

# Iniciar servidor de métricas do Prometheus
python -c "
from prometheus_client import start_http_server
import threading

def start_prometheus_server():
    start_http_server(9646)

threading.Thread(target=start_prometheus_server, daemon=True).start()
"

# Iniciar o Locust normalmente
locust -f locustfile.py --host=http://api.local
