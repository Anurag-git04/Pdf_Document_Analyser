import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from analyzer import DocumentAnalyzer  # The only custom class you need to import now
from groq import Groq                 # Import Groq for the LLM

# --- Configuration and API Key Loading ---
# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Document Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI-Powered Document Analyzer")
st.markdown("Upload a scientific PDF to extract text, identify math, find entities, and generate an enhanced summary with Llama 3 on Groq.")

# --- File Uploader ---
uploaded = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded:
    # Save uploaded PDF to a temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded.read())
        pdf_path = tmp.name

    try:
        # --- Core Analysis Step ---
        # 1. Initialize the main analyzer class
        analyzer = DocumentAnalyzer()
        
        # 2. Run the entire analysis with a single, clean method call
        with st.spinner("Analyzing document... This may take a moment for OCR or large files."):
            analysis_report = analyzer.analyze_document(pdf_path)

        # 3. Display results from the structured report
        if 'error' in analysis_report:
            st.error(f"Analysis failed: {analysis_report['error']}")
        else:
            # Unpack all the data from the report for easy access
            summary = analysis_report['summary']
            math_results = analysis_report['mathematical_expressions']
            entities = analysis_report['named_entities']
            pages = analysis_report['pages_content']
            doc_info = analysis_report['document_info']

            # --- Display "Classic" Extracted Information ---
            st.header("📝 Executive Summary (BART Model)")
            st.write(summary)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pages", doc_info['total_pages'])
            col2.metric("Total Words", f"{doc_info['total_words']:,}")
            col3.metric("Math Expressions Found", math_results.get('total_count', 0))

            with st.expander("🔎 View Named Entities"):
                ent_dict = {k: v for k, v in entities.items() if v}
                if not ent_dict:
                    st.info("No named entities were found.")
                else:
                    for category, ent_list in ent_dict.items():
                        st.write(f"**{category}:** {', '.join(ent_list[:10])}")
            
            with st.expander("🔢 View Mathematical Content"):
                if math_results.get("total_count", 0) == 0:
                    st.info("No mathematical expressions were detected.")
                if math_results.get("latex_expressions"):
                    st.subheader("LaTeX Expressions")
                    for expr in math_results["latex_expressions"][:10]:
                        st.latex(expr.strip('$'))
                if math_results.get("equation_references"):
                    st.subheader("Equation References")
                    st.write(", ".join(math_results["equation_references"][:10]))
                if math_results.get("math_expressions"):
                    st.subheader("Other Math Expressions")
                    for expr in math_results["math_expressions"][:10]:
                        st.code(expr)
            
            with st.expander("📄 View Page-by-Page Text"):
                for page in pages:
                    st.text_area(f"Page {page['page_number']} (Method: {page['extraction']}, Words: {page['word_count']})", 
                                 page["cleaned_text"], 
                                 height=150,
                                 key=f"page_{page['page_number']}")

            # --- Groq LLM Integration for Enhanced Synthesis ---
            if not GROQ_API_KEY:
                st.warning("GROQ_API_KEY not found in .env file. Real-time LLM synthesis is disabled.")
            else:
                st.header("🤖 Groq LLM: Real-time Synthesis with Llama 3")
                st.markdown("Click the button below to send the extracted data to Llama 3 on Groq's ultra-fast engine for a higher-level analysis.")

                if st.button("🚀 Synthesize with Groq"):
                    with st.spinner("Connecting to Groq..."):
                        try:
                            client = Groq(api_key=GROQ_API_KEY)

                            # Prepare a concise prompt with pre-processed data (this part is correct)
                            entity_summary_parts = []
                            for category, ent_list in ent_dict.items():
                                if ent_list:
                                    entity_summary_parts.append(f"- {category}: {', '.join(ent_list[:5])}")
                            entity_summary = "\n".join(entity_summary_parts) if entity_summary_parts else "None found."

                            math_summary_parts = []
                            if math_results.get("latex_expressions"):
                                expr_list = [f"`{expr}`" for expr in math_results["latex_expressions"][:3]]
                                math_summary_parts.append(f"- Key LaTeX Expressions: {', '.join(expr_list)}")
                            if math_results.get("math_expressions"):
                                expr_list = [f"`{expr}`" for expr in math_results["math_expressions"][:3]]
                                math_summary_parts.append(f"- Other Math Expressions: {', '.join(expr_list)}")
                            math_summary = "\n".join(math_summary_parts) if math_summary_parts else "No significant mathematical content detected."

                            # The structured prompt for the LLM (this part is correct)
                            prompt = f"""
                            You are an expert AI research assistant. Your task is to synthesize the pre-processed content from a scientific document and generate a structured, insightful report in Markdown format.
                            Base your analysis STRICTLY on the information provided below. Do not add external knowledge.

                            ---
                            [Input 1: Executive Summary]
                            {summary}

                            ---
                            [Input 2: Key Named Entities Found]
                            {entity_summary}

                            ---
                            [Input 3: Key Mathematical Content Found]
                            {math_summary}
                            ---

                            [Your Task]
                            Generate a report with the following structure:
                            ## 💡 Key Insights
                            (In 2-3 bullet points, what are the most important conclusions from the summary?)
                            ## 🔬 Significance of Technical Content
                            (Briefly explain what the identified mathematical expressions might represent in the context of the summary.)
                            ## 📚 Key Subjects and Entities
                            (List the most important topics and entities and explain their relevance based on the summary.)
                            """

                            # Call the Groq API with streaming enabled
                            completion_stream = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.7,
                                max_tokens=2048,
                                stream=True,
                            )
                            
                            # --- THIS IS THE FIX ---
                            # Create a helper generator to extract only the text content
                            def stream_parser(stream):
                                for chunk in stream:
                                    yield chunk.choices[0].delta.content or ""
                            
                            # Use st.write_stream with our new, clean generator
                            st.subheader("Enhanced Report from Groq (Llama 3)")
                            st.write_stream(stream_parser(completion_stream))
                            # -----------------------

                        except Exception as e:
                            st.error(f"Error calling Groq API: {e}")
    finally:
        # Clean up the temporary file safely
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception as e:
                st.warning(f"Could not delete temporary file: {e}")