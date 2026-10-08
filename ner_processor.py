import spacy
from transformers import pipeline
from typing import Dict, List

class NERProcessor:
    def __init__(self):
        self.spacy_nlp = spacy.load("en_core_web_sm")
        try:
            self.hf_ner = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
        except Exception:
            self.hf_ner = None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {"PERSON": [], "ORG": [], "GPE": [], "OTHER": []}

        # spaCy
        doc = self.spacy_nlp(text)
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
            else:
                entities["OTHER"].append(ent.text)

        if self.hf_ner:
            hf_labels = {'PER': 'PERSON', 'ORG': 'ORG', 'LOC': 'GPE'}
            results = self.hf_ner(text[:1000])  
            for ent in results:
                category = hf_labels.get(ent['entity_group'], "OTHER")
                entities[category].append(ent['word'])
        for key in entities:
            entities[key] = list(set(entities[key]))
        return entities
