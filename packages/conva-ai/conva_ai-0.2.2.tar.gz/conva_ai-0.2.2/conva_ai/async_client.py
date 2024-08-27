import uuid
import httpx
import json
from conva_ai.base import BaseClient
from conva_ai.response import ConvaAIResponse
from typing import AsyncGenerator, Any
from conva_ai.context import ConversationContext
from requests.models import Response


class AsyncConvaAI(BaseClient):
    def __init__(
        self, assistant_id: str, assistant_version: str, api_key: str, host: str = "https://infer-v2.conva.ai"
    ):
        super().__init__(assistant_id, assistant_version, api_key, host)
        self.async_client = httpx.AsyncClient()

    async def astream_response(self, response: httpx.Response) -> AsyncGenerator[ConvaAIResponse, Any]:
        async for event_data in response.aiter_text():
            if event_data.startswith("data: "):
                event_data = event_data[len(b"data: ") :].strip()
            event_response = json.loads(event_data)
            rt = event_response.get("response_type", "assistant")
            if rt != "status":
                is_final = event_response.get("is_final", False)
                yield ConvaAIResponse(**event_response)
                if is_final:
                    action_response = ConvaAIResponse(**event_response)
                    yield action_response

    async def send_text2action_request_async(
        self,
        query: str,
        app_context: dict,
        *,
        stream: bool,
        capability_name: str = "",
        capability_group: str = "",
        disable_cache: bool = False,
        history: str = "{}",
        capability_context: dict[str, Any] = {},
    ) -> httpx.Response:
        request_id = uuid.uuid4().hex
        conversation_context = ConversationContext(
            assistant_context=self.assistant_context,
            capability_context=capability_context,
            conversation_history=history,
        )
        request = self.async_client.build_request(
            "POST",
            url=f"{self.host}/v1/assistants/{self.assistant_id}/text2action",
            json={
                "type": "text2action",
                "request_id": request_id,
                "assistant_id": self.assistant_id,
                "assistant_version": self.assistant_version,
                "device_id": str(uuid.getnode()),
                "input_query": query,
                "domain_name": self.domain,
                "app_context": app_context,
                "conversation_history": history,
                "capability_name": capability_name if capability_name else "",
                "capability_group": capability_group if capability_group else "",
                "disable_cache": disable_cache,
                "stream": stream,
                "conversation_context": conversation_context.model_dump(),
            },
            timeout=30,
            headers={"Authorization": self.api_key, "Content-Type": "application/json"},
        )
        response = await self.async_client.send(request, stream=stream)
        return response

    async def handle_error(self, response: Response):
        try:
            message = json.loads(response.content)
            raise Exception(message["detail"])
        except Exception:
            raise Exception(response.content)

    async def invoke_capability(
        self,
        query: str,
        capability_group: str = "",
        history="{}",
        disable_cache: bool = False,
        stream=False,
        capability_context: dict[str, Any] = {},
    ) -> ConvaAIResponse | AsyncGenerator[ConvaAIResponse, Any]:
        app_context: dict = {}
        response = await self.send_text2action_request_async(
            query,
            app_context,
            capability_group=capability_group,
            disable_cache=disable_cache,
            stream=stream,
            history=history,
            capability_context=capability_context,
        )
        if response.status_code != 200:
            await self.handle_error(response)
        if stream:
            return self.astream_response(response)
        else:
            action_response = ConvaAIResponse(**response.json())
            return action_response

    async def invoke_capability_name(
        self,
        query: str,
        capability_name: str,
        history="{}",
        disable_cache: bool = False,
        stream=False,
        capability_context: dict[str, Any] = {},
    ) -> ConvaAIResponse | AsyncGenerator[ConvaAIResponse, Any]:
        app_context: dict = {}
        response = await self.send_text2action_request_async(
            query,
            app_context,
            capability_name=capability_name,
            disable_cache=disable_cache,
            stream=stream,
            history=history,
            capability_context=capability_context,
        )
        if response.status_code != 200:
            await self.handle_error(response)
        if stream:
            return self.stream_response(response)
        else:
            action_response = ConvaAIResponse(**response.json())
            return action_response
