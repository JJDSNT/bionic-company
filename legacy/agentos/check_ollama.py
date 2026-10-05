import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:0.5b")

def check_server():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        r.raise_for_status()
        tags = r.json().get("models", [])
        available = any(m["name"] == MODEL_NAME for m in tags)
        if not available:
            print(f"❌ Modelo '{MODEL_NAME}' não está disponível no servidor.")
            return False
        print(f"✅ Servidor acessível e modelo '{MODEL_NAME}' disponível.")
        return True
    except Exception as e:
        print(f"❌ Falha ao conectar no servidor Ollama: {e}")
        return False

if __name__ == "__main__":
    if check_server():
        print("🔁 Agora você pode executar seus agentes com segurança.")
    else:
        print("⚠️ Corrija o servidor ou verifique a conexão antes de continuar.")
