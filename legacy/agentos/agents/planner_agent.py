import os
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# Carregar variáveis de ambiente
load_dotenv()

model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:0.5b")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Inicializar modelo via Ollama
llm = OllamaLLM(model=model_name, base_url=base_url)

# Criar prompt com template
template = "Crie um plano de transformação digital para: {objetivo}"
prompt = PromptTemplate.from_template(template)

# Novo pipeline moderno
chain = prompt | llm

if __name__ == "__main__":
    objetivo = "melhorar o atendimento ao cliente em uma loja de móveis"
    plano = chain.invoke({"objetivo": objetivo})
    print("\n📋 Plano gerado pelo agente planejador:\n")
    print(plano)
