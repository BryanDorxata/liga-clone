"""
Liga ng mga Barangay Chatbot Tools - Unified Service
"""
import os
import re
from typing import Dict, Any, List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from langdetect import detect, detect_langs, LangDetectException
from sklearn.metrics.pairwise import cosine_similarity

class LigaChatbotService:
    def __init__(self, doc_path: str = "utils/liga_documentation.md"):
        # Local documentation
        self.doc_path = doc_path
        self.content = ""
        self.sections = []
        self.qa_pairs = []
        
        # Language detection
        self.filipino_indicators = {
            'ang', 'ng', 'sa', 'ay', 'na', 'ni', 'mga', 'para', 'nang', 'kung',
            'ano', 'bakit', 'paano', 'saan', 'kailan', 'sino', 'alin', 'ilan',
            'mga', 'dapat', 'pwede', 'hindi', 'oo', 'talaga', 'kasi', 'pero',
            'tapos', 'yung', 'yun', 'dito', 'doon', 'dyan', 'namin', 'natin',
            'atin', 'kaya', 'lang', 'nila', 'niya', 'ako', 'ikaw', 'siya',
            'tayo', 'kayo', 'sila', 'ko', 'mo', 'niya', 'namin', 'ninyo',
            'nila', 'ba', 'po', 'opo', 'hindi', 'oo', 'opo', 'salamat',
            'kumusta', 'mabuti', 'ayos', 'okay', 'salamat', 'pasensya',
            'barangay', 'liga', 'SK', 'kapitan', 'kagawad', 'chairman'
        }
        
        self.taglish_patterns = [
            r'\b(yung|yun)\s+\w+',
            r'\b(kasi|pero)\s+\w+',
            r'\bmay\s+\w+\s+(ba|naman)',
            r'\b(parang|like)\s+\w+',
        ]
        
        # Embedding model
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Initialize
        self._load_documentation()
    
    def _load_documentation(self):
        """Load and parse the liga documentation file"""
        try:
            doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.doc_path)
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            self.sections = self._parse_sections()
            self.qa_pairs = self._extract_qa_pairs()
            
            print(f"Loaded documentation with {len(self.sections)} sections and {len(self.qa_pairs)} Q&A pairs")
            
        except Exception as e:
            print(f"Error loading documentation: {e}")
            self.content = ""
            self.sections = []
            self.qa_pairs = []
    
    def _parse_sections(self) -> List[Dict]:
        """Parse documentation into sections"""
        sections = []
        current_section = {"title": "", "content": "", "level": 0}
        
        lines = self.content.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                if current_section["content"].strip():
                    sections.append(current_section.copy())
                
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {
                    "title": title,
                    "content": "",
                    "level": level
                }
            else:
                current_section["content"] += line + '\n'
        
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_qa_pairs(self) -> List[Dict]:
        """Extract Q&A pairs from the FAQ section"""
        qa_pairs = []
        
        faq_content = ""
        for section in self.sections:
            if "frequently asked question" in section["title"].lower() or "faq" in section["title"].lower():
                faq_content = section["content"]
                break
        
        if not faq_content:
            faq_match = re.search(r'# Frequently Asked Question.*?(?=\n#|\Z)', self.content, re.DOTALL | re.IGNORECASE)
            if faq_match:
                faq_content = faq_match.group(0)
        
        if faq_content:
            qa_pattern = r'(\d+)\s*\n([^\n]+?)\n\n(.*?)(?=\n\d+|\Z)'
            matches = re.findall(qa_pattern, faq_content, re.DOTALL)
            
            for match in matches:
                number, question, answer = match
                qa_pairs.append({
                    "number": int(number),
                    "question": question.strip(),
                    "answer": answer.strip(),
                    "combined": f"Q: {question.strip()}\nA: {answer.strip()}"
                })
        
        return qa_pairs
    
    def detect_language(self, text: str) -> Dict:
        """Detect language with special handling for Filipino and Tag-lish"""
        if not text.strip():
            return {
                'primary_language': 'english',
                'confidence': 0.5,
                'filipino_score': 0.0,
                'english_score': 0.5,
                'is_mixed': False
            }
        
        clean_text = text.lower().strip()
        words = re.findall(r'\b\w+\b', clean_text)
        
        if not words:
            return {
                'primary_language': 'english',
                'confidence': 0.5,
                'filipino_score': 0.0,
                'english_score': 0.5,
                'is_mixed': False
            }
        
        filipino_word_count = sum(1 for word in words if word in self.filipino_indicators)
        filipino_score = filipino_word_count / len(words)
        
        taglish_score = 0
        for pattern in self.taglish_patterns:
            if re.search(pattern, clean_text):
                taglish_score += 0.2
        
        try:
            detected_langs = detect_langs(text)
            langdetect_results = {lang.lang: lang.prob for lang in detected_langs}
            english_prob = langdetect_results.get('en', 0)
            tagalog_prob = langdetect_results.get('tl', 0)
        except LangDetectException:
            english_prob = 0.5
            tagalog_prob = 0.0
        
        total_filipino_score = (filipino_score * 0.7) + (tagalog_prob * 0.3)
        total_english_score = english_prob
        
        is_mixed = filipino_score > 0.1 and english_prob > 0.3
        
        if is_mixed or taglish_score > 0.2:
            primary_language = 'taglish'
            confidence = 0.6 + (taglish_score * 0.4)
        elif total_filipino_score > 0.4:
            primary_language = 'filipino'
            confidence = total_filipino_score
        else:
            primary_language = 'english'
            confidence = max(total_english_score, 0.5)
        
        return {
            'primary_language': primary_language,
            'confidence': min(confidence, 1.0),
            'filipino_score': total_filipino_score,
            'english_score': total_english_score,
            'is_mixed': is_mixed
        }
    
    def _keyword_search(self, query: str, threshold: float = 0.1) -> List[Dict]:
        """Search using keyword matching"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        
        # Search Q&A pairs first (higher priority)
        for qa in self.qa_pairs:
            combined_text = (qa["question"] + " " + qa["answer"]).lower()
            text_words = set(re.findall(r'\b\w+\b', combined_text))
            
            overlap = len(query_words.intersection(text_words))
            if overlap > 0:
                score = overlap / len(query_words) * 1.5  # Boost Q&A pairs
                if score >= threshold:
                    results.append({
                        "content": qa["combined"],
                        "type": "qa",
                        "title": f"FAQ #{qa['number']}",
                        "score": score
                    })
        
        # Search sections
        for section in self.sections:
            if not section["content"].strip():
                continue
                
            section_text = (section["title"] + " " + section["content"]).lower()
            text_words = set(re.findall(r'\b\w+\b', section_text))
            
            overlap = len(query_words.intersection(text_words))
            if overlap > 0:
                score = overlap / len(query_words)
                if score >= threshold:
                    results.append({
                        "content": section["content"][:1000] + ("..." if len(section["content"]) > 1000 else ""),
                        "type": "section",
                        "title": section["title"],
                        "score": score
                    })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
    
    def _semantic_search(self, query: str, threshold: float = 0.3) -> List[Dict]:
        """Search using semantic similarity"""
        if not self.qa_pairs and not self.sections:
            return []
        
        texts = []
        metadata = []
        
        # Add Q&A pairs
        for qa in self.qa_pairs:
            texts.append(qa["combined"])
            metadata.append({
                "type": "qa",
                "title": f"FAQ #{qa['number']}",
                "content": qa["combined"]
            })
        
        # Add sections (first 500 chars)
        for section in self.sections:
            if section["content"].strip():
                content = section["content"][:500]
                texts.append(content)
                metadata.append({
                    "type": "section", 
                    "title": section["title"],
                    "content": content
                })
        
        if not texts:
            return []
        
        try:
            query_embedding = self.embedding_model.encode([query])
            text_embeddings = self.embedding_model.encode(texts)
            
            similarities = cosine_similarity(query_embedding, text_embeddings)[0]
            
            results = []
            for i, (similarity, meta) in enumerate(zip(similarities, metadata)):
                if similarity >= threshold:
                    results.append({
                        "content": meta["content"],
                        "type": meta["type"],
                        "title": meta["title"],
                        "score": float(similarity)
                    })
            
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:3]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

# Global singleton instance - initialized once and reused
_service_instance = None

def get_service() -> LigaChatbotService:
    """Get the singleton service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = LigaChatbotService()
    return _service_instance

