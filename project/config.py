import os
import pathlib
from functools import lru_cache
from environs import Env

from openai import OpenAI

env = Env()
env.read_env()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    OPENAI_CLIENT = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    ORIGINS = [
        "http://localhost:3000",
    ]
    REPORT_PROMPT = "You are a professional sales assistant. You will be provided with a dialogue between a user and " \
                    "a sales representative. Your task is to evaluate the quality of the salesperson's conversation " \
                    "and provide further recommendations to improve their sales communication skills.\n" \
                    "In your response, you should create a report, highlighting the positive aspects, identifying any" \
                    " negative elements in the conversation, and providing further recommendations. return your answer in Markdown2"


class TestConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> DevelopmentConfig | ProductionConfig | TestConfig:
    config_cls_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestConfig
    }
    config_name = env('FASTAPI_CONFIG', default='production')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
