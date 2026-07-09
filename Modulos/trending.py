"""
Busca filmes/séries em alta (trending) usando a API do TMDB.
Docs: https://developer.themoviedb.org/reference/trending-all
"""

import random
import requests
from config import TMDB_API_KEY

TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/original"


def get_trending(media_type="all", window="day", language="pt-BR"):
    """
    media_type: 'all' | 'movie' | 'tv'
    window: 'day' | 'week'
    Retorna uma lista de dicts com os itens em alta.
    """
    url = f"{TMDB_BASE}/trending/{media_type}/{window}"
    params = {"api_key": TMDB_API_KEY, "language": language}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("results", [])


def get_details(item_id, media_type, language="pt-BR"):
    """Pega detalhes completos (sinopse, gêneros, elenco, imagens extras)."""
    url = f"{TMDB_BASE}/{media_type}/{item_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "append_to_response": "credits,images",
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def pick_title(media_type="all", window="day", exclude_ids=None):
    """
    Escolhe um título aleatório entre os trending (evita repetir os IDs
    passados em exclude_ids, útil se você guardar um histórico).
    Retorna um dict pronto para uso: title, overview, release_date,
    poster_url, backdrop_urls, genres, media_type, id.
    """
    exclude_ids = exclude_ids or set()
    results = get_trending(media_type=media_type, window=window)
    candidates = [r for r in results if r["id"] not in exclude_ids]
    if not candidates:
        candidates = results
    if not candidates:
        raise RuntimeError("Nenhum título em alta encontrado no TMDB.")

    chosen = random.choice(candidates)
    real_media_type = chosen.get("media_type", media_type if media_type != "all" else "movie")
    details = get_details(chosen["id"], real_media_type)

    title = details.get("title") or details.get("name")
    overview = details.get("overview", "")
    release_date = details.get("release_date") or details.get("first_air_date", "")
    genres = [g["name"] for g in details.get("genres", [])]

    poster_path = details.get("poster_path")
    backdrops = details.get("images", {}).get("backdrops", [])[:5]
    backdrop_paths = [b["file_path"] for b in backdrops] or (
        [details.get("backdrop_path")] if details.get("backdrop_path") else []
    )

    return {
        "id": chosen["id"],
        "media_type": real_media_type,
        "title": title,
        "overview": overview,
        "release_date": release_date,
        "genres": genres,
        "poster_url": f"{IMG_BASE}{poster_path}" if poster_path else None,
        "backdrop_urls": [f"{IMG_BASE}{p}" for p in backdrop_paths],
    }
