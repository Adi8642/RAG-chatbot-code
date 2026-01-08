import os
import sys
import json
import requests
import warnings
from typing import List
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# LangChain Community Imports (Loaders & Vector Stores)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# OpenAI Models
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# ✅ UPDATED: Chains are now in 'langchain_classic' in v1.0+
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings

# --- Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-chat"
DOCUMENT_PATH = "./documents/project_quasar_brief.txt"

class OpenRouterEmbeddings(Embeddings):
    """Custom embedding class for OpenRouter API."""
    def __init__(self, model: str = "text-embedding-ada-002", api_key: str = None):
        if not api_key:
            raise ValueError("OpenRouter API key must be provided.")
        self.model = model
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/embeddings"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            self.api_url,
            headers=self.headers,
            data=json.dumps({"model": self.model, "input": texts})
        )
        response.raise_for_status()
        response_data = response.json()
        return [item['embedding'] for item in response_data['data']]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._get_embeddings([text])[0]

def main():
    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY not found. Please check your .env file.")
        sys.exit(1)

    print(f"✅ API Key loaded. (Ends with: {OPENROUTER_API_KEY[-4:]})")

    # 1. Load Document
    if not os.path.exists(DOCUMENT_PATH):
        print(f"❌ ERROR: Document not found at {DOCUMENT_PATH}")
        sys.exit(1)
        
    try:
        loader = TextLoader(DOCUMENT_PATH)
        docs = loader.load()
        print(f"✅ Document loaded: {len(docs)} document(s).")
    except Exception as e:
        print(f"❌ ERROR: Failed to load document: {e}")
        sys.exit(1)

    # 2. Split Document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    print(f"✅ Document split into {len(split_docs)} chunks.")

    # 3. Create Vector Store
    print("Initialize Custom Embeddings...")
    try:
        embeddings = OpenRouterEmbeddings(api_key=OPENROUTER_API_KEY)
        vector_store = FAISS.from_documents(split_docs, embedding=embeddings)
        print("✅ Vector store created successfully.")
    except Exception as e:
        print(f"❌ ERROR: Failed to create vector store: {e}")
        sys.exit(1)

    # 4. Initialize LLM
    try:
        llm = ChatOpenAI(
            model_name=MODEL_NAME,
            openai_api_base=OPENROUTER_API_BASE,
            openai_api_key=OPENROUTER_API_KEY,
            temperature=0.3
        )
        print("✅ LLM Initialized.")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize LLM: {e}")
        sys.exit(1)

    # 5. Create Chain
    prompt = ChatPromptTemplate.from_template("""
    Answer the user's question based only on the following context.
    If the answer is not in the context, say you don't know.
    Context:
    {context}

    Question: {input}
    """)
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    print("✅ Retrieval Chain Assembled.")

    # 6. Test Query
    query = "What is the purpose of Project Quasar?"
    print(f"\nrunning Query: '{query}'")
    try:
        response = retrieval_chain.invoke({"input": query})
        print("\n--- Answer ---")
        print(response["answer"])
    except Exception as e:
        print(f"❌ ERROR: Failed to run chain: {e}")

if __name__ == "__main__":
    main()
