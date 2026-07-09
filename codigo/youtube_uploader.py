"""
Faz upload do vídeo para o YouTube via API oficial (YouTube Data API v3).

Configuração necessária (uma única vez):
1. Crie um projeto em https://console.cloud.google.com/
2. Ative a "YouTube Data API v3"
3. Crie uma credencial OAuth 2.0 (tipo "App para desktop")
4. Baixe o JSON e salve como client_secret.json na raiz do projeto
5. Na primeira execução, uma janela do navegador vai abrir pra você
   autorizar o acesso à sua conta do YouTube (o token fica salvo em
   youtube_token.json para as próximas execuções).
"""

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import (
    YOUTUBE_CLIENT_SECRETS_FILE,
    YOUTUBE_TOKEN_FILE,
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PRIVACY_STATUS,
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_credentials():
    creds = None
    if os.path.exists(YOUTUBE_TOKEN_FILE):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(
            YOUTUBE_TOKEN_FILE, SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(YOUTUBE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def upload_video(video_path, title, description, tags=None, thumbnail_path=None):
    """Sobe o vídeo e retorna o ID dele no YouTube."""
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": YOUTUBE_CATEGORY_ID,
        },
        "status": {"privacyStatus": YOUTUBE_PRIVACY_STATUS, "selfDeclaredMadeForKids": False},
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload: {int(status.progress() * 100)}%")

    video_id = response["id"]

    if thumbnail_path and os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(thumbnail_path)
        ).execute()

    return video_id
