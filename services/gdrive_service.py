import io
from typing import Optional

from config.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


def _get_credentials():
    """Build OAuth2 credentials for Google Drive API.

    This uses the installed app flow. For Streamlit Cloud, credentials should
    be configured via st.secrets.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    import os
    import json

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    token_path = "token.json"

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def _find_or_create_folder(service, folder_name: str) -> str:
    """Find a folder by name in Google Drive, or create it."""
    query = (
        f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    # Create the folder
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]


def upload_to_drive(
    csv_bytes: bytes,
    filename: str,
    folder_name: str = "Topic Maps",
) -> Optional[str]:
    """Upload a CSV file to Google Drive and return a shareable link.

    Returns the web view link for the uploaded file, or None on failure.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("Google Drive credentials are not configured.")

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload

    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)

    folder_id = _find_or_create_folder(service, folder_name)

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        resumable=True,
    )

    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    # Make the file accessible to anyone with the link
    service.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return uploaded.get("webViewLink")
