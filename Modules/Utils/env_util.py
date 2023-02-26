import os

from dotenv import load_dotenv


def get_base_folder() -> str:
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_log_folder() -> str:
    log_folder = os.path.join(get_base_folder(), 'Logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    return log_folder


def is_docker() -> bool:
    return os.path.exists('/.dockerenv')


def load_env(env_file: str = '.env.local') -> None:
    file = os.path.join(os.path.dirname(get_base_folder()), env_file)
    load_dotenv(dotenv_path=file)
