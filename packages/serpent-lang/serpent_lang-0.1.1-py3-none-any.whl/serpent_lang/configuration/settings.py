from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# todo: rework to remove deployment names.  these should be set by the concrete class
class EngineSettings(BaseSettings):
    """
    environment variables required to work with langchain and openAI libraries (openAI, Azure openAI specific)
    """
    azure_openai_api_key: str
    azure_openai_endpoint: str
    openai_api_type: str
    openai_api_version: str
    openai_chat_engine: str
    # azure_embedding_deployment_name: str
    # azure_chat_deployment_name: str
    # azure_cosmosdb_conn_string: str
    # azure_cosmosdb_db_name: str
    # azure_cosmosdb_collection_name: str
    # azure_cosmosdb_index_name: str
    


engine_settings = EngineSettings()
