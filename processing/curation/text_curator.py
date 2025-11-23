"""
Text curation module inspired by NVIDIA NeMo Curator
Provides quality filtering, deduplication, and text cleaning capabilities
"""
import re
import hashlib
from typing import Dict, List, Optional, Set
from collections import Counter
import unicodedata

try:
    import langdetect
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class TextCurator:
    """
    Text curation processor inspired by NVIDIA NeMo Curator
    Provides quality filtering, deduplication, and text cleaning
    """
    
    def __init__(self, use_gpu: bool = True):
        self.name = "text_curator"
        self.use_gpu = use_gpu
        self.embedding_model = None
        
        # Initialize embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use multilingual model for better language support
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception:
                self.embedding_model = None
    
    def clean_text(self, text: str) -> Dict[str, any]:
        """
        Clean and normalize text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Dictionary with cleaned text and cleaning metadata
        """
        if not text:
            return {
                "cleaned_text": "",
                "cleaning_stats": {
                    "original_length": 0,
                    "cleaned_length": 0,
                    "removed_chars": 0
                }
            }
        
        original_length = len(text)
        cleaned = text
        
        # Normalize unicode characters
        cleaned = unicodedata.normalize('NFKC', cleaned)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove control characters (except newlines and tabs)
        cleaned = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
        
        # Remove excessive punctuation
        cleaned = re.sub(r'[!]{3,}', '!', cleaned)
        cleaned = re.sub(r'[?]{3,}', '?', cleaned)
        cleaned = re.sub(r'[.]{4,}', '...', cleaned)
        
        # Remove URLs
        cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
        
        # Remove email addresses
        cleaned = re.sub(r'\S+@\S+', '', cleaned)
        
        # Remove excessive line breaks
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        cleaned_length = len(cleaned)
        removed_chars = original_length - cleaned_length
        
        return {
            "cleaned_text": cleaned,
            "cleaning_stats": {
                "original_length": original_length,
                "cleaned_length": cleaned_length,
                "removed_chars": removed_chars,
                "reduction_percent": round((removed_chars / original_length * 100) if original_length > 0 else 0, 2)
            }
        }
    
    def assess_quality(self, text: str) -> Dict[str, any]:
        """
        Assess text quality using heuristic filters
        
        Args:
            text: Text to assess
            
        Returns:
            Dictionary with quality metrics and score
        """
        if not text:
            return {
                "quality_score": 0.0,
                "quality_metrics": {},
                "passed_filters": [],
                "failed_filters": []
            }
        
        metrics = {}
        passed_filters = []
        failed_filters = []
        
        # Length check
        text_length = len(text)
        word_count = len(text.split())
        char_count = len(text.replace(' ', ''))
        
        metrics["length"] = text_length
        metrics["word_count"] = word_count
        metrics["char_count"] = char_count
        
        # Minimum length filter
        if text_length >= 50:
            passed_filters.append("minimum_length")
        else:
            failed_filters.append("minimum_length")
        
        # Word count filter
        if word_count >= 10:
            passed_filters.append("minimum_words")
        else:
            failed_filters.append("minimum_words")
        
        # Character diversity (unique chars / total chars)
        unique_chars = len(set(text.lower()))
        char_diversity = unique_chars / max(len(text), 1)
        metrics["char_diversity"] = round(char_diversity, 3)
        
        if char_diversity > 0.1:  # At least 10% unique characters
            passed_filters.append("char_diversity")
        else:
            failed_filters.append("char_diversity")
        
        # Repetition check (check for excessive repetition)
        words = text.split()
        if len(words) > 0:
            word_freq = Counter(words)
            max_freq = max(word_freq.values())
            repetition_ratio = max_freq / len(words)
            metrics["repetition_ratio"] = round(repetition_ratio, 3)
            
            if repetition_ratio < 0.3:  # No single word should appear more than 30%
                passed_filters.append("low_repetition")
            else:
                failed_filters.append("high_repetition")
        
        # Special character ratio
        special_chars = len(re.findall(r'[^\w\s]', text))
        special_char_ratio = special_chars / max(len(text), 1)
        metrics["special_char_ratio"] = round(special_char_ratio, 3)
        
        if special_char_ratio < 0.3:  # Less than 30% special characters
            passed_filters.append("reasonable_special_chars")
        else:
            failed_filters.append("excessive_special_chars")
        
        # Calculate quality score (0-100)
        quality_score = 0.0
        total_filters = len(passed_filters) + len(failed_filters)
        if total_filters > 0:
            quality_score = (len(passed_filters) / total_filters) * 100
        
        # Bonus for longer, diverse text
        if word_count > 100:
            quality_score += 5
        if char_diversity > 0.3:
            quality_score += 5
        
        quality_score = min(100.0, quality_score)
        
        return {
            "quality_score": round(quality_score, 2),
            "quality_metrics": metrics,
            "passed_filters": passed_filters,
            "failed_filters": failed_filters,
            "is_high_quality": quality_score >= 70.0
        }
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with language detection results
        """
        if not LANGDETECT_AVAILABLE:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "available": False
            }
        
        if not text or len(text) < 10:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "reason": "text_too_short"
            }
        
        try:
            # Detect primary language
            primary_lang = detect(text)
            
            # Get confidence scores
            lang_probs = detect_langs(text)
            confidence = lang_probs[0].prob if lang_probs else 0.0
            
            # Get all detected languages with probabilities
            all_languages = [
                {"language": lang.lang, "probability": round(lang.prob, 3)}
                for lang in lang_probs[:3]  # Top 3 languages
            ]
            
            return {
                "language": primary_lang,
                "confidence": round(confidence, 3),
                "all_languages": all_languages,
                "available": True
            }
        except Exception as e:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "error": str(e),
                "available": True
            }
    
    def deduplicate_texts(self, texts: List[str], method: str = "exact") -> Dict[str, any]:
        """
        Remove duplicate texts
        
        Args:
            texts: List of texts to deduplicate
            method: Deduplication method ("exact", "fuzzy", "semantic")
            
        Returns:
            Dictionary with deduplicated texts and statistics
        """
        if not texts:
            return {
                "deduplicated_texts": [],
                "original_count": 0,
                "deduplicated_count": 0,
                "removed_count": 0,
                "duplicates": []
            }
        
        original_count = len(texts)
        deduplicated = []
        seen_hashes = set()
        duplicates = []
        
        if method == "exact":
            # Exact deduplication using hash
            for text in texts:
                text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                if text_hash not in seen_hashes:
                    seen_hashes.add(text_hash)
                    deduplicated.append(text)
                else:
                    duplicates.append(text)
        
        elif method == "fuzzy" and SENTENCE_TRANSFORMERS_AVAILABLE:
            # Fuzzy deduplication using embeddings
            if self.embedding_model:
                embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
                
                # Simple cosine similarity threshold
                threshold = 0.95
                seen_indices = set()
                
                for i, text in enumerate(texts):
                    if i in seen_indices:
                        continue
                    
                    is_duplicate = False
                    for j, dedup_text in enumerate(deduplicated):
                        if j in seen_indices:
                            continue
                        
                        # Calculate cosine similarity
                        similarity = np.dot(embeddings[i], embeddings[j]) / (
                            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                        )
                        
                        if similarity >= threshold:
                            is_duplicate = True
                            duplicates.append(text)
                            break
                    
                    if not is_duplicate:
                        deduplicated.append(text)
                        seen_indices.add(i)
            else:
                # Fallback to exact if model not available
                return self.deduplicate_texts(texts, method="exact")
        
        else:
            # Fallback to exact
            return self.deduplicate_texts(texts, method="exact")
        
        removed_count = original_count - len(deduplicated)
        
        return {
            "deduplicated_texts": deduplicated,
            "original_count": original_count,
            "deduplicated_count": len(deduplicated),
            "removed_count": removed_count,
            "duplicates": duplicates,
            "method": method
        }
    
    def curate_text(self, text: str, enable_cleaning: bool = True, 
                   enable_quality_check: bool = True, 
                   enable_language_detection: bool = True) -> Dict[str, any]:
        """
        Complete text curation pipeline
        
        Args:
            text: Text to curate
            enable_cleaning: Enable text cleaning
            enable_quality_check: Enable quality assessment
            enable_language_detection: Enable language detection
            
        Returns:
            Dictionary with curated text and all metadata
        """
        result = {
            "original_text": text,
            "curated_text": text,
            "curation_metadata": {}
        }
        
        # Text cleaning
        if enable_cleaning:
            cleaning_result = self.clean_text(text)
            result["curated_text"] = cleaning_result["cleaned_text"]
            result["curation_metadata"]["cleaning"] = cleaning_result["cleaning_stats"]
        
        # Quality assessment
        if enable_quality_check:
            quality_result = self.assess_quality(result["curated_text"])
            result["curation_metadata"]["quality"] = quality_result
        
        # Language detection
        if enable_language_detection:
            lang_result = self.detect_language(result["curated_text"])
            result["curation_metadata"]["language"] = lang_result
        
        return result