def search_liga_documents(query: str) -> Dict[str, Any]:
    """
    Search Liga ng mga Barangay documentation for information
    """
    try:
        service = get_service()  # Use singleton instance
        
        # Detect language
        language_info = service.detect_language(query)
        
        # Search documentation
        keyword_results = service._keyword_search(query, threshold=0.1)
        semantic_results = service._semantic_search(query, threshold=0.3)
        
        # Combine results, avoiding duplicates
        combined_results = []
        seen_titles = set()
        
        for result in keyword_results:
            if result["title"] not in seen_titles:
                combined_results.append(result)
                seen_titles.add(result["title"])
        
        for result in semantic_results:
            if result["title"] not in seen_titles:
                combined_results.append(result)
                seen_titles.add(result["title"])
        
        if combined_results:
            avg_score = sum(r["score"] for r in combined_results) / len(combined_results)
            confidence = min(avg_score, 1.0)
            
            context_parts = []
            for result in combined_results[:3]:
                if result["type"] == "qa":
                    context_parts.append(result["content"])
                else:
                    context_parts.append(f"**{result['title']}**\n{result['content']}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            return {
                "status": "success",
                "context": context,
                "sources": [{"title": r["title"], "type": r["type"]} for r in combined_results[:3]],
                "confidence": confidence,
                "language_detected": language_info['primary_language'],
                "num_chunks": len(combined_results),
                "search_method": "documentation_search"
            }
        
        # No results found
        return {
            "status": "no_results",
            "context": "No relevant information found in Liga documentation.",
            "sources": [],
            "confidence": 0.0,
            "language_detected": language_info['primary_language'],
            "num_chunks": 0,
            "search_method": "no_results"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "context": "",
            "sources": [],
            "confidence": 0.0
        }
