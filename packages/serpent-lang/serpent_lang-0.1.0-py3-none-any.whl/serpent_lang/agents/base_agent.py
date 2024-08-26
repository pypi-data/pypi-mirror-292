import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from langchain.agents import Tool, AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, \
    MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable

from serpent_lang.core.base_chat_model_action import BaseChatModelAction

_logger = logging.getLogger(__name__)


class BaseAgent(BaseChatModelAction, ABC):
    @abstractmethod
    def get_agent_name(self) -> str:
        """
        The name of the agent.
        :return: the name of the agent as a string
        """

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """"""

    def get_tool_names(self) -> list[str]:
        return [tool.name for tool in self.get_tools()]
    
    def build_system_prompt_template(self) -> SystemMessagePromptTemplate:
        system_prompt = self.get_system_prompt()
        tool_names = self.get_tool_names()
        return SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=["input", "intermediate_steps", tool_names, "agent_scratchpad", "tools"], template=system_prompt))

    def build_prompt_template(self) -> ChatPromptTemplate:
        system_prompt_template = self.build_system_prompt_template()

        prompt_template = ChatPromptTemplate.from_messages([
            system_prompt_template,
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=["input"], template="{input}")),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        return prompt_template

    def build_agent(self, llm: BaseChatModel, tools: list[Tool], prompt_template: ChatPromptTemplate,
                    **kwargs) -> Runnable:
        """
        This method provides an optional means to override the default agent.
        The default agent is `tool_calling_agent` that is invoked with `create_tool_calling_agent()`
        Example:
            agent = create_tool_calling_agent(llm, tools, prompt_template)
            return agent

        :param llm: The model used by the agent.
        :param tools: The list of tools available to the agent.
        :param prompt_template: A ChatPromptTemplate to use as the prompt.
        :param kwargs: Additional keyword arguments to be passed to the create_react_agent function.
        :return: A Langchain Runnable (agent in this case) to be used with an AgentExecutor.
        """
        agent = create_tool_calling_agent(llm, tools, prompt_template, **kwargs)
        return agent

    def build_executor_input(self, query: str, session_id: str = None, filters: dict[str, any] = None) -> dict[str, any]:
        """
        This method provides an optional means to override the default object passed to the AgentExecutor invocation.
        :return: the object to be passed to the AgentExecutor invocation.
        """

        return {
            "input": query,
            "tool_names": self.get_tool_names(),
            "tools": self.get_tools(),
        }

    # todo: figure out how to use langchain parsers with agent to parse the final response only
    def parse_output(self, content: str) -> str:
        """
        This method provides an optional means to parse the final string response of the agent
        :param content: the final response output of the agent
        :return:
        """

        return content

    def execute(self, query: str, session_id: str = None, filters: dict[str, any] = None, state=None):
        start_time = datetime.now(timezone.utc)
        tools = self.get_tools()
        prompt_template = self.build_prompt_template()
        llm = self.get_llm()

        agent = self.build_agent(llm, tools, prompt_template)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )

        input_arg = self.build_executor_input(query, session_id, filters)
        response = agent_executor(input_arg)

        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).seconds
        logging.info(f"Finished processing field query request at {end_time} in {execution_time} seconds.")

        ai_message = f"{response['output']}"
        result = self.parse_output(ai_message)

        return result
