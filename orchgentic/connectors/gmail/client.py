from email.message import EmailMessage
import base64
from googleapiclient.discovery import build
from orchgentic.connectors.gmail.oauth import load_credentials
def gmail_service(connection="default"):
    return build("gmail","v1",credentials=load_credentials(connection))
def search_messages(connection, query, max_results=10):
    return gmail_service(connection).users().messages().list(userId="me",q=query,maxResults=max_results).execute().get("messages",[])
def read_message(connection, message_id):
    return gmail_service(connection).users().messages().get(userId="me",id=message_id,format="full").execute()
def create_draft(connection,to,subject,body):
    msg=EmailMessage(); msg.set_content(body); msg["To"]=to; msg["Subject"]=subject
    raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return gmail_service(connection).users().drafts().create(userId="me",body={"message":{"raw":raw}}).execute()
def extract_headers(message):
    values={}
    for h in (message.get("payload",{}) or {}).get("headers",[]) or []:
        n=h.get("name","").lower()
        if n in {"from","to","subject","date"}: values[n]=h.get("value")
    return values


def send_message(connection: str, to: str, subject: str, body: str) -> dict:
    service = gmail_service(connection)
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": encoded}).execute()

def reply_message(connection: str, message_id: str, body: str) -> dict:
    service = gmail_service(connection)
    original = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["From", "Subject"],
    ).execute()
    headers = extract_headers(original)
    to_addr = headers.get("from")
    subject = headers.get("subject") or ""
    if subject and not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    email = EmailMessage()
    email.set_content(body)
    email["To"] = to_addr
    email["Subject"] = subject
    encoded = base64.urlsafe_b64encode(email.as_bytes()).decode()
    return service.users().messages().send(
        userId="me",
        body={"raw": encoded, "threadId": original.get("threadId")},
    ).execute()

def trash_message(connection: str, message_id: str) -> dict:
    service = gmail_service(connection)
    return service.users().messages().trash(userId="me", id=message_id).execute()
