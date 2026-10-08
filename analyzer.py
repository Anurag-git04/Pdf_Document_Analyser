
from document_processor import DocumentProcessor
from math_detector import MathExpressionDetector
from ner_processor import NERProcessor
from summary_generator import DocumentSummarizer 
from typing import Dict, List
import json
import logging


class DocumentAnalyzer:
    def __init__(self, document_processor, math_detector, ner_processor, summarizer):
        self.document_processor = document_processor
        self.math_detector = math_detector
        self.ner_processor = ner_processor
        self.summarizer = summarizer
        self.logger = logging.getLogger(__name__)
    
    def analyze_document(self, pdf_path: str) -> Dict:
        """Complete end-to-end document analysis."""
        self.logger.info(f"Starting analysis of: {pdf_path}")
        
        try:
            pages_content = self.document_processor.extract_text_from_pdf(pdf_path)
            if not pages_content:
                full_text = ""
            else:
                full_text = ' '.join([page['cleaned_text'] for page in pages_content])
            
            math_results = self.math_detector.detect_math(full_text)
            ner_results = self.ner_processor.extract_entities(full_text)
            summary_results = self.summarizer.summarize(full_text)
            
            analysis_result = {
                'document_info': {
                    'total_pages': len(pages_content),
                    'total_words': sum([page.get('word_count', 0) for page in pages_content]),
                    'file_path': pdf_path
                },
                'pages_content': pages_content,
                'mathematical_expressions': math_results,
                'named_entities': ner_results,
                'summary': summary_results,
                'analysis_metadata': {
                    'processing_status': 'completed',
                    'modules_used': ['pdf_extraction', 'math_detection', 'ner', 'summarization']
                }
            }
            
            self.logger.info("Document analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {
                'error': str(e),
                'analysis_metadata': {
                    'processing_status': 'failed'
                }
            }
    
    def generate_analysis_report(self, analysis_result: Dict) -> str:
        """Generate a formatted analysis report."""
        if 'error' in analysis_result:
            return f"Analysis failed: {analysis_result['error']}"
        
        report = []
        doc_info = analysis_result['document_info']
        
        report.append("# Document Analysis Report\n")
        report.append(f"**Total Pages:** {doc_info['total_pages']}")
        report.append(f"**Total Words:** {doc_info['total_words']}\n")
        
        # Summary section
        summary = analysis_result['summary']
        report.append("## Executive Summary")
        report.append(summary) 
        report.append(f"*Summary generated using a BART model or fallback.*\n")
        
        # Mathematical expressions
        math_info = analysis_result['mathematical_expressions']
        if math_info['total_count'] > 0:
            report.append("## Mathematical Content")
            report.append(f"**Total expressions found:** {math_info['total_count']}")
            
            if math_info.get('latex_expressions'):
                report.append("**LaTeX expressions:**")
                for expr in math_info['latex_expressions'][:5]:
                    report.append(f"- `{expr}`")
            
            if math_info.get('math_expressions'):
                report.append("**Mathematical expressions:**")
                for expr in math_info['math_expressions'][:5]:
                    report.append(f"- `{expr}`")
            report.append("")
        
        # Named entities
        entities = analysis_result['named_entities']
        report.append("## Named Entities")
        
        for category, entity_list in entities.items():
            if entity_list:
                report.append(f"**{category}:** {', '.join(entity_list[:10])}")
        
        return '\n'.join(report)