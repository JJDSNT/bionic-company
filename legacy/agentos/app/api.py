from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ag_ui.core import (
    RunAgentInput,
    RunStartedEvent,
    RunFinishedEvent,
    TextMessageStartEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    EventType,
)
from ag_ui.encoder import EventEncoder
from uuid import uuid4
from langgraph.digital_plan_graph import build_graph

app = FastAPI(title="AG-UI AgentOS")

@app.post("/awp")
async def agui_endpoint(input_data: RunAgentInput):
    encoder = EventEncoder()
    graph = build_graph()
    message_id = str(uuid4())

    async def event_generator():
        yield encoder.encode(RunStartedEvent(
            type=EventType.RUN_STARTED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))

        yield encoder.encode(TextMessageStartEvent(
            type=EventType.TEXT_MESSAGE_START,
            message_id=message_id,
            role="assistant"
        ))

        # extraindo texto do usuário
        user_msg = next((m.content for m in input_data.messages if m.role == "user"), "nenhuma mensagem")

        # rodando o grafo
        result = graph.invoke({"objetivo": user_msg})

        for line in str(result.get("resultado", "")).splitlines():
            if line.strip():
                yield encoder.encode(TextMessageContentEvent(
                    type=EventType.TEXT_MESSAGE_CONTENT,
                    message_id=message_id,
                    delta=line
                ))

        yield encoder.encode(TextMessageEndEvent(
            type=EventType.TEXT_MESSAGE_END,
            message_id=message_id
        ))

        yield encoder.encode(RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))

    return StreamingResponse(event_generator(), media_type="text/event-stream")
