import logging
from abc import ABC, abstractmethod

from langchain_core.prompts import PromptTemplate, BasePromptTemplate
from pydantic import BaseModel
from typing_extensions import Any

from serpent_lang.chains.base_chat_chain import BaseChain

_logger = logging.getLogger(__name__)


class BaseMessageChain(BaseChain[str], ABC):
    def get_system_prompt(self) -> str:
        pass

    def get_chain_input(self, query: str, session_id: str = None, additional_filters: dict[str, any] = None) -> dict[str, Any]:
        return {"input": query}

    def build_prompt_template(self, query: str, session_id: str) -> BasePromptTemplate:
        prompt_template = PromptTemplate(
            template=query
        )

        return prompt_template
