from langflow_streamlit.utils.process_utils import check_if_port_is_used_by_program, kill_process_on_port
from langflow_streamlit.utils import settings, LOGGER
from subprocess import run, PIPE
import multiprocessing
import os


class StreamlitManager:
    port = settings.STREAMLIT_PORT
    path = settings.FOLDER_PATH

    @classmethod
    def __load_streamlit(cls):
        if not os.path.exists(f"{cls.path}streamlit.py"):
            with open(f"{cls.path}streamlit.py", "w") as file:
                file.write("import streamlit as st")
        else:
            with open(f"{cls.path}streamlit.py", "r+") as file:
                content = file.read()
                if len(content) < 10:
                    file.seek(0)
                    file.write("import streamlit as st\nfrom time import sleep\nwhile True:\n    sleep(2)")
                    file.truncate()

    @classmethod
    def ignore_email(cls):
        import os
        from os.path import exists, isfile, expanduser

        streamlit_config_path = expanduser("~")+ "/.streamlit"
        if not exists(streamlit_config_path):
            os.makedirs(streamlit_config_path)
        if not isfile(streamlit_config_path+"/credentials.toml"):
            with open(streamlit_config_path+"/credentials.toml", "w") as f:
                f.write('[general]\nemail = ""')

    @classmethod
    def run_streamlit(cls, args):
        try:
            cls.ignore_email()
            exec_result = run(
                f"streamlit run {cls.path}streamlit.py --browser.serverPort {cls.port} --server.port {cls.port} {args}",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            )
            if exec_result.returncode != 0:
                LOGGER.error(f"Streamlit startup failed. stderr: {exec_result.stderr} stdout: {exec_result.stdout}")
        except KeyboardInterrupt:
            LOGGER.info("Shutting down streamlit")

    @classmethod
    def start(cls, args="--server.headless false"):
        if check_if_port_is_used_by_program(cls.port, ["streamlit"]):
            kill_process_on_port(cls.port)
        cls.__load_streamlit()
        process = multiprocessing.Process(target=cls.run_streamlit, args=(args,))
        process.start()
        return process

    @classmethod
    def restart(cls):
        kill_process_on_port(cls.port)
        cls.start("--server.headless true")
