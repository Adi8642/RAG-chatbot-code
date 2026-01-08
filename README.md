# RAG-chatbot-code
# Enterprise RAG AI Assistant

A robust Retrieval-Augmented Generation (RAG) system built with **Streamlit**, **LangChain**, and **OpenRouter/DeepSeek**, designed to answer questions from internal company documents with high accuracy and low hallucination.

![System Architecture](system_architecture.png)

## 🚀 Key Features

*   **📄 Document Chat**: Upload any PDF document (e.g., Project Briefs, Employee Handbooks) and ask questions naturally.
*   **✅ High Accuracy**: Achieved **100% Accuracy** on the "Project Nova" evaluation dataset (25 queries).
*   **🛡️ Hallucination Prevention**: Explicitly trained to say "I don't know" when information is missing from the context.
*   **📊 Performance Metrics**: Includes scripts to calculate Latency (Min/Max/Mean) and Query Resolution Score (QRS).
*   **⚡ Modern Stack**: Uses FAISS for vector search and DeepSeek-V3 for reasoning.

## 🛠️ Technology Stack

*   **Frontend**: Streamlit
*   **Orchestration**: LangChain (Python)
*   **Vector Database**: FAISS (Facebook AI Similarity Search)
*   **LLM**: DeepSeek (via OpenRouter API)
*   **Embeddings**: Custom OpenRouter Embeddings

## 📂 Project Structure

```bash
├── app.py                  # Main Streamlit Application
├── rag_engine.py           # Core RAG Logic (Loading, Splitting, Retrieval)
├── rag_pipeline.py         # Standalone script for testing the pipeline
├── evaluate.py             # Evaluation suite (Accuracy & QRS metrics)
├── generate_pdf.py         # Utility to generate the "Project Nova" test PDF
├── project_nova_brief.pdf  # Default knowledge base
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (API Keys)
```

## ⚡ Quick Start

### 1. Prerequisites
*   Python 3.10+
*   An OpenRouter API Key

### 2. Installation
Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your API Key:

```env
OPENROUTER_API_KEY=your_key_here
```

### 4. Running the App
Launch the Streamlit interface:

```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

## 🧪 Evaluation & Testing

We provide a comprehensive evaluation suite to verify system performance.

**Run the Evaluation Script:**
```bash
python evaluate.py
```
**Output Metrics:**
*   **Accuracy Metric**: Percentage of correctly answered questions.
*   **Query Resolution Score (QRS)**: Overall system effectiveness.
*   **Latency Stats**: Min, Max, Mean, and Median response times.

**Current Benchmarks (Project Nova Dataset):**
*   **Accuracy**: 100%
*   **Mean Latency**: ~2.9s
*   **Unanswerable Handling**: 100% Correct Abstention

## 📝 Customization

*   **Upload Your Own Data**: Use the sidebar in the app to upload any PDF file.
*   **Modify System Prompt**: Edit `rag_engine.py` to change the persona or strictness of the AI.

## 🤝 Contributing
Feel free to open issues or submit pull requests for improvements!
