import re
from typing import Dict, List

class MathExpressionDetector:
    def __init__(self):
        # A comprehensive list of Greek letters for regex
        greek_letters = [
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
            'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
            'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
        ]
        greek_pattern = '|'.join([f'\\\\{letter}' for letter in greek_letters])

        # LaTeX patterns for major math environments and delimiters
        self.latex_patterns = [
            r'\$\$.*?\$\$',                               
            r'\$.*?\$',                                   
            r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}',  
            r'\\begin\{align\*?\}.*?\\end\{align\*?\}',        
            r'\\begin\{gather\*?\}.*?\\end\{gather\*?\}',      
            r'\\begin\{multline\*?\}.*?\\end\{multline\*?\}',  
            r'\\\[.*?\\\]',                             
            r'\\\(.*?\\\)',                               
        ]

        self.inline_math_patterns = [
            r'\b\w+\'?\s?\(?\w+\)?\s*=\s*[\w\(\)\+\-\*\s\.,]+',

            r'\b[a-zA-Z](?:_\{?[a-zA-Z0-9t\-]+\}?|\^\d+)?\s*=\s*.*?(?=\s{2,}|;|\n|,)',
            
            r'\b(?:exp|log|sin|cos|tan|softmax|sigmoid|discretize|Uniform)\s*\(.*?\)',
            
            r'(?:\\sum|\\prod|\\int|Σ|Π|∫)(?:_\{.*?\}|\^\{.*?\})?.*?(?=\s)',
            
            rf'(?:{greek_pattern})(_\w+)?\s*\(?.*?\)?',

            r'\\frac\{.*?\}\{.*?\}',
            r'\\sqrt\{.*?\}',
            
            # Basic arithmetic and ratios
            r'\b\d+\s*[\+\-\*/\^]\s*\d+\b',
            r'\b\d+/\d+\b',
            
            # Expressions with inequalities or arrows
            r'\b\w+\s*[<>≤≥=→↔]\s*\w+\b',
        ]

        # Patterns for numbered or referenced equations (e.g., Eq. (1), (2.5), (3a))
        self.equation_ref_patterns = [
            r'Eq\.?\s*\(\s*\d+(?:\.\d+)?[a-z]?\s*\)',
            r'Equation\s+\d+',
            r'\(A-\d+\)',                        
            r'(?<![a-zA-Z])\(\d+(?:\.\d+)?[a-z]?\)(?![a-zA-Z])', 
        ]

    def detect_math(self, text: str) -> Dict[str, List[str]]:
      
        all_matches = {}

        temp_text = text
        latex_matches = []
        for pattern in self.latex_patterns:
            found = re.findall(pattern, temp_text, flags=re.DOTALL)
            latex_matches.extend(found)
            temp_text = re.sub(pattern, " LATEX_BLOCK_REMOVED ", temp_text) 

        all_matches["latex_expressions"] = sorted(list(set(latex_matches)))

       
        inline_matches = []
        for pattern in self.inline_math_patterns:
            inline_matches.extend(re.findall(pattern, temp_text))
        
        
        equation_refs = []
        for pattern in self.equation_ref_patterns:
            equation_refs.extend(re.findall(pattern, temp_text))

        # Clean up and filter noise from inline expressions
        filtered_inline = sorted(list(set(
            expr.strip() for expr in inline_matches if self._is_meaningful(expr)
        )))

        all_matches["math_expressions"] = filtered_inline
        all_matches["equation_references"] = sorted(list(set(equation_refs)))
        
        all_matches["total_count"] = sum(len(v) for v in all_matches.values())

        return all_matches

    def _is_meaningful(self, expr: str) -> bool:
        """Filters out expressions that are likely not mathematical."""
        expr = expr.strip(" .,;")
        if len(expr) < 3:
            return False
        if re.fullmatch(r'[\d\.]+', expr):
            return False
        if expr.count(' ') > 5 and not any(c in expr for c in r'=\+-*/^ΣΠ∫'):
             return False
        if expr.lower() in ["et al."]:
            return False
        return True