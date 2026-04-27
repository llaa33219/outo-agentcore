from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from outo_agentcore.core.message import Message
from outo_agentcore.core.context import Context, ToolCall
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.tool import ToolResult
from outo_agentcore.core.router import CALL_AGENT, FINISH, RoutingError

if TYPE_CHECKING:
    from outo_agentcore.core.router import Router

_FINISH_NUDGE = (
    "[SYSTEM] Your plain text response was NOT delivered to the caller. "
    "You MUST use the finish tool to return results. "
    'Call finish(message="your result") now.'
)

@dataclass
class RunResult:
    output: str
    messages: list[Message] = field(default_factory=list)

class Runtime:
    def __init__(self, router: Router):
        self._router = router
        self._messages: list[Message] = []
    
    async def execute(self, forward_message: str, agent: Agent) -> RunResult:
        call_id = uuid.uuid4().hex
        self._messages.append(Message(
            type="forward", sender="user", receiver=agent.name,
            content=forward_message, call_id=call_id
        ))
        output = await self._run_agent_loop(agent, forward_message, call_id, caller="user")
        self._messages.append(Message(
            type="return", sender=agent.name, receiver="user",
            content=output, call_id=call_id
        ))
        return RunResult(output=output, messages=list(self._messages))
    
    async def _run_agent_loop(
        self, agent: Agent, forward_message: str, call_id: str,
        caller: str | None = None
    ) -> str:
        system_prompt = self._router.build_system_prompt(agent, caller=caller)
        context = Context(system_prompt)
        context.add_user(forward_message)
        tool_schemas = self._router.build_tool_schemas(agent.name)
        
        while True:
            response = await self._router.call_llm(agent, context, tool_schemas)
            
            if not response.tool_calls:
                context.add_assistant_text(response.content or "")
                context.add_user(_FINISH_NUDGE)
                continue
            
            finish_call = _find_finish(response.tool_calls)
            if finish_call is not None:
                return finish_call.arguments.get("message", "")
            
            context.add_assistant_tool_calls(response.tool_calls, response.content)
            for tc in response.tool_calls:
                result = await self._execute_tool_call(tc, agent.name, call_id)
                context.add_tool_result(tc.id, tc.name, str(result))
    
    async def _execute_tool_call(
        self, tc: ToolCall, caller_name: str, caller_call_id: str
    ) -> str:
        if tc.name == CALL_AGENT:
            agent_name = tc.arguments.get("agent_name", "")
            message = tc.arguments.get("message", "")
            target = self._router.get_agent(agent_name)
            sub_call_id = uuid.uuid4().hex
            
            self._messages.append(Message(
                type="forward", sender=caller_name, receiver=agent_name,
                content=message, call_id=sub_call_id
            ))
            result = await self._run_agent_loop(
                target, message, sub_call_id, caller=caller_name
            )
            self._messages.append(Message(
                type="return", sender=agent_name, receiver=caller_name,
                content=result, call_id=sub_call_id
            ))
            return f"[{agent_name}]{result}[/{agent_name}]"
        
        tool = self._router.get_tool(tc.name)
        tool_result = await tool.execute(**tc.arguments)
        return tool_result.content if isinstance(tool_result, ToolResult) else str(tool_result)

def _find_finish(tool_calls: list[ToolCall]) -> ToolCall | None:
    for tc in tool_calls:
        if tc.name == FINISH:
            return tc
    return None
