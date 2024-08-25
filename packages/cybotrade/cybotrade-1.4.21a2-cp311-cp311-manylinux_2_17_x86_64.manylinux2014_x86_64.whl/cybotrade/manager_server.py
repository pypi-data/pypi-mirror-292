import logging
import json
from aiohttp import web
from cybotrade.models import OrderSide
from cybotrade.runtime import StrategyTrader

class ManagerServer():
    strategy_trader: StrategyTrader | None = None

    def __init__(self, manager, logger: logging.Logger):
        self.manager = manager 
        self.logger = logger

    async def start(self):
        app = web.Application()
        async def on_shutdown(app):
            self.manager.on_shutdown()
        app.on_shutdown.append(on_shutdown)
        app.add_routes([web.post('/', self.on_signal())])
        logging.info("Starting ManagerServer")
        await web._run_app(app, port=8001, access_log=self.logger)


    def on_signal(self):
        async def handler(req: web.Request) -> web.StreamResponse:
            param_body = await req.text()
            try:
                signal_table = json.loads(param_body)
                signal = OrderSide.Buy
                if signal_table["side"] == "sell":
                    signal = OrderSide.Sell

                await self.manager.on_signal(id=signal_table["id"], signal=signal) 
                resp = web.Response()  
                resp.set_status(200)
                return resp
            except Exception as e:
                logging.error(f"Received invalid signal message: {param_body}: {e}");
                resp = web.Response()
                resp.set_status(400)
                return resp
                
        return handler
