We built webhook testing around the trigger system.

There are two ways to test it:

1. Test the trigger without running the web server

This manually dispatches the trigger through Orchgentic:

orch trigger run order_webhook --debug

That uses the trigger YAML in:

triggers/order_webhook.yaml

Current example shape:

trigger:
  id: order_webhook
  type: webhook
  target_agent: Bob
  enabled: true
  path: /webhooks/orders
  task: |
    Review this incoming webhook event and summarize what action is needed.

This is useful for confirming the trigger can load, target Bob, and dispatch correctly.

2. Test the actual webhook HTTP endpoint

Start the webhook server:

orch serve-webhooks

By default it runs on:

http://127.0.0.1:8000

Health check:

curl http://127.0.0.1:8000/health

Expected:

{"ok":true}

Then send a test webhook payload to the path defined in the trigger YAML:

curl -X POST http://127.0.0.1:8000/webhooks/orders ^
  -H "Content-Type: application/json" ^
  -d "{\"order_id\":\"12345\",\"customer\":\"Test Customer\",\"status\":\"new\"}"

In Git Bash, use:

curl -X POST http://127.0.0.1:8000/webhooks/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id":"12345","customer":"Test Customer","status":"new"}'

Expected response shape:

{
  "ok": true,
  "results": [
    {
      "trigger_id": "order_webhook",
      "result": "..."
    }
  ]
}

If the path does not match any enabled webhook trigger, you should get a 404 like:

No webhook trigger configured for /wrong/path

So the quick test loop is:

orch serve-webhooks
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/webhooks/orders -H "Content-Type: application/json" -d '{"test":true}'

The key is that the webhook path must match the trigger YAML exactly:

path: /webhooks/orders