import streamlit as st
import tempfile
import os
import re
from dotenv import load_dotenv
from analyzer import DocumentAnalyzer
from document_processor import DocumentProcessor
from math_detector import MathExpressionDetector
from ner_processor import NERProcessor
from summary_generator import DocumentSummarizer
from groq import Groq
from spacy_streamlit import visualize_ner

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def highlight_math(text: str, expressions: list) -> str:
    """Replaces math expressions in text with a highlighted version."""
    sorted_expressions = sorted(expressions, key=len, reverse=True)
    highlighted_text = text
    for expr in sorted_expressions:
        safe_expr = re.escape(expr)
        marker = f" <mark style='background-color: #fce67b; padding: 2px 4px; border-radius: 4px;'>`{expr}`</mark> "
        highlighted_text = re.sub(safe_expr, marker, highlighted_text, count=1)
    return highlighted_text

#  Streamlit Page Setup 
st.set_page_config(page_title="AI Document Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI-Powered Document Analyzer")
st.markdown("Upload a scientific PDF to extract text, identify math, find entities, and generate an enhanced summary with Llama 3 on Groq.")

@st.cache_resource
def load_processors():
    """Loads all heavy AI models and processors once and caches them."""
    st.write("First-time setup: Loading AI models...") 
    doc_processor = DocumentProcessor()
    math_detector = MathExpressionDetector()
    ner_processor = NERProcessor()
    summarizer = DocumentSummarizer()

    analyzer = DocumentAnalyzer(doc_processor, math_detector, ner_processor, summarizer)
    return analyzer, ner_processor.spacy_nlp

try:
    analyzer, nlp = load_processors()
except Exception as e:
    st.error(f"Fatal error during model initialization: {e}")
    st.error("The application cannot start. Please check the logs or try restarting.")
    st.stop() 


#  File Uploader 
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        pdf_path = tmp.name

    try:
        with st.spinner("Analyzing document... This may take a moment."):
            analysis_report = analyzer.analyze_document(pdf_path)

        #  Display results from the report 
        if 'error' in analysis_report:
            st.error(f"Analysis failed: {analysis_report['error']}")
        else:
            summary = analysis_report['summary']
            math_results = analysis_report['mathematical_expressions']
            entities = analysis_report['named_entities']
            pages = analysis_report['pages_content']
            doc_info = analysis_report['document_info']
            full_text = ' '.join([page['cleaned_text'] for page in pages])

            # Display Key Metrics and Initial Summary 
            st.header("📊 Analysis Dashboard")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pages", doc_info['total_pages'])
            col2.metric("Total Words", f"{doc_info['total_words']:,}")
            col3.metric("Math Expressions Found", math_results.get('total_count', 0))

            with st.expander("📝 View Extractive Summary (BERT-based)"):
                st.write(summary)

            tab1, tab2, tab3 = st.tabs(["**Entities & Math Lists**", "**Visual Highlights**", "**Page-by-Page Text**"])

            with tab1:
                st.subheader("Named Entities Found")
                ent_dict = {k: v for k, v in entities.items() if v}
                if not ent_dict:
                    st.info("No named entities were found.")
                else:
                    for category, ent_list in ent_dict.items():
                        st.markdown(f"**{category}:**")
                        st.write(f"`{', '.join(ent_list[:20])}`")
                
                st.subheader("Mathematical Content Found")
                if math_results.get("total_count", 0) == 0:
                    st.info("No mathematical expressions were detected.")
                if math_results.get("latex_expressions"):
                    st.markdown("**LaTeX Expressions:**")
                    for expr in math_results["latex_expressions"][:10]:
                        st.latex(expr.strip('$'))
                if math_results.get("math_expressions"):
                    st.markdown("**Other Math Expressions:**")
                    for expr in math_results["math_expressions"][:10]:
                        st.code(expr)

            with tab2:
                st.subheader("Visual Analysis of Full Text")
                if nlp:
                    doc = nlp(full_text[:50000]) 
                    visualize_ner(doc, labels=nlp.get_pipe("ner").labels, title="Highlighted Named Entities (spaCy)")
                
                st.markdown("---")
                st.subheader("Highlighted Mathematical Content")
                all_math = math_results.get("latex_expressions", []) + math_results.get("math_expressions", [])
                if all_math:
                    highlighted_text = highlight_math(full_text, all_math)
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                else:
                    st.info("No math expressions to highlight.")

            with tab3:
                st.subheader("Page-by-Page Extracted Text")
                for page in pages:
                    st.text_area(f"Page {page['page_number']} (Method: {page['extraction']}, Words: {page['word_count']})", 
                                 page["cleaned_text"], 
                                 height=200,
                                 key=f"page_{page['page_number']}")

