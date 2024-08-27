import uvicorn
from fastapi import FastAPI

from agent_build_sdk.model.model import AgentReq, AgentResp

from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.utils.logger import logger


class EndpointServer:
    def __init__(self, agent: BasicAgent):
        self.app = FastAPI()
        self.agent = agent

        @self.app.post("/agent/init")
        def init(req: AgentReq) -> AgentResp:
            self.agent.memory.clear()
            return AgentResp(success=True)

        # interact
        @self.app.post("/agent/interact")
        def interact(req: AgentReq) -> AgentResp:
            return self.agent.interact(req)

        # perceive
        @self.app.post("/agent/perceive")
        def perceive(req: AgentReq):
            try:
                self.agent.perceive(req)
                return AgentResp(success=True)
            except Exception as e:
                logger.error(f"invoke perceive error.", e)
                return AgentResp(success=False, errMsg=f"perceive error {e}")

        @self.app.post("/agent/checkHealth")
        def checkHealth(req: AgentReq):
            return AgentResp(success=True)

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=7860)

