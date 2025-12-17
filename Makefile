# Define o nome da imagem Docker
DOCKER_IMAGE_NAME = olympic-networks
CONTAINER_NAME = olympic-analysis-container

# Define o executável Python dentro do container Docker
# A flag -u desabilita o buffering para ver logs em tempo real
DOCKER_PYTHON = python3 -u

# Define os diretórios dos scripts do pipeline e saídas, relativos ao diretório /app do container
PIPELINE_DIR = main/src/pipeline
OUTPUTS_DIR = main/src/outputs

# Lista de scripts do pipeline para rodar em ordem
PIPELINE_SCRIPTS = \
	$(PIPELINE_DIR)/01_network_generation.py \
	$(PIPELINE_DIR)/02a_community_enrichment.py \
	$(PIPELINE_DIR)/02b_community_cohesion.py \
	$(PIPELINE_DIR)/02c_community_typology.py \
	$(PIPELINE_DIR)/03_additional_metrics.py

# Alvo padrão: constrói a imagem, roda o pipeline, gera figuras e tabelas
all: build run-pipeline generate-figures generate-tables

# Constrói a imagem Docker
build: Dockerfile
	@echo "Construindo imagem Docker $(DOCKER_IMAGE_NAME)..."
	docker build -t $(DOCKER_IMAGE_NAME) .
	@echo "Imagem Docker $(DOCKER_IMAGE_NAME) construída com sucesso."

# Executa o pipeline completo dentro de um novo container
run-pipeline: build
	@echo "Rodando pipeline de análise dentro do container Docker..."
	# Remove qualquer container existente com o mesmo nome para evitar conflitos
	docker rm -f $(CONTAINER_NAME) || true
	# Cria o diretório results no host se não existir
	mkdir -p results
	# Executa o container montando o diretório results como volume
	# Isso permite que os arquivos sejam salvos diretamente no host
	docker run --name $(CONTAINER_NAME) -v "$(PWD)/results:/app/main/results" $(DOCKER_IMAGE_NAME) bash -c "\
		cd $(PIPELINE_DIR) && \
		echo '=== Executando 01_network_generation.py ===' && \
		$(DOCKER_PYTHON) 01_network_generation.py && \
		echo '=== Executando 02a_community_enrichment.py ===' && \
		$(DOCKER_PYTHON) 02a_community_enrichment.py && \
		echo '=== Executando 02b_community_cohesion.py ===' && \
		$(DOCKER_PYTHON) 02b_community_cohesion.py && \
		echo '=== Executando 02c_community_typology.py ===' && \
		$(DOCKER_PYTHON) 02c_community_typology.py && \
		echo '=== Executando 03_additional_metrics.py ===' && \
		$(DOCKER_PYTHON) 03_additional_metrics.py \
	"
	@echo "Pipeline de análise concluído. Resultados salvos em ./results"
	docker rm -f $(CONTAINER_NAME) # Limpa o container após a execução
	@echo "Container $(CONTAINER_NAME) removido."

# Gera figuras (assumindo que figures.py usa os resultados)
generate-figures:
	@echo "Gerando figuras..."
	# Cria diretório de figuras se não existir
	mkdir -p docs/monografia/figuras
	# Executa o script de figuras dentro de um container temporário
	# Montamos os volumes para resultados e monografia (em main/src/monografia)
	docker run --rm \
		-v "$(PWD)/results:/app/main/results" \
		-v "$(PWD)/docs/monografia:/app/main/src/monografia" \
		$(DOCKER_IMAGE_NAME) bash -c "\
		cd $(OUTPUTS_DIR) && $(DOCKER_PYTHON) figures.py\
	"
	@echo "Figuras geradas. Verifique o diretório 'docs/monografia/figuras'."

# Gera tabelas LaTeX (assumindo que latex_tables.py usa os resultados)
generate-tables:
	@echo "Gerando tabelas LaTeX..."
	# Cria diretório de tabelas se não existir
	mkdir -p docs/monografia/tabelas
	# Executa o script de tabelas dentro de um container temporário
	# Montamos os volumes para resultados e monografia (em main/docs/monografia)
	docker run --rm \
		-v "$(PWD)/results:/app/main/results" \
		-v "$(PWD)/docs/monografia:/app/main/docs/monografia" \
		$(DOCKER_IMAGE_NAME) bash -c "\
		cd $(OUTPUTS_DIR) && $(DOCKER_PYTHON) latex_tables.py\
	"
	@echo "Tabelas LaTeX geradas. Verifique o diretório 'docs/monografia/tabelas'."

# Limpa os arquivos e diretórios gerados
clean:
	@echo "Limpando arquivos e diretórios gerados..."
	rm -rf results main/results
	@echo "Limpeza completa."

.PHONY: all build run-pipeline generate-figures generate-tables clean
