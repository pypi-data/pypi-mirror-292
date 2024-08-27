from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import BasePromptTemplate

from serpent_lang.core.base_chat_model_action import BaseChatModelAction

TQuery = TypeVar('TQuery', bound=object)


class BaseChain(Generic[TQuery], BaseChatModelAction, ABC):
    @property
    def output_parser(self) -> BaseOutputParser:
        """
        Returns a default output parser of type StrOutputParser
        :return:
        """

        return StrOutputParser()


    @abstractmethod
    def build_prompt_template(self, query: TQuery, session_id: str) -> BasePromptTemplate:
        """"""

    @abstractmethod
    def get_chain_input(self, query: TQuery, session_id: str = None) -> object:
        """"""

    def post_processing(self, query: TQuery, response: any, session_id: str = None):
        return None

    def execute(self, query: TQuery, session_id: str = None) -> any:
        llm = self.get_llm()
        prompt_template = self.build_prompt_template(session_id=session_id, query=query)
        output_parser = self.output_parser

        chain = prompt_template | llm | output_parser

        chain_input = self.get_chain_input(query, session_id)
        response = chain.invoke(chain_input)

        self.post_processing(query, response, session_id)

        return response
