from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TypeVar, Generic, Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, ChatMessagePromptTemplate, \
    BasePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever

TQuery = TypeVar('TQuery', bound=object)


class BaseRagChain(Generic[TQuery], ABC):
    @property
    def output_parser(self) -> BaseOutputParser:
        """
        Returns a default output parser of type StrOutputParser
        :return:
        """

        return StrOutputParser()

    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        """
        example: return llm_factory.get_llm(HuggingFaceModelSettings(
            model_id=engine_settings.hugging_face_model_id,
            max_tokens=engine_settings.hugging_face_max_tokens
        ))
        :return:
        """
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Returns the system prompt template
        :return:
        """
    
    @abstractmethod
    def get_chain_input(self, query: TQuery, session_id: str = None) -> object:
        """
        Returns the chain input
        :param query:
        :param session_id:
        :return:
        """

    @abstractmethod
    def post_processing(self, query: TQuery, response: any, session_id: str = None):
        """
        Post-processes the response
        :param query:
        :param response:
        :param session_id:
        :return:
        """

    def execute(self, retriever: VectorStoreRetriever, format_docs: Callable, query: TQuery, session_id: str = None) -> any:
        llm = self.get_llm()
        prompt = ChatPromptTemplate.from_template(self.get_system_prompt())
        output_parser = self.output_parser
        retriever = retriever
        format_docs = format_docs

        chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm 
                | output_parser
        )

        chain_input = self.get_chain_input(query, session_id)
        response = chain.invoke(chain_input)

        self.post_processing(query, response, session_id)

        return response