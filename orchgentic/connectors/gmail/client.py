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
