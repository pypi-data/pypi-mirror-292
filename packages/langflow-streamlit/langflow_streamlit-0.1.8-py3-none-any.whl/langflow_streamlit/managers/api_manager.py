from langflow_streamlit.utils.process_utils import check_if_port_is_used_by_program, kill_process_on_port
from langflow_streamlit.utils import settings, LOGGER
import multiprocessing


class APIManager:
    port = settings.API_PORT

    @classmethod
    def run_streamlit_api(cls):
        try:
            from fastapi import FastAPI
            from langflow_streamlit.api import router
            from langflow_streamlit.utils import settings
            from asyncio import new_event_loop
            import uvicorn

            loop = new_event_loop()
            app = FastAPI()
            app.include_router(router, prefix="/api/v1")

            @app.get("/health")
            async def health():
                pass

            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=cls.port,
                workers=1,
                log_level="error",
                reload=False,
                loop="asyncio",
            )
            loop.create_task(uvicorn.Server(config=config).serve())
            loop.run_forever()
        except KeyboardInterrupt:
            LOGGER.info("Shutting down streamlit api")
        except BaseException as err:
            LOGGER.error(f"Unexpected shutdown of streamlit api. err: {err}")

    @classmethod
    def start(cls, args=""):
        if check_if_port_is_used_by_program(cls.port, ["python"]):
            kill_process_on_port(cls.port)
        process = multiprocessing.Process(target=cls.run_streamlit_api)
        process.start()
        return process
