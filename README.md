# dubby

![CI](https://github.com/jonatasu/dubby/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Docker](https://img.shields.io/badge/docker-ready-green)

**Tradução e dublagem de vídeos/áudios com web UI moderna**

Pipeline completo: extração de áudio → transcrição (ASR) → tradução → síntese de voz → remux

✅ **Funcionalidades ativas:**

- 🎤 ASR com Faster-Whisper (modelo local)
- 🌐 Tradução com argostranslate (EN↔PT, EN↔ES)
- 🔊 TTS com vozes nativas por idioma (pyttsx3)
- 🎬 Processamento de vídeo com FFmpeg
- 🐳 Deploy com Docker completo
- 🚀 Instalação automática com bootstrap

## 🚀 Instalação Rápida (Recomendado)

### Opção 1: Bootstrap Automático

```bash
# Clone o repositório
git clone https://github.com/jonatasu/dubby.git
cd dubby

# Execute o bootstrap (instala tudo automaticamente)
python3 scripts/bootstrap.py
```

O script bootstrap:

- ✅ Verifica Python 3.12+
- ✅ Instala dependências do sistema
- ✅ Cria ambiente virtual
- ✅ Instala dependências Python
- ✅ Baixa modelo ASR
- ✅ Inicializa tradução
- ✅ Testa funcionalidade

### Opção 2: Docker (Zero Setup)

```bash
# Pull da imagem oficial
docker pull ghcr.io/jonatasu/dubby:latest

# Execute com volumes persistentes
docker run --rm -it -p 8000:8000 \
  -v "$PWD/models:/app/models" \
  -v "$PWD/uploads:/app/uploads" \
  -v "$PWD/outputs:/app/outputs" \
  ghcr.io/jonatasu/dubby:latest
```

## 📋 Requisitos do Sistema

### Dependências Obrigatórias

**Python 3.12+** (versão estável mais recente)

**Sistema (macOS):**

```bash
brew install ffmpeg git python@3.12
```

**Sistema (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install ffmpeg git python3.12 python3.12-venv espeak espeak-data
```

**Sistema (CentOS/RHEL):**

```bash
sudo yum install ffmpeg git python3.12 espeak
```

### Dependências Python (Automáticas)

O arquivo `requirements.txt` inclui **todas as dependências com versões fixas**:

```
# Core Framework
fastapi==0.115.0              # Web framework
uvicorn[standard]==0.30.6      # ASGI server
pydantic-settings==2.5.2      # Configuration

# Audio/Speech Processing
faster-whisper==1.0.3         # ASR
pyttsx3==2.99                  # TTS
scipy==1.14.0                  # Audio processing
soundfile==0.12.1              # Audio I/O
ffmpeg-python==0.2.0           # Video processing

# Translation (Fixed Versions)
argostranslate==1.9.6          # Translation engine
ctranslate2==4.6.0             # Translation backend
sacremoses==0.0.53             # Text preprocessing
sentencepiece==0.2.0           # Tokenization
stanza==1.1.1                  # NLP pipeline

# PyTorch Stack
torch==2.5.1                   # Deep learning
torchvision==0.20.1            # Vision utilities
torchaudio==2.5.1              # Audio utilities

# Testing
pytest==8.3.2                  # Testing framework
```

## 🏃‍♂️ Executar Localmente

### Método 1: Make (Recomendado)

```bash
# Instalar dependências e executar
make run

# Ou apenas executar (se já instalado)
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Método 2: Tasks do VS Code

Se estiver usando VS Code, use as tasks configuradas:

- `Ctrl+Shift+P` → "Tasks: Run Task" → "Run dubby (uvicorn)"

### Acesso

🌐 **Web Interface:** http://localhost:8000

## 🐳 Docker

### Local Build & Run

```bash
# Build da imagem
docker build -t dubby:local .

# Execute com volumes (dados persistentes)
docker run --rm -it -p 8000:8000 \
  -v "$PWD/models:/app/models" \
  -v "$PWD/uploads:/app/uploads" \
  -v "$PWD/outputs:/app/outputs" \
  dubby:local
```

### Docker Compose (Recomendado)

```bash
# Build e execute em uma linha
docker compose up --build

# Execute em background
docker compose up -d --build
```

### Imagem Oficial (GHCR)

**Imagens pré-construídas** estão disponíveis no GitHub Container Registry:

```bash
# Última versão (main branch)
docker pull ghcr.io/jonatasu/dubby:latest

# Versão específica (release tags)
docker pull ghcr.io/jonatasu/dubby:v1.0.0

# Execute a imagem oficial
docker run --rm -it -p 8000:8000 \
  -v "$PWD/models:/app/models" \
  -v "$PWD/uploads:/app/uploads" \
  -v "$PWD/outputs:/app/outputs" \
  ghcr.io/jonatasu/dubby:latest
```

## ☁️ Deploy em Produção

### Plataformas Suportadas

**Container-based (Recomendado):**

- 🚀 Railway
- 🔸 Render
- ✈️ Fly.io
- ☁️ Google Cloud Run
- 🔷 Azure Container Instances
- 📦 AWS ECS/Fargate

**Configuração básica:**

- 🐳 Use a imagem: `ghcr.io/jonatasu/dubby:latest`
- 🔌 Exponha a porta: `8000`
- 💾 Monte volumes persistentes para: `models/`, `uploads/`, `outputs/`
- ⚙️ Variáveis de ambiente: veja `.env.example`

### PythonAnywhere (ASGI)

PythonAnywhere suporta aplicações ASGI:

1. **Ambiente virtual:** Crie com Python 3.12+ e instale `requirements.txt`
2. **Configuração ASGI:** Aponte para `asgi:application` (arquivo `asgi.py`)
3. **Arquivos estáticos:** Mapeie `/static` para `app/static` e `/outputs` para `outputs`
4. **FFmpeg:** Se não disponível, o app funcionará apenas com áudio
5. **Modelo offline:** Execute `python scripts/bootstrap.py` para configuração completa

## 🧪 Desenvolvimento e Testes

### Executar Testes

```bash
# Todos os testes
make test

# Com coverage
pytest --cov=app tests/

# Testes específicos
pytest tests/test_health.py -v
```

### Estrutura de Testes

```
tests/
├── test_health.py          # Testes de endpoints
├── test_basic.py           # Testes de UI
└── test_services.py        # Testes de serviços (ASR, tradução, TTS)
```

### Linting e Formatação

```bash
# Ruff (linter)
ruff check .

# Black (formatação)
black .

# Type checking
mypy app/
```

## 🔧 Troubleshooting

### Problemas Comuns

**1. Erro de importação argostranslate**

```bash
# Reinstale com versões fixas
pip install -r requirements.txt --force-reinstall
```

**2. Modelo ASR não encontrado**

```bash
# Re-baixe o modelo
python scripts/download_whisper_model.py
```

**3. TTS não funciona (macOS)**

```bash
# Verifique se o sistema tem vozes instaladas
say "test" # Deve funcionar
```

**4. FFmpeg não encontrado**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verifique instalação
ffmpeg -version
```

**5. Problemas de permissão (Docker)**

```bash
# Execute com usuário atual
docker run --user $(id -u):$(id -g) ...
```

### Logs e Debug

```bash
# Logs detalhados
export DEBUG=1
uvicorn app.main:app --log-level debug

# Logs Docker
docker logs container_name

# Health check
curl http://localhost:8000/health
```

## 📊 Status do Projeto

### ✅ Funcionalidades Implementadas

- [x] **ASR (Automatic Speech Recognition)**
  - Faster-Whisper com modelo local
  - Suporte a múltiplos idiomas
  - Detecção automática de idioma
- [x] **Tradução**
  - argostranslate offline
  - Pares: EN↔PT, EN↔ES (expansível)
  - Instalação automática de modelos
- [x] **TTS (Text-to-Speech)**
  - pyttsx3 com vozes nativas
  - Vozes específicas por idioma
  - Configuração automática de qualidade
- [x] **Processamento de Mídia**
  - FFmpeg para vídeo/áudio
  - Extração e remux automático
  - Suporte a múltiplos formatos
- [x] **Web Interface**
  - Upload de arquivos
  - Seleção de idiomas
  - Download de resultados
  - Status em tempo real
- [x] **Deploy e CI/CD**
  - Docker completo
  - GitHub Actions
  - GHCR publishing
  - Health checks

### 🔬 Experimental: Voice Cloning (OpenVoice & Spectral)

Status geral: camada de clonagem experimental suporta dois caminhos:

1. `openvoice` (ainda placeholder – aguarda modelos reais)
2. `spectral` (Fase 1) pseudo-clone: ajusta pitch e brilho espectral do áudio TTS gerado com base em um perfil da voz original.

#### Pipeline Alvo (OpenVoice completo)

1. Extrair áudio original (referência)
2. Gerar embedding / “tone color”
3. Converter texto traduzido em mel + vocoder com timbre preservado
4. Ajustar duração para casar com timestamps ASR

#### Modo Spectral (implementado nesta fase)

O modo `spectral` cria um perfil simples da voz de referência:

- `pitch` (estimativa fundamental via autocorrelação simplificada)
- `energy` (RMS)
- `centroid` (centro espectral)

Em seguida aplica sobre o áudio TTS base:

- Pitch shift leve (misturado pela intensidade `voice_clone_pitch_strength`)
- Filtro de modelagem espectral (ajuste de brilho/formant simplificado – intensidade `voice_clone_formant_strength`)

Objetivo: aproximar o timbre/altura original sem dependências pesadas enquanto a clonagem neural real não chega.

#### Configuração (variáveis / .env)

| Chave (.env / Settings)                                         | Descrição                                   | Valores / Exemplo                  | Default          |
| --------------------------------------------------------------- | ------------------------------------------- | ---------------------------------- | ---------------- |
| `VOICE_CLONE_ENABLED`                                           | Liga/desliga qualquer tentativa de clonagem | true / false                       | true             |
| `VOICE_CLONE_MODE` (`voice_clone_mode`)                         | Estratégia                                  | baseline                           | baseline         |
|                                                                 |                                             | spectral (pseudo timbre)           |                  |
|                                                                 |                                             | openvoice (quando modelos prontos) |                  |
| `VOICE_CLONE_PITCH_STRENGTH` (`voice_clone_pitch_strength`)     | 0–1 intensidade do ajuste de pitch          | 0.0–1.0                            | 0.7              |
| `VOICE_CLONE_FORMANT_STRENGTH` (`voice_clone_formant_strength`) | 0–1 intensidade de brilho/formant           | 0.0–1.0                            | 0.5              |
| `OPENVOICE_MODELS_DIR`                                          | Pasta de modelos OpenVoice                  | caminho                            | models/openvoice |
| `OPENVOICE_CLI_COMMAND`                                         | Nome do binário CLI                         | openvoice                          | openvoice        |

Exemplo `.env` para modo spectral:

```
VOICE_CLONE_ENABLED=true
VOICE_CLONE_MODE=spectral
VOICE_CLONE_PITCH_STRENGTH=0.6
VOICE_CLONE_FORMANT_STRENGTH=0.4
```

#### Instalação de modelos OpenVoice (quando usar o modo openvoice)

```
python scripts/download_openvoice_models.py
```

Se bloqueado (proxy/SSL), baixe os arquivos `.pt` manualmente e coloque em `models/openvoice`.

#### Fallback & Segurança

- Ausência de modelos/CLI ou erros → fallback automático para TTS nativo
- Erros não interrompem pipeline de dublagem

#### Limitações Atuais

- Modo spectral NÃO preserva exatamente voz (apenas heurística de pitch + brilho)
- Sem alinhamento fonético ou prosódia neural
- OpenVoice ainda não gera áudio real (placeholder)

⚠ Python 3.13+: o pacote `openvoice-cli` (<=0.0.5) depende de componentes (`audioop`) removidos
na stdlib nesta versão. Por isso a detecção neural é desabilitada automaticamente em Python 3.13+
e o sistema recai para `spectral` ou `baseline`. Para testar futura integração neural, use Python 3.12
ou aguarde atualização upstream.

#### Roadmap Próximo

- [ ] Substituir placeholder OpenVoice por pipeline real (encoder + tone color + vocoder)
- [ ] Cache de embeddings / perfis
- [ ] Ajuste dinâmico de duração por segmento (DTW / time-stretch controlado)
- [ ] Parâmetros avançados (pitch target override, preservação de energia)

### �🔮 Roadmap Futuro

- [ ] **Voice Cloning** (OpenVoice, RVC, Coqui TTS)
- [ ] **Tradução melhorada** (Google Translate API, Azure)
- [ ] **Streaming processing** (chunks em tempo real)
- [ ] **Multi-language UI** (i18n)
- [ ] **API keys management** (serviços externos)
- [ ] **Batch processing** (múltiplos arquivos)

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/amazing-feature`
3. Commit suas mudanças: `git commit -m 'Add amazing feature'`
4. Push para a branch: `git push origin feature/amazing-feature`
5. Abra um Pull Request

### Desenvolvimento Local

```bash
# Setup completo
python scripts/bootstrap.py

# Executar com reload
make run

# Testes antes do commit
make test
```

---

**✨ Dubby** - Powered by FastAPI, Faster-Whisper, argostranslate, and pyttsx3

## Uso

1. Acesse a página inicial e envie um arquivo de vídeo/áudio.
2. Escolha idioma de entrada e saída.
3. Aguarde o processamento; baixe o resultado.

## Notas técnicas

- ASR: `faster-whisper` (baixa modelos em `models/`).
- Tradução: `argostranslate` (instala pacotes sob demanda; veja `scripts/bootstrap_models.py`).
- TTS: `app/services/tts.py` implementa fallback (tom senoidal ajustado por segmento). Substitua por OpenVoice/serviço para voz real.
- Mídia: `ffmpeg` para extração/mux.

### Ambientes com proxy/SSL corporativo (erro de certificado Hugging Face)

Se você ver erros como `SSLCertVerificationError` ou "download online está bloqueado" ao baixar modelos do Hugging Face:

- Opção A (recomendada): operar com modelo local.
  1.  Baixe manualmente o repositório do modelo (ex.: Systran/faster-whisper-medium) no diretório `models/`.
  2.  Defina `ASR_MODEL` no `.env` para o caminho local, por exemplo:
      `ASR_MODEL=models/Systran__faster-whisper-medium`
- Opção B: configurar certificados/proxy do ambiente:
  - Defina variáveis `HTTPS_PROXY`/`HTTP_PROXY`.
  - Aponte `REQUESTS_CA_BUNDLE` e/ou `CURL_CA_BUNDLE` para o seu CA corporativo.
  - Reinicie o servidor após ajustar o ambiente.

## Roadmap

- [ ] Clonagem de voz zero-shot (OpenVoice) com suporte multi-idiomas.
- [ ] Alinhamento de fala mais preciso (WhisperX/Aeneas).
- [ ] Fila de jobs e background workers.
- [ ] Melhorar UI e progresso.

## Aviso legal

Garanta que você tem direitos para transcrever, traduzir e clonar a voz do conteúdo processado.
