# Inteli - Instituto de Tecnologia e Liderança


<p align="center">
<a href= "https://www.inteli.edu.br/"><img src="./docs/imagens/inteli.png" alt="Inteli - Instituto de Tecnologia e Liderança" border="0" width=40% height=40%></a>
</p>

<br>

# Rappitors


## 👨‍🎓 Integrantes:
- [Anna Aragão](https://www.linkedin.com/in/anna-aragao/)
- [Bruna Brasil](https://www.linkedin.com/in/bruna-brasil-alexandre/)
- [João Sotto](https://www.linkedin.com/in/jo%C3%A3o-pedro-sotto-maior/)
- [Kaiane Souza](https://www.linkedin.com/in/kaiane-souza/)
- [Paula Piva](https://www.linkedin.com/in/paulapiva03/)


## 👩‍🏫 Professores:
### Orientador
- <a href="https://www.linkedin.com/in/reginaldo-arakaki-9574222b/">Reginaldo Arakaki</a>
### Instrutores
- <a href="https://www.linkedin.com/in/jefferson-o-silva/">Jefferson Oliveira</a>
- <a href="https://www.linkedin.com/in/ovidio-netto/">Ovidio Netto</a>
- <a href="https://www.linkedin.com/in/rafael-jacomossi-6135b0a1/">Rafael Jacomossi</a>
- <a href="https://www.linkedin.com/in/gui-cestari/">Guilherme Cestari</a>
- <a href="https://www.linkedin.com/in/fernando-pizzo-208b526a/">Fernando Pizzo</a>
- <a href="https://www.linkedin.com/in/filipe-gon%C3%A7alves-08a55015b/">Filipe Gonçalves</a>


## 📜 Descrição

Este projeto foi desenvolvido em parceria com a **Rappi**, com foco na melhoria da **experiência dos entregadores** por meio da implementação de testes automatizados, observabilidade e estratégias robustas de controle de qualidade de software. O trabalho teve como objetivo garantir **confiabilidade e desempenho** na exibição de informações críticas como **taxa dos pedidos** e **ganhos dos entregadores**.

## 🎯 Objetivos

- Monitorar e garantir a exibição correta dos ganhos dos entregadores, mesmo com falhas na API.
- Reduzir o tempo de resposta da interface (< 2 segundos em 95% das requisições).
- Aumentar a confiabilidade da experiência dos entregadores em ambiente de produção.
- Criar uma base de testes documentada e replicável para validação contínua.

## ⚙️ O que foi desenvolvido

- **Serviço de cache com Redis**, que armazena os últimos ganhos conhecidos dos entregadores, garantindo a disponibilidade dos dados mesmo em caso de falha da API.
- **Simulador de comportamento do entregador**, com dados mockados, utilizado para validar diferentes fluxos de exibição e comportamento do sistema.
- **Testes automatizados com Gherkin**, cobrindo cenários críticos relacionados à exibição de ganhos e taxas.
- **Testes de carga com Locust**, medindo o tempo de resposta da API e o impacto sob carga contínua.
- **Monitoramento com Prometheus e logs estruturados**, acompanhando métricas de latência, disponibilidade e uso do cache.
- **Documentação técnica em Markdown**, incluindo hipóteses de testes, estrutura da arquitetura, estratégias de integração e histórico de sprints.

## 📁 Estrutura do Projeto

- `tests/gherkin/`: Cenários de teste BDD com Gherkin para simular casos reais enfrentados por entregadores.
- `services/cache/`: Serviço de cache implementado com Redis para garantir a exibição de dados mesmo em situações de erro da API.
- `locust/`: Scripts de carga com Locust, focados em medir tempo de resposta e comportamento sob diferentes níveis de requisição.
- `monitoring/`: Configurações de métricas expostas para Prometheus e logs estruturados.
- `docs/`: Documentação da arquitetura de integração, estratégias de controle de qualidade e hipóteses de testes.
- `scripts/`: Scripts utilitários para simulação de APIs, geração de massa de dados e automação de testes.

## 🧩 Foco técnico

Este projeto também teve como direcionadores:

- **Engenharia de Qualidade**, com foco em testes orientados a negócios e problemas reais.
- **Observabilidade**, através de métricas precisas e alertas baseados em limiares definidos.
- **Testes como Documentação Viva**, utilizando Gherkin como forma de expressar regras de negócio e garantir rastreabilidade.

## 📁 Estrutura de pastas

A organização deste repositório foi pensada para garantir modularidade, escalabilidade e facilidade de manutenção, além de suportar práticas modernas de testes, documentação e observabilidade.

🗂️ Visão Geral

```
 .
   ||--docker-compose.yml
   ||--docs
   ||--  |__imagens
   ||--  |__Index.md
   ||--grafana_data
   ||--prometheus.yml
   ||--pytest.ini
   ||--README.md
   ||--src
   ||--  |__rappitors_api
   ||--  |__system_performance
   ||--  |__test
```

✨ Destaques
Modularização: Cada serviço ou componente está isolado em seu próprio diretório, promovendo manutenibilidade e reaproveitamento de código.

Observabilidade: O sistema já inclui suporte nativo ao Prometheus e Grafana para coleta e visualização de métricas.

Testes automatizados: O diretório test/ segue a abordagem BDD com arquivos .feature e steps bem organizados.

Infraestrutura como código: O uso de docker-compose.yml e Dockerfiles facilita a replicação do ambiente em diferentes máquinas.

## 🔧 Instalação

Para rodar o projeto localmente, siga os passos abaixo.

### 1. Pré-requisitos

Certifique-se de ter os seguintes itens instalados:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

Opcional (para desenvolvimento e testes manuais):

- [Python 3.10+](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

---

### 2. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

As demais instruções podem ser encontradas no arquivo "Index.md"

## 🗓️ Histórico de Entregas por Sprint

### ✅ Sprint 1 (03/02 a 14/02)
**Principais entregas:**
- Início do projeto com definição de objetivos e estrutura inicial.
- Criação do repositório e setup de ambiente.
- Primeiros testes com Gherkin voltados a exibição de ganhos e taxas.
- Introdução ao uso de Prometheus e logs estruturados.

---

### ✅ Sprint 2 (17/02 a 28/02)
**Principais entregas:**
- Implementação do serviço de cache para ganhos dos entregadores.
- Conexão dos testes com API real para validação de dados.
- Uso de dados mock para simulação de comportamento do entregador.
- Estruturação de logs estruturados e alertas via Prometheus.
- Finalização de critérios OKRs com foco nos entregadores.

---

### ✅ Sprint 3 (03/03 a 14/03)
**Principais entregas:**
- Documentação e definição dos Requisitos Funcionais e Não Funcionais.
- Mapeamento de RFs para alocação e entregadores.
- Refatoração de tarefas Locust para simular cenários de entrega.
- Início da integração com Prometheus e melhorias em docker-compose.

---

### ✅ Sprint 4 (17/03 a 28/03)
**Principais entregas:**
- Integração com Grafana e exposição de métricas.
- Refatoração de rotas e padronização de APIs.
- Criação do serviço de cache com controle de latência.
- Documentação de protocolos e controle de versionamento.
- Documentação final da Sprint 4 e refinamento dos dashboards.
- Criação de dashboards para status, saúde e negócios.

---

### ✅ Sprint 5 (31/03 a 11/04)
**Principais entregas:**
- Finalização da integração com Prometheus e Locust.
- Adição de métricas customizadas e dashboards de controle.
- Integração com APIs externas de geolocalização e clima.
- Organização da documentação de integração externa.
- Métricas dos entregadores implementadas e refinadas.
- Ajustes finais no Prometheus e melhorias na API Git Info.


## 📋 Licença/License

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/2023M4T10Inteli/grupo3">Rappitors</a> by <a href="https://github.com/2023M3T10-Inteli">Inteli</a>, is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

