"""
Converte o roteiro em áudio narrado usando edge-tts (gratuito, vozes da
Microsoft, boa qualidade em pt-BR). Não requer chave de API.
"""

import asyncio
import edge_tts
from config import TTS_VOICE


async def _synthesize(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_audio(text, output_path="assets/narration.mp3", voice=None):
    """Gera o arquivo de áudio e retorna o caminho do arquivo."""
    voice = voice or TTS_VOICE
    asyncio.run(_synthesize(text, output_path, voice))
    return output_path
