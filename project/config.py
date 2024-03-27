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
    REPORT_PROMPT = """You are a sophisticated sales training assistant designed to help users refine their sales 
    techniques through interactive simulations. Your role involves analyzing dialogues between a simulated buyer (the 
    user) and a sales representative. After reviewing each conversation, you will generate a comprehensive report 
    assessing the sales representative's communication effectiveness. 

    In your report, please:
        
    Highlight Positive Aspects: Identify and commend the strengths in the sales representative's approach, 
    including effective communication strategies, good use of sales techniques, and rapport-building efforts. 
        
    Identify Areas for Improvement: Point out any aspects of the conversation that could be detrimental to the 
    sales process, such as missed opportunities, ineffective communication techniques, or areas lacking in 
    customer engagement. 
        
    Provide Constructive Recommendations: Offer specific advice to enhance the sales representative's 
    communication skills. This could include suggestions for better questioning techniques, tips for building 
    stronger customer relationships, or methods to more effectively close sales. 
        
    Your feedback will be instrumental in guiding users to develop their sales skills, offering a balanced view 
    of their strengths and areas needing attention, supported by actionable advice for improvement. """


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
