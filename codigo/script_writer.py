"""
Gera o roteiro de narração para o vídeo curto, usando a API da Anthropic.
"""

import json
import requests
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def generate_script(movie_info, duration_seconds=45):
    """
    movie_info: dict retornado por trending.pick_title()
    Retorna um dict: {"hook": str, "narration": str, "title_card": str, "hashtags": [str]}
    """
    title = movie_info["title"]
    overview = movie_info["overview"]
    genres = ", ".join(movie_info.get("genres", []))
    media_type = "filme" if movie_info["media_type"] == "movie" else "série"

    system_prompt = (
        "Você escreve roteiros curtos e envolventes para vídeos verticais de YouTube "
        "(Shorts) sobre filmes e séries, em português do Brasil. O tom é empolgado, "
        "direto, sem spoilers pesados, pensado para prender atenção nos 3 primeiros "
        "segundos. NUNCA copie texto de sinopses ou reviews existentes: escreva sempre "
        "com suas próprias palavras. Responda SOMENTE em JSON válido, sem markdown, "
        "sem texto antes ou depois."
    )

    user_prompt = f"""
Crie o roteiro de um vídeo curto (~{duration_seconds} segundos de narração, aprox. 110-130 palavras)
sobre o(a) {media_type} "{title}".

Gêneros: {genres or "não informado"}
Sinopse oficial (use só como referência de fatos, não copie frases): {overview or "não disponível"}

Responda em JSON com este formato exato:
{{
  "hook": "frase de abertura de até 12 palavras para prender atenção",
  "narration": "roteiro completo de narração, incluindo o hook, em um único parágrafo fluido",
  "title_card": "título curto para aparecer na tela (até 6 palavras)",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"]
}}
"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    resp = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()

    # remove possíveis cercas de código (```json ... ```)
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
