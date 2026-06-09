from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from orchgentic.connectors.gmail.scopes import GMAIL_SCOPES
from orchgentic.connectors.gmail.storage import token_path, credentials_path, save_account
class GmailConnectionError(Exception): pass
def ensure_credentials_file(name, credentials_file=None):
    dest=credentials_path(name)
    if credentials_file:
        src=Path(credentials_file)
        if not src.exists(): raise GmailConnectionError(f"Credentials file not found: {credentials_file}")
        dest.write_text(src.read_text(encoding="utf-8"),encoding="utf-8")
    if not dest.exists():
        raise GmailConnectionError(f"Missing Gmail OAuth credentials. Run: orch connect gmail --name {name} --credentials path/to/credentials.json")
    return dest
def load_credentials(name="default"):
    p=token_path(name)
    if not p.exists(): raise GmailConnectionError(f"Gmail connection '{name}' is not connected. Run: orch connect gmail --name {name}")
    creds=Credentials.from_authorized_user_file(str(p),GMAIL_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request()); p.write_text(creds.to_json(),encoding="utf-8")
    if not creds or not creds.valid: raise GmailConnectionError(f"Gmail connection '{name}' is invalid. Reconnect with: orch connect gmail --name {name}")
    return creds
def connect_gmail(name="default", credentials_file=None):
    cf=ensure_credentials_file(name,credentials_file)
    flow=InstalledAppFlow.from_client_secrets_file(str(cf),GMAIL_SCOPES)
    creds=flow.run_local_server(port=0)
    token_path(name).write_text(creds.to_json(),encoding="utf-8")
    email=None
    try:
        from googleapiclient.discovery import build
        service=build("gmail","v1",credentials=creds)
        email=service.users().getProfile(userId="me").execute().get("emailAddress")
    except Exception: pass
    save_account(name,email,GMAIL_SCOPES)
    return {"name":name,"email":email,"scopes":GMAIL_SCOPES}
