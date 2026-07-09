"""
Configurações centrais do bot.
Preencha as variáveis abaixo ou crie um arquivo .env na raiz do projeto
com as mesmas chaves (recomendado para não deixar segredo no código).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- TMDB (The Movie Database) ---
# Crie uma conta gratuita em https://www.themoviedb.org/ e gere uma API Key
# em Configurações > API.
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "SUA_TMDB_API_KEY_AQUI")

# --- Anthropic (Claude) ---
# Gere sua chave em https://console.anthropic.com/
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "SUA_ANTHROPIC_API_KEY_AQUI")
CLAUDE_MODEL = "claude-sonnet-4-6"

# --- Narração (TTS) ---
# Voz do edge-tts em português do Brasil. Para ver outras vozes disponíveis,
# rode no terminal: edge-tts --list-voices | grep pt-BR
TTS_VOICE = "pt-BR-AntonioNeural"

# --- YouTube ---
# Baixe o arquivo client_secret.json no Google Cloud Console
# (APIs & Serviços > Credenciais > Criar credenciais > ID do cliente OAuth)
# e coloque na raiz do projeto com esse nome.
YOUTUBE_CLIENT_SECRETS_FILE = "client_secret.json"
YOUTUBE_TOKEN_FILE = "youtube_token.json"
YOUTUBE_CATEGORY_ID = "24"  # 24 = Entertainment
YOUTUBE_PRIVACY_STATUS = "private"  # troque para "public" quando confiar no fluxo

# --- Vídeo ---
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # formato vertical (Shorts). Use 1920x1080 para vídeo horizontal.
VIDEO_FPS = 30
OUTPUT_DIR = "assets"
