"""
Automação: gera um vídeo curto sobre um filme/série em alta e sobe no YouTube.

Uso:
    python main.py
"""

import os
import json
from datetime import datetime

from modules import trending, script_writer, tts, video_builder, youtube_uploader

HISTORY_FILE = "assets/history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_history(history):
    os.makedirs("assets", exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)


def run(upload=True, media_type="all", window="day"):
    print("1/5 - Buscando título em alta...")
    history = load_history()
    movie_info = trending.pick_title(media_type=media_type, window=window, exclude_ids=history)
    print(f"   -> Escolhido: {movie_info['title']} ({movie_info['media_type']})")

    print("2/5 - Gerando roteiro com Claude...")
    script = script_writer.generate_script(movie_info)
    print(f"   -> Hook: {script['hook']}")

    print("3/5 - Gerando narração (TTS)...")
    audio_path = tts.generate_audio(script["narration"])

    print("4/5 - Montando o vídeo...")
    video_path = video_builder.build_video(movie_info, script, audio_path)
    print(f"   -> Vídeo salvo em: {video_path}")

    if upload:
        print("5/5 - Enviando para o YouTube...")
        description = (
            f"{script['narration']}\n\n"
            f"{' '.join(script['hashtags'])}\n\n"
            f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y')}."
        )
        video_id = youtube_uploader.upload_video(
            video_path=video_path,
            title=script["title_card"] + f" | {movie_info['title']}",
            description=description,
            tags=[movie_info["title"]] + movie_info.get("genres", []),
        )
        print(f"   -> Publicado: https://youtube.com/shorts/{video_id}")
    else:
        print("5/5 - Upload desativado (upload=False). Vídeo ficou salvo localmente.")

    history.add(movie_info["id"])
    save_history(history)

    print("Concluído!")


if __name__ == "__main__":
    run(upload=True)
