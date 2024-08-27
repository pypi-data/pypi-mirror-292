
from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.server.server import EndpointServer



class AgentBuilder:

    def __init__(self, name: str, code: str,agent: BasicAgent, mock: bool = False):
        self.name = name
        self.code = code
        self.agent = agent
        self.mock = mock

    def start(self):
        server = EndpointServer(self.agent)
        server.start()
