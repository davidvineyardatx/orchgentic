from fastapi import FastAPI, Request, HTTPException
from orchgentic.config.loader import load_all_triggers
from orchgentic.triggers.models import TriggerEvent
from orchgentic.triggers.dispatcher import TriggerDispatcher

def create_webhook_app():
    app = FastAPI(title="Orchgentic Webhook Server")
    dispatcher = TriggerDispatcher()

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.post("/{full_path:path}")
    async def receive(full_path: str, request: Request):
        path = "/" + full_path
        body = await request.json()
        matches = [t for t in load_all_triggers("triggers") if t.enabled and t.type == "webhook" and t.path == path]
        if not matches:
            raise HTTPException(status_code=404, detail=f"No webhook trigger configured for {path}")
        results = []
        for t in matches:
            event = TriggerEvent(t.id, t.type, t.target_agent, t.task, {"webhook_path": path, "body": body})
            results.append({"trigger_id": t.id, "result": await dispatcher.dispatch(event)})
        return {"ok": True, "results": results}

    return app
