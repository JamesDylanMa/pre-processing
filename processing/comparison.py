"""
Compare results from different processors
"""
from typing import Dict, List
import json


class ResultComparator:
    """Compare and evaluate processing results"""
    
    def __init__(self):
        self.name = "result_comparator"
    
    def compare_results(self, results: List[Dict]) -> Dict:
        """
        Compare multiple processing results
        
        Args:
            results: List of result dictionaries from different processors
            
        Returns:
            Comparison analysis dictionary
        """
        if not results:
            return {"error": "No results to compare"}
        
        comparison = {
            "total_processors": len(results),
            "processors": [r.get("parser") or r.get("processor", "unknown") for r in results],
            "comparison_metrics": {},
            "recommendations": []
        }
        
        # Extract text from all results
        texts = []
        for result in results:
            text = result.get("text", "")
            if not text and result.get("pages"):
                # Extract from pages
                text = "\n".join([page.get("text", "") for page in result.get("pages", [])])
            if not text and result.get("sheets"):
                # Extract from sheets
                text = json.dumps([sheet.get("data", []) for sheet in result.get("sheets", [])])
            texts.append(text)
        
        # Calculate metrics
        metrics = []
        for i, (result, text) in enumerate(zip(results, texts)):
            metric = {
                "processor": result.get("parser") or result.get("processor", f"processor_{i}"),
                "text_length": len(text),
                "word_count": len(text.split()) if text else 0,
                "has_errors": "error" in result,
                "has_tables": len(result.get("tables", [])) > 0 or len(result.get("sheets", [])) > 0,
                "has_metadata": "metadata" in result and bool(result["metadata"]),
                "processing_time": result.get("processing_time", 0)
            }
            metrics.append(metric)
        
        comparison["comparison_metrics"] = metrics
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, results)
        comparison["recommendations"] = recommendations
        
        # Find best processor
        best_processor = self._find_best_processor(metrics)
        comparison["best_processor"] = best_processor
        
        return comparison
    
    def _generate_recommendations(self, metrics: List[Dict], results: List[Dict]) -> List[str]:
        """Generate recommendations based on comparison"""
        recommendations = []
        
        # Find processor with most text extracted
        max_text = max(m.get("text_length", 0) for m in metrics)
        best_text_processor = next((m["processor"] for m in metrics if m["text_length"] == max_text), None)
        
        if best_text_processor:
            recommendations.append(
                f"'{best_text_processor}' extracted the most text ({max_text} characters)"
            )
        
        # Check for errors
        error_processors = [m["processor"] for m in metrics if m["has_errors"]]
        if error_processors:
            recommendations.append(
                f"Warning: The following processors encountered errors: {', '.join(error_processors)}"
            )
        
        # Check for table extraction
        table_processors = [m["processor"] for m in metrics if m["has_tables"]]
        if table_processors:
            recommendations.append(
                f"For documents with tables, consider using: {', '.join(table_processors)}"
            )
        
        # Check for metadata
        metadata_processors = [m["processor"] for m in metrics if m["has_metadata"]]
        if metadata_processors:
            recommendations.append(
                f"For document metadata extraction, consider using: {', '.join(metadata_processors)}"
            )
        
        return recommendations
    
    def _find_best_processor(self, metrics: List[Dict]) -> Dict:
        """Find the best overall processor"""
        if not metrics:
            return {}
        
        # Score each processor
        scored = []
        for metric in metrics:
            score = 0
            
            # Higher text length is better
            score += metric.get("text_length", 0) / 1000
            
            # Having tables is good
            if metric.get("has_tables"):
                score += 10
            
            # Having metadata is good
            if metric.get("has_metadata"):
                score += 5
            
            # Errors reduce score
            if metric.get("has_errors"):
                score -= 50
            
            scored.append({
                "processor": metric["processor"],
                "score": score,
                "metrics": metric
            })
        
        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        return scored[0] if scored else {}


