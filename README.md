# OCR de Certidões Imobiliárias com Ollama

Sistema de OCR para certidões de imóveis brasileiras usando LLM local via Docker.

## Pré-requisitos

- Docker Desktop instalado
- Python 3.8+
- 8GB+ RAM livre recomendado

## 1. Instalar e Configurar Ollama

### Criar e executar container Ollama

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### Verificar se está rodando

```bash
docker ps
```

## 2. Baixar Modelos de IA

### Instalar modelos (requer 8GB+ RAM livre)

```bash
# Modelo de visão (7.8GB) - para OCR
docker exec -it ollama ollama pull llama3.2-vision

# Modelo de texto (4.7GB) - para estruturação JSON
docker exec -it ollama ollama pull llama3
```

### Verificar modelos instalados

```bash
docker exec -it ollama ollama list
```

## 3. Instalar Dependências Python

```bash
pip install ollama pandas
```

## 4. Executar o OCR

### Comando básico

```bash
python main.py imagem_exemplo.png
```

### Com saída CSV

```bash
python main.py imagem_exemplo.png --output resultado.csv
```

### Com JSON detalhado

```bash
python main.py imagem_exemplo.png --show-json
```

### Com todas as opções

```bash
python main.py imagem_exemplo.png --show-json --output resultado.csv
```

## Campos Extraídos

- **Matrícula**: Número de registro
- **Proprietário**: Nome do proprietário
- **CPF**: CPF do proprietário
- **Endereço do Imóvel**: Rua, número, bairro
- **Município**: Cidade
- **Estado**: UF
- **Área do Terreno**: Metragem
- **Registro Anterior**: Matrícula anterior
- **Data de Registro**: Data
- **Cartório**: Nome e localização
- **Livro/Folha**: Referências do cartório
- **Observações**: Anotações importantes

## Comandos Úteis

### Parar Ollama

```bash
docker stop ollama
```

### Iniciar Ollama

```bash
docker start ollama
```

### Ver logs

```bash
docker logs ollama
```

### Testar modelo manualmente

```bash
docker exec -it ollama ollama run moondream
```

## Solução de Problemas

### Erro "signal: killed"
- Feche outros programas para liberar RAM
- Precisa de pelo menos 10GB RAM disponível
- Considere adicionar mais RAM ou usar API externa (GPT-4V, Claude)

### Container não inicia
```bash
docker rm ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### Modelos não aparecem
```bash
docker exec -it ollama ollama list
```

## Requisitos de Memória

| Modelo | RAM Necessária |
|--------|----------------|
| llama3.2-vision | ~8GB |
| llama3 | ~5GB |

**Total recomendado: 10GB+ RAM disponível**