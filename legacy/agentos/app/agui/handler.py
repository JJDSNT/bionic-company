from ag_ui.core import AGUIHandler, Event
from langgraph.digital_plan_graph import build_graph

handler = AGUIHandler()
graph = build_graph()


@handler.on_event("user_input")
async def handle_user_input(event: Event):
    objetivo = event.data.get("text", "melhorar o atendimento ao cliente")

    yield {"type": "message", "text": f"🎯 Objetivo recebido: {objetivo}"}

    result = graph.invoke({"objetivo": objetivo})

    yield {"type": "message", "text": "📋 Plano gerado:"}
    yield {"type": "message", "text": result.get("plano", "sem plano")}

    yield {"type": "message", "text": f"🛠️ Ação sugerida: {result.get('acao', 'sem ação')}"}
    yield {"type": "message", "text": f"✅ Resultado da execução: {result.get('resultado', 'sem resultado')}"}
