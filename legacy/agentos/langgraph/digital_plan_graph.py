from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

from agents.planner_agent import chain as planner_chain
from agents.executor_agent import chain as executor_chain


# 1. Define o contexto compartilhado que flui entre os nós
class GraphState(TypedDict):
    objetivo: str
    plano: Optional[str]
    acao: Optional[str]
    resultado: Optional[str]


# 2. Função: gerar o plano
def gerar_plano(state: GraphState) -> GraphState:
    plano = planner_chain.invoke({"objetivo": state["objetivo"]})
    return {**state, "plano": plano}


# 3. Função: extrair a primeira ação do plano
def extrair_primeira_acao(state: GraphState) -> GraphState:
    linhas = str(state["plano"]).split("\n")
    for linha in linhas:
        if linha.strip().startswith("1.") or linha.strip().startswith("-"):
            return {**state, "acao": linha.strip()}
    return {**state, "acao": state["plano"]}  # fallback


# 4. Função: executar a ação
def executar_acao(state: GraphState) -> GraphState:
    resultado = executor_chain.invoke({"acao": state["acao"]})
    return {**state, "resultado": resultado}


# 5. Construção do grafo sequencial
def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("planner", gerar_plano)
    workflow.add_node("extrair_acao", extrair_primeira_acao)
    workflow.add_node("executor", executar_acao)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "extrair_acao")
    workflow.add_edge("extrair_acao", "executor")
    workflow.add_edge("executor", END)

    return workflow.compile()


# 6. Exemplo de execução manual
if __name__ == "__main__":
    graph = build_graph()
    resultado_final = graph.invoke({
        "objetivo": "melhorar o atendimento ao cliente"
    })
    print("\n✅ Resultado Final do Grafo:\n")
    print(resultado_final)
