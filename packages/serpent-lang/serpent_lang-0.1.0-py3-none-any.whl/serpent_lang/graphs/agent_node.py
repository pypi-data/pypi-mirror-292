from langchain_core.messages import HumanMessage
from langchain_core.runnables.base import RunnableLike

from serpent_lang.agents.base_agent import BaseAgent


class AgentNode:
    def __init__(self, agent: BaseAgent):
        self.agent = agent

    @property
    def name(self):
        return self.agent.get_agent_name()

    def create_action(self, query, session_id, filters) -> RunnableLike:
        # todo: type state
        def action(state: any):
            result = self.agent.execute(query=query, session_id=session_id, filters=filters, state=state)

            return {
                "messages": [HumanMessage(content=result, name=self.name)]
            }

        return action