# Groq LLM Integration
            if not GROQ_API_KEY:
                st.warning("GROQ_API_KEY not found. Real-time LLM synthesis is disabled.")
            else:
                st.header("🤖 Groq LLM: Real-time Synthesis with Llama 3")
                if st.button("🚀 Synthesize with Groq"):
                    with st.spinner("Connecting to Groq... Llama is thinking..."):
                        try:
                            client = Groq(api_key=GROQ_API_KEY)
                            
                            entity_summary_parts = []
                            for category, ent_list in ent_dict.items():
                                if ent_list:
                                    entity_summary_parts.append(f"- **{category}**: {', '.join(ent_list[:7])}")
                            entity_summary = "\n".join(entity_summary_parts) if entity_summary_parts else "None found."
                            
                            math_summary_parts = []
                            if math_results.get("latex_expressions"):
                                math_summary_parts.append(f"- **Key LaTeX Expressions**: {[f'`{e}`' for e in math_results['latex_expressions'][:3]]}")
                            if math_results.get("math_expressions"):
                                math_summary_parts.append(f"- **Other Math Expressions**: {[f'`{e}`' for e in math_results['math_expressions'][:3]]}")
                            math_summary = "\n".join(math_summary_parts) if math_summary_parts else "No significant mathematical content detected."

                            prompt = f"""
You are an expert AI research assistant. Your task is to synthesize a comprehensive, insightful, and well-structured analysis of a technical document based on pre-processed information.

Here is the data extracted from the document:

**1. Initial Extractive Summary:**
---
{summary}
---

**2. Key Named Entities:**
---
{entity_summary}
---

**3. Key Mathematical Content:**
---
{math_summary}
---

**Your Task:**

Based **only** on the information provided above, generate an "Enhanced Analysis Report". Your report should have the following sections:

**## Executive Synthesis:**
A one-paragraph abstractive summary. Do NOT just copy the initial summary. Synthesize the information to create a new, more readable overview of the document's purpose and key findings.

**## Core Concepts and Entities:**
In bullet points, explain the significance of the key entities. For people, mention their likely role (e.g., authors). For organizations, mention their context. For technical terms (like model names or methods), briefly explain what they are based on the summary.

**## Mathematical & Technical Focus:**
Describe the nature of the document's technical content based on the mathematical expressions. Is it heavy in calculus, algebra, statistics? Mention any key equations if they seem important.

**## Overall Assessment:**
Provide a concluding sentence about the document's likely field and complexity (e.g., "This appears to be a dense research paper in machine learning, focusing on...")

Write the report in clear, professional language. Use Markdown for formatting.
"""
                            
                            chat_completion = client.chat.completions.create(
                                model="llama-3.3-70b-versatile", 
                                messages=[{"role": "user", "content": prompt}], 
                                temperature=0.6, 
                                max_tokens=1500,
                                stream=True
                            )

                            def stream_parser(stream):
                                for chunk in stream:
                                    yield chunk.choices[0].delta.content or ""
                            
                            st.subheader("Enhanced Report from Groq (Llama 3.3)")
                            st.write_stream(stream_parser(chat_completion))
                        
                        except Exception as e:
                            st.error(f"Error calling Groq API: {e}")

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)