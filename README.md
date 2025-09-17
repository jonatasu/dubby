# dubby

![CI](https://github.com/jonatasu/dubby/actions/workflows/ci.yml/badge.svg)

Tradução e dublagem de vídeos/áudios via web UI. Pipeline: extração de áudio → transcrição (ASR) → tradução → síntese (voz clonada futura; fallback simples) → remux.

Estado: protótipo funcional com TTS de fallback (tom). Substitua por clonagem de voz (OpenVoice/serviço) quando desejar.

## Requisitos (macOS)

- Homebrew: https://brew.sh
- ffmpeg (via Homebrew)
- Python 3.11+

```zsh
# Dependências de sistema
brew install ffmpeg

# Ambiente Python (recomendado)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Opcional para tradução offline melhor:

```zsh
pip install argostranslate
python scripts/bootstrap_models.py
```

## Executar localmente

```zsh
# Ative o ambiente se ainda não estiver
source .venv/bin/activate

# Rodar o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Abra no navegador: http://localhost:8000

## Docker

```zsh
# Build
docker build -t dubby:local .
# Run
docker run --rm -it -p 8000:8000 -v "$PWD/models:/app/models" -v "$PWD/uploads:/app/uploads" -v "$PWD/outputs:/app/outputs" dubby:local
```

Ou via docker-compose:

```zsh
docker compose up --build
```

## Deploy em Cloud

- Qualquer plataforma que rode contêiner (Railway, Render, Fly.io, etc.).
- Use a imagem gerada pelo Dockerfile. Exponha a porta 8000.
- Opcional: monte volumes persistentes para `models/`, `uploads/` e `outputs/`.
- Variáveis de ambiente: veja `.env.example`.

### PythonAnywhere (WSGI/ASGI)

PythonAnywhere suporta apps ASGI. Passos gerais:

1. Crie um virtualenv com Python 3.11 e instale as dependências do `requirements.txt`.
2. No painel da aplicação web, configure como app ASGI e aponte o módulo `asgi:application` deste projeto (arquivo `asgi.py` na raiz).
3. Static files: mapeie `/static` para `app/static` e `/outputs` para `outputs` se quiser servir downloads direto da plataforma.
4. ffmpeg: se não houver ffmpeg no host, o app mostrará um erro claro. Alternativas:

- Processar apenas áudio (uploads .wav/.mp3 e entregar `*.dubbed.wav`).
- Processar vídeo externamente (local/Docker) e apenas servir os resultados.

5. Modelos offline: rode o script para baixar o modelo e atualizar `.env`:

```bash
python scripts/download_whisper_model.py --model Systran/faster-whisper-medium
```

Isso gravará em `models/` e definirá `ASR_MODEL` no `.env` para o caminho local.

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
