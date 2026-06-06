import asyncio
from orchgentic.triggers.models import TriggerEvent
from orchgentic.triggers.dispatcher import TriggerDispatcher

class HeartbeatTriggerRunner:
    def __init__(self, trigger_config, dispatcher=None):
        self.config = trigger_config
        self.dispatcher = dispatcher or TriggerDispatcher()

    async def run_once(self, debug=False):
        event = TriggerEvent(
            self.config.id,
            self.config.type,
            self.config.target_agent,
            self.config.task,
            {"source": "heartbeat", "interval_seconds": self.config.interval_seconds}
        )
        return await self.dispatcher.dispatch(event, debug=debug)

    async def run_forever(self, debug=False):
        while True:
            print(await self.run_once(debug=debug))
            await asyncio.sleep(self.config.interval_seconds)
