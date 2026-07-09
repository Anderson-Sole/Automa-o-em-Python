"""
Monta o vídeo final: baixa as imagens do filme/série, aplica um efeito de
zoom lento (Ken Burns), sobrepõe título e legenda, e sincroniza com o áudio
da narração.
"""

import os
import requests
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
)

from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR


def _download_image(url, path):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return path


def _ken_burns_clip(image_path, duration, zoom_start=1.0, zoom_end=1.15):
    """Cria um clipe com zoom lento sobre a imagem, cortado para o formato do vídeo."""
    clip = ImageClip(image_path)

    # redimensiona para preencher o frame mantendo proporção, depois centraliza
    clip = clip.resize(height=VIDEO_HEIGHT * 1.2)
    if clip.w < VIDEO_WIDTH:
        clip = clip.resize(width=VIDEO_WIDTH * 1.2)

    def zoom(t):
        progress = t / duration
        return zoom_start + (zoom_end - zoom_start) * progress

    clip = clip.resize(zoom).set_duration(duration)
    clip = clip.set_position(("center", "center"))
    return clip


def build_video(movie_info, script, audio_path, output_path="assets/final_video.mp4"):
    """
    movie_info: dict de trending.pick_title()
    script: dict de script_writer.generate_script()
    audio_path: caminho do mp3 gerado pelo tts
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # baixa imagens (pôster + backdrops), usa o que tiver disponível
    image_urls = [u for u in ([movie_info.get("poster_url")] + movie_info.get("backdrop_urls", [])) if u]
    if not image_urls:
        raise RuntimeError("Nenhuma imagem disponível para montar o vídeo.")

    image_paths = []
    for i, url in enumerate(image_urls[:4]):  # até 4 imagens no slideshow
        path = os.path.join(OUTPUT_DIR, f"img_{i}.jpg")
        image_paths.append(_download_image(url, path))

    per_image_duration = total_duration / len(image_paths)
    clips = [_ken_burns_clip(p, per_image_duration) for p in image_paths]
    background = concatenate_videoclips(clips, method="compose").set_fps(VIDEO_FPS)
    background = background.crop(
        x_center=background.w / 2,
        y_center=background.h / 2,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
    )

    # título fixo no topo
    title_clip = (
        TextClip(
            script["title_card"],
            fontsize=70,
            color="white",
            font="DejaVu-Sans-Bold",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(VIDEO_WIDTH - 100, None),
        )
        .set_position(("center", 100))
        .set_duration(total_duration)
    )

    # legenda com o hook nos primeiros segundos
    hook_clip = (
        TextClip(
            script["hook"],
            fontsize=55,
            color="yellow",
            font="DejaVu-Sans-Bold",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(VIDEO_WIDTH - 150, None),
        )
        .set_position(("center", "center"))
        .set_duration(min(4, total_duration))
    )

    final = CompositeVideoClip(
        [background, title_clip, hook_clip], size=(VIDEO_WIDTH, VIDEO_HEIGHT)
    ).set_audio(audio)

    final.write_videofile(
        output_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", threads=4
    )

    return output_path
