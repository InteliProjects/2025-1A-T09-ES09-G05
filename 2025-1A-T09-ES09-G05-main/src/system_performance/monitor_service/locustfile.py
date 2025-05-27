from locust import HttpUser, task, between
from prometheus_client import Counter, Histogram, start_http_server, Gauge
import time
import threading
import random

# Iniciar servidor Prometheus na porta 9646
def start_prometheus_server():
    start_http_server(9646)

threading.Thread(target=start_prometheus_server, daemon=True).start()

# Definição das métricas
REQUEST_COUNT = Counter("locust_requests_total", "Total de requisições enviadas", ["endpoint", "status_code"])
REQUEST_LATENCY = Histogram("locust_request_latency_seconds", "Tempo de resposta das requisições", ["endpoint"])
REQUEST_SUCCESS_COUNT = Counter("locust_requests_success", "Total de requisições bem-sucedidas", ["endpoint"])
REQUEST_FAILURE_COUNT = Counter("locust_requests_failure", "Total de requisições com falha", ["endpoint"])

# Definição das métricas de Business Drivers
EXECUTION_TIME_HISTOGRAM = Histogram("tempo_execucao_segundos", "Tempo de execução para alocar um entregador")
WAIT_TIME_HISTOGRAM = Histogram("tempo_espera_total_segundos", "Tempo total de espera antes da alocação")
DISTANCE_HISTOGRAM = Histogram("distancia_entregador_km", "Distância do entregador mais próximo")
CLIMA_INSTAVEL_COUNT = Counter("pedidos_clima_instavel_total", "Número total de pedidos feitos em clima instável")
WAIT_TIME_STABLE_HISTOGRAM = Histogram("tempo_espera_estavel_segundos", "Tempo de espera em clima estável")
WAIT_TIME_UNSTABLE_HISTOGRAM = Histogram("tempo_espera_instavel_segundos", "Tempo de espera em clima instável")

# Métricas estáticas do git com nomes únicos
TOTAL_FILES = Histogram("git_total_files", "Total de arquivos versionados.")
TOTAL_FOLDERS = Histogram("git_total_folders", "Total de pastas versionadas.")
TOTAL_CODE_LINES = Histogram("git_total_code_lines", "Total de linhas de código.")
TOTAL_FILES_PER_EXT = Histogram("git_total_files_per_ext", "Total de arquivos por extensão.")

# Métricas de tempo no estado
STATE_TIME_HISTOGRAM = Histogram("tempo_estado", "Tempo de permanência no estado", ["estado"])
STATE_COUNT = Counter("estado_entregador_total", "Contagem de estados do entregador", ["estado"])

