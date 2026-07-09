# Movie Video Bot 🎬

Automação que gera um vídeo curto (formato Shorts) sobre um filme ou série
em alta, narra com voz sintética, monta o vídeo e sobe automaticamente no
YouTube.

## Fluxo

```
trending.py  →  script_writer.py  →  tts.py  →  video_builder.py  →  youtube_uploader.py
(TMDB)          (Claude API)         (edge-tts)  (moviepy)            (YouTube API)
```

## Instalação

```bash
cd movie_video_bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

No Linux, o moviepy também precisa do ImageMagick instalado para gerar texto:
```bash
sudo apt install imagemagick
```

## Configuração de chaves

Crie um arquivo `.env` na raiz do projeto:

```
TMDB_API_KEY=sua_chave_tmdb
ANTHROPIC_API_KEY=sua_chave_anthropic
```

- **TMDB**: conta grátis em https://www.themoviedb.org/ → Configurações → API
- **Anthropic**: https://console.anthropic.com/

## Configuração do YouTube (uma vez só)

1. Crie um projeto em https://console.cloud.google.com/
2. Ative a **YouTube Data API v3**
3. Crie uma credencial OAuth 2.0 do tipo "App para computador"
4. Baixe o JSON e salve como `client_secret.json` na raiz do projeto
5. Na primeira execução vai abrir o navegador pra você autorizar — depois
   disso o token fica salvo e você não precisa repetir

⚠️ Enquanto estiver testando, deixe `YOUTUBE_PRIVACY_STATUS = "private"` no
`config.py`, pra não publicar vídeos com bugs publicamente. Troque para
`"public"` quando estiver satisfeito com o resultado.

## Uso

```bash
python main.py
```

Isso vai:
1. Escolher um filme/série em alta no TMDB (evitando repetir os já usados,
   guardados em `assets/history.json`)
2. Gerar o roteiro com Claude
3. Narrar com voz em português (edge-tts, grátis)
4. Montar o vídeo vertical com pôster/imagens do TMDB + efeito de zoom
5. Subir automaticamente pro YouTube como vídeo privado

## Agendando a automação

Pra rodar automaticamente todo dia, use o `cron` (Linux/Mac):

```bash
crontab -e
# roda todo dia às 10h
0 10 * * * cd /caminho/para/movie_video_bot && venv/bin/python main.py >> log.txt 2>&1
```

No Windows, use o Agendador de Tarefas apontando pro `main.py`.

## Personalizações fáceis

- **Formato horizontal em vez de Shorts**: em `config.py`, troque
  `VIDEO_WIDTH = 1920` e `VIDEO_HEIGHT = 1080`.
- **Só filmes ou só séries**: em `main.py`, chame `run(media_type="movie")`
  ou `run(media_type="tv")`.
- **Trocar a voz**: veja vozes disponíveis com
  `edge-tts --list-voices | grep pt-BR` e ajuste `TTS_VOICE` em `config.py`.
- **Não subir automaticamente**: chame `run(upload=False)` pra só gerar o
  vídeo localmente e revisar antes de postar.

## Aviso sobre direitos autorais

O vídeo usa pôsteres e imagens de fundo (backdrops) do TMDB. Isso costuma
ser aceito como uso de comentário/crítica, mas o YouTube pode acionar
Content ID dependendo do estúdio. Se isso acontecer com frequência, troque
as imagens por artes originais/genéricas relacionadas ao gênero do filme
em vez das imagens oficiais.
