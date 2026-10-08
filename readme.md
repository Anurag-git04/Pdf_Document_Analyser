# 📄 AI-Powered Document Analyzer

This project is a sophisticated document analysis tool designed to process scientific and technical PDF files. It leverages a suite of modern AI and NLP models to extract text, identify mathematical expressions, perform Named Entity Recognition (NER), and generate multiple layers of summaries. The application is presented through a user-friendly Streamlit web interface and is fully containerized with Docker for easy deployment and portability.

![Screenshot of the AI Document Analyzer UI](<ss/first.png>)

---

## ✨ Features

- **High-Speed Text Extraction:** Utilizes `PyMuPDF` for fast and accurate text extraction from digitally-native PDFs.
- **Advanced Mathematical Detection:** Employs a robust regex engine to find and categorize LaTeX, inline equations, and equation references.
- **Hybrid Named Entity Recognition (NER):** Combines the speed of `spaCy` with the power of a fine-tuned Hugging Face `Transformers` model for accurate entity detection (PERSON, ORG, GPE).
- **Dual-Layer Summarization:**
    -   **Extractive Summary:** A BERT-based model quickly pulls the most relevant sentences from the text.
    -   **Abstractive Synthesis:** An optional integration with the **Groq LPU™ Inference Engine** uses Llama 3 to generate a high-quality, human-like "Enhanced Analysis Report" from the extracted data.
- **Interactive Web Interface:** A clean and modern UI built with Streamlit, featuring visual highlights for entities and mathematical content.
- **Dockerized & Portable:** Fully containerized with Docker, ensuring a consistent and easy-to-run environment on any machine.

---

## 🛠️ Technology Stack

- **Backend:** Python
- **Core Libraries:**
    -   Streamlit (Web UI)
    -   PyMuPDF (PDF Processing)
    -   spaCy & Transformers (NLP / NER)
    -   PyTorch (Model Backend)
    -   bert-extractive-summarizer (Summarization)
    -   Groq SDK (LLM Inference)
- **Deployment:** Docker

---

## 🚀 Getting Started

There are two ways to run this application: locally using a Python virtual environment or via Docker (recommended for consistency).

### Prerequisites

- Python 3.12+
- Docker Desktop installed and running.
- A Groq API key (for the optional LLM synthesis feature).

### Method 1: Running with Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a `.env` file:**
    In the root of the project, create a file named `.env` and add your Groq API key:
    ```
    GROQ_API_KEY="gsk_YourSecretGroqApiKey"
    ```

3.  **Build the Docker image:**
    This command will build the image and download all necessary models. This may take a considerable amount of time on the first run.
    ```bash
    docker build -t pdf-analyzer .
    ```

4.  **Run the Docker container:**
    This command starts the application and securely passes your API key from the `.env` file into the container.
    ```bash
    docker run --rm -p 8501:8501 --env-file .env pdf-analyzer
    ```
    *   `--rm`: Automatically removes the container when it's stopped.
    *   `--env-file .env`: Loads environment variables from your `.env` file.

5.  **Access the application:**
    Open your web browser and navigate to **`http://localhost:8501`**.

### Method 2: Running Locally

1.  **Clone the repository and navigate into it.**

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

4.  **Create a `.env` file** as described in the Docker instructions above.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

6.  **Access the application:**
    Your browser should automatically open to the application, or you can navigate to the local URL provided in the terminal.

---

## 🏗️ Project Structure

The project is organized into modular components for clarity and maintainability:

```
.
├── analyzer.py             # Main orchestrator class that ties all modules together.
├── app.py                  # The Streamlit web application front-end.
├── document_processor.py   # Handles PDF text extraction.
├── math_detector.py        # Detects mathematical expressions.
├── ner_processor.py        # Performs Named Entity Recognition.
├── summary_generator.py    # Generates the extractive summary.
|
├── Dockerfile              # Blueprint for building the Docker image.
├── .dockerignore           # Specifies files to exclude from the Docker image.
├── requirements.txt        # List of Python dependencies.
└── README.md               # This file.
```

---

## 📸 Screenshots

#### Analysis Dashboard
![Summary Screenshot](<ss/summary.png>)

#### Groq LLM Synthesis
![Groq Synthesis Screenshot](<ss/Groq_LLM.png>)

![Groq AI maths Screenshot](<ss/Ai_maths.png>)