# Métricas de confiabilidade
MTBF = Gauge('mtbf_seconds', 'Mean Time Between Failures')
MTTR = Gauge('mttr_seconds', 'Mean Time To Repair')
SYSTEM_UP = Gauge("system_up", "Indica se o sistema está online (1) ou offline (0)")

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Tempo de espera entre requisições

    @task
    def get_status_entregador(self):
        """Consulta o status do entregador e registra o tempo em cada estado"""
        endpoint = "/entregadores/status"
        print(f"[INFO] Requisição para {endpoint}")

        try:
            response = self.client.get(f"http://rappitors_api:8000{endpoint}")

            if response.status_code == 200:
                data_list = response.json()  # lista de entregadores

                for entregador in data_list:
                    historico = entregador.get("historico_estados", [])

                    for registro in historico:
                        estado_bruto = registro.get("estado")
                        tempo_no_estado = registro.get("tempo_no_estado_s")

                        if estado_bruto and tempo_no_estado is not None:
                            tempo_no_estado = float(tempo_no_estado)  # <- Converte para float
                            print(f"[INFO] Registrando métrica: Estado={estado_bruto}, Tempo={tempo_no_estado}s")
                            STATE_TIME_HISTOGRAM.labels(estado=estado_bruto).observe(tempo_no_estado)
                            STATE_COUNT.labels(estado=estado_bruto).inc()


            else:
                print(f"[ERROR] Falha ao acessar {endpoint} - Status {response.status_code}")
                REQUEST_FAILURE_COUNT.labels(endpoint=endpoint).inc()

        except Exception as e:
            print(f"[ERROR] Erro ao processar os dados: {e}")
            
    @task
    def get_entregador(self):
        """Teste de carga no endpoint /entregadores/{id}"""
        entregador_id = random.randint(1, 9)
        endpoint = f"/entregadores/{entregador_id}"
        self.perform_request(endpoint)

    @task
    def get_pedido_taxa(self):
        """Teste de carga no endpoint /pedidos/{pedido_id}/taxa"""
        pedido_id = random.randint(1, 9)
        endpoint = f"/pedidos/{pedido_id}/taxa"
        self.perform_request(endpoint)

    @task
    def get_git_stats_task(self):
        endpoint = f"/git"
        response = self.client.get(f"http://rappitors_api:8000{endpoint}")

        data = response.json()
        total_files = data.get('total_files')
        total_folders = data.get('total_folders')
        total_code_lines = data.get('total_code_lines')
        total_files_per_ext = data.get('total_files_per_ext')

        TOTAL_FILES.observe(total_files)
        TOTAL_FOLDERS.observe(total_folders)
        TOTAL_CODE_LINES.observe(total_code_lines)
        TOTAL_FILES_PER_EXT.observe(total_files_per_ext)
        
    @task
    def alocar_entregador(self):
        endpoint = "/alocar_entregador"
        response = self.client.get(f"http://rappitors_api:8000{endpoint}")  

        if response.status_code == 200:
            try:
                data = response.json()
                tempo_espera = data.get("tempo_espera_total", 0)
                distancia = data.get("distancia_km", 0)
                clima_instavel = data.get("clima_instavel", False)
                
                WAIT_TIME_HISTOGRAM.observe(tempo_espera)
                DISTANCE_HISTOGRAM.observe(distancia)

                # Métricas condicionais ao clima
                if clima_instavel:
                    CLIMA_INSTAVEL_COUNT.inc()
                    WAIT_TIME_UNSTABLE_HISTOGRAM.observe(tempo_espera)
                else:
                    WAIT_TIME_STABLE_HISTOGRAM.observe(tempo_espera)

                # Métrica de sucesso/erro
                if data.get("aceitou_pedido"):
                    REQUEST_SUCCESS_COUNT.labels(endpoint=endpoint).inc()
                else:
                    REQUEST_FAILURE_COUNT.labels(endpoint=endpoint).inc()
            except Exception as e:
                print(f"Erro ao processar JSON: {e}")
                REQUEST_FAILURE_COUNT.labels(endpoint=endpoint).inc()
        else:
            print(f"Falha na requisição - status {response.status_code}")
            REQUEST_FAILURE_COUNT.labels(endpoint=endpoint).inc()

    @task
    def check_system_health(self):
        try:
            response = self.client.get("http://rappitors_api:8000/health")
            if response.status_code != 200:
                print(f"[ERROR] /health retornou status {response.status_code} - {response.text}")
            try:
                data = response.json()
            except Exception as json_e:
                print(f"[ERROR] Falha ao decodificar JSON: {json_e} - Corpo da resposta: {response.text}")
                data = {}
            if response.status_code == 200:
                SYSTEM_UP.set(1)
                mtbf_value = data.get("mtbf")
                if mtbf_value is not None:
                    MTBF.set(mtbf_value)
            else:
                SYSTEM_UP.set(0)
                mttr_value = data.get("mttr")
                if mttr_value is not None:
                    MTTR.set(mttr_value)
        except Exception as e:
            print(f"[ERROR] Erro ao consultar /health: {e}")
            SYSTEM_UP.set(0)

    def perform_request(self, endpoint):
        """Executa a requisição e coleta métricas no Prometheus"""
        start_time = time.time()
        response = self.client.get(f"http://rappitors_api:8000{endpoint}")  # Nome do serviço no Docker
        latency = time.time() - start_time

        # Atualizar métricas do Prometheus
        REQUEST_COUNT.labels(endpoint=endpoint, status_code=response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

        # Registrar sucesso ou falha
        if response.status_code == 200:
            REQUEST_SUCCESS_COUNT.labels(endpoint=endpoint).inc()
        else:
            REQUEST_FAILURE_COUNT.labels(endpoint=endpoint).inc()  # ADICIONADO
