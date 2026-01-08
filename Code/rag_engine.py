import os
import streamlit as st
import requests
import json
from typing import List
from dotenv import load_dotenv

import warnings
warnings.filterwarnings("ignore")

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ✅ UPDATED: Chains are now in 'langchain_classic' in v1.0+
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings

# --- Configuration ---
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Fallback to streamlit secrets if not in env
if not OPENROUTER_API_KEY and hasattr(st, "secrets"):
    try:
        OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    except KeyError:
        pass

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-chat"


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


class RAG_Engine:
    def __init__(self, pdf_path):
        """
        Initializes the RAG engine using LangChain components.
        """
        print("Initializing RAG Engine...")
        
        if not OPENROUTER_API_KEY:
             st.error("OpenRouter API Key not found. Please check your .env file or Streamlit secrets.")
             raise ValueError("API Key missing")

        # 1. Load the document
        if not os.path.exists(pdf_path):
             raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
             
        loader = PyPDFLoader(pdf_path)
        self.documents = loader.load()
        print(f"Loaded {len(self.documents)} pages from the PDF.")

        # 2. Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        self.split_docs = text_splitter.split_documents(self.documents)
        print(f"Split the document into {len(self.split_docs)} chunks.")

        # 3. Create embeddings and vector store
        print("Creating vector store with custom OpenRouter embeddings...")
        self.embeddings = OpenRouterEmbeddings(api_key=OPENROUTER_API_KEY)
        self.vector_store = FAISS.from_documents(self.split_docs, embedding=self.embeddings)
        print("Vector store created successfully.")

        # 4. Initialize LLM
        self.llm = ChatOpenAI(
            model_name=MODEL_NAME,
            openai_api_base=OPENROUTER_API_BASE,
            openai_api_key=OPENROUTER_API_KEY,
            temperature=0.3
        )

        # 5. Create Chain
        prompt = ChatPromptTemplate.from_template("""
        You are an expert assistant for 'Project Nova'. Your task is to answer questions accurately based ONLY on the provided context.
        If the answer is not available in the context, clearly state "I do not have information on this topic based on the provided document." Do not make up information.

        Context:
        {context}

        Question: {input}
        """)
        
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        print("RAG Pipeline assembled.")

    def query(self, user_question):
        """
        The main query function.
        """
        print(f"Received query: {user_question}")
        try:
            response = self.retrieval_chain.invoke({"input": user_question})
            answer = response["answer"]
            print(f"Generated answer: {answer}")
            return answer
        except Exception as e:
            return f"Error occurred during query: {e}"