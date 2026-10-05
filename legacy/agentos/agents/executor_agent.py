import os
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# Carrega as variáveis de ambiente
load_dotenv()

model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:0.5b")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Inicializa o LLM com base nas variáveis
llm = OllamaLLM(model=model_name, base_url=base_url)

# Prompt template moderno
template = (
    "Você é um agente executor.\n"
    "Recebeu a seguinte ação de um plano estratégico:\n\n"
    "{acao}\n\n"
    "Explique como ela seria executada na prática, listando etapas, ferramentas necessárias e possíveis riscos."
)
prompt = PromptTemplate.from_template(template)

# Pipeline moderno
chain = prompt | llm

if __name__ == "__main__":
    acao = "Criar um chatbot de atendimento ao cliente usando WhatsApp Business API e integração com CRM"
    resultado = chain.invoke({"acao": acao})
    print("\n🛠️ Execução simulada da ação:\n")
    print(resultado)
