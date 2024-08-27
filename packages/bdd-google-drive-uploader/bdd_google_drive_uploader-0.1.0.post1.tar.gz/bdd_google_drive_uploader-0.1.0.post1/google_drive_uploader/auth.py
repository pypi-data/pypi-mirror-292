# google_drive_uploader/auth.py
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]


class AuthManager:
    def __init__(
        self, credentials_json="credentials.json", credentials_pickle="token.pickle"
    ):
        self.credentials_json = credentials_json
        self.credentials_pickle = credentials_pickle
        self.creds = self.get_creds()

    def get_creds(self):
        """取得 Google Drive API 憑證"""
        creds = None
        if os.path.exists(self.credentials_pickle):
            with open(self.credentials_pickle, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_json, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.credentials_pickle, "wb") as token:
                pickle.dump(creds, token)
        return creds
