from check_ollama import check_server
from agents.planner_agent import chain as planner_chain
from agents.executor_agent import chain as executor_chain


def extrair_primeira_acao(texto: str) -> str:
    """Extrai a primeira ação do plano gerado. Método simples baseado em quebra de linha."""
    linhas = texto.strip().split("\n")
    for linha in linhas:
        if linha.strip().startswith("1.") or linha.strip().startswith("-"):
            return linha.strip()
    return texto.strip()  # fallback se não houver estrutura numerada


if __name__ == "__main__":
    print("🔍 Verificando servidor Ollama...")
    if not check_server():
        exit(1)

    print("\n🤖 Gerando plano com o agente planejador...\n")
    objetivo = "melhorar o atendimento ao cliente em uma loja de móveis"
    plano = planner_chain.invoke({"objetivo": objetivo})
    print(plano)

    print("\n📌 Extraindo primeira ação do plano...")
    acao = extrair_primeira_acao(str(plano))
    print(f"\n➡️ Primeira ação identificada: {acao}")

    print("\n🛠️ Executando ação com o agente executor...\n")
    resultado = executor_chain.invoke({"acao": acao})
    print(resultado)
