import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ocr_engine import get_ocr_engine
from core.image_preprocessor import ImagePreprocessor
from core.text_postprocessor import TextPostprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRComparator:
    
    def __init__(self, config_path: str = "config/preprocessing_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.engines = ["paddleocr", "tesseract", "easyocr"]
        self.preprocessor = ImagePreprocessor(self.config)
        self.postprocessor = TextPostprocessor(self.config)
        
    def compare_on_samples(self, sample_paths: List[str]) -> Dict[str, Any]:
        results = {
            "timestamp": datetime.now().isoformat(),
            "config_version": self.config.get("config_version"),
            "samples": [],
            "summary": {}
        }
        
        for sample_path in sample_paths:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {sample_path}")
            logger.info(f"{'='*60}")
            
            sample_result = self._compare_sample(sample_path)
            results["samples"].append(sample_result)
        
        results["summary"] = self._calculate_summary(results["samples"])
        
        return results
    
    def _compare_sample(self, sample_path: str) -> Dict[str, Any]:
        sample_result = {
            "file": sample_path,
            "engines": {}
        }
        
        logger.info("Preprocessing image...")
        preprocessed_path, preprocess_meta = self.preprocessor.preprocess(
            sample_path, save_debug=True
        )
        
        for engine_name in self.engines:
            logger.info(f"\nTesting {engine_name}...")
            engine_result = self._test_engine(engine_name, preprocessed_path)
            sample_result["engines"][engine_name] = engine_result
            
            logger.info(f"  Tokens: {engine_result['token_count']}")
            logger.info(f"  Avg Confidence: {engine_result['avg_confidence']:.3f}")
            logger.info(f"  Time: {engine_result['time_seconds']:.2f}s")
            logger.info(f"  Text Length: {engine_result['text_length']}")
        
        return sample_result
    
    def _test_engine(self, engine_name: str, image_path: str) -> Dict[str, Any]:
        try:
            engine_config = self.config.get("ocr", {}).get("engines", {}).get(engine_name, {})
            lang = engine_config.get("lang", "en")
            engine = get_ocr_engine(engine_name, lang)
            
            start_time = time.time()
            raw_data = engine.extract_text_with_coordinates(image_path)
            extraction_time = time.time() - start_time
            
            tokens = []
            confidences = []
            
            for item in raw_data:
                bbox = item['bbox']
                
                if isinstance(bbox, list) and len(bbox) == 4:
                    if all(isinstance(x, list) for x in bbox):
                        x_coords = [p[0] for p in bbox]
                        y_coords = [p[1] for p in bbox]
                        normalized_bbox = [min(x_coords), min(y_coords), 
                                         max(x_coords), max(y_coords)]
                    else:
                        normalized_bbox = bbox
                else:
                    normalized_bbox = [0, 0, 0, 0]
                
                token = {
                    'text': item['text'],
                    'bbox': normalized_bbox,
                    'confidence': item['confidence']
                }
                tokens.append(token)
                confidences.append(item['confidence'])
            
            processed_tokens = self.postprocessor.process_tokens(tokens)
            
            full_text = '\n'.join([t['text'] for t in processed_tokens])
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            low_conf_count = sum(1 for c in confidences if c < 0.6)
            
            return {
                "success": True,
                "token_count": len(tokens),
                "avg_confidence": avg_confidence,
                "low_confidence_count": low_conf_count,
                "time_seconds": extraction_time,
                "text_length": len(full_text),
                "sample_text": full_text[:200]
            }
            
        except Exception as e:
            logger.error(f"Engine {engine_name} failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_summary(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary = {}
        
        for engine_name in self.engines:
            engine_stats = {
                "total_samples": 0,
                "successful_samples": 0,
                "avg_confidence": 0,
                "avg_time": 0,
                "total_tokens": 0,
                "low_confidence_tokens": 0
            }
            
            confidences = []
            times = []
            
            for sample in samples:
                if engine_name in sample["engines"]:
                    result = sample["engines"][engine_name]
                    engine_stats["total_samples"] += 1
                    
                    if result.get("success"):
                        engine_stats["successful_samples"] += 1
                        confidences.append(result["avg_confidence"])
                        times.append(result["time_seconds"])
                        engine_stats["total_tokens"] += result["token_count"]
                        engine_stats["low_confidence_tokens"] += result["low_confidence_count"]
            
            if confidences:
                engine_stats["avg_confidence"] = sum(confidences) / len(confidences)
            if times:
                engine_stats["avg_time"] = sum(times) / len(times)
            
            summary[engine_name] = engine_stats
        
        return summary
    
    def save_results(self, results: Dict[str, Any], output_path: str = "output/ocr_comparison.json"):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nResults saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        print("\n" + "="*60)
        print("OCR ENGINE COMPARISON SUMMARY")
        print("="*60)
        
        summary = results["summary"]
        
        best_engine = max(
            summary.items(),
            key=lambda x: x[1]["avg_confidence"] if x[1]["successful_samples"] > 0 else 0
        )
        
        print(f"\nBest Engine: {best_engine[0].upper()}")
        print(f"  Average Confidence: {best_engine[1]['avg_confidence']:.3f}")
        print(f"  Average Time: {best_engine[1]['avg_time']:.2f}s")
        
        print("\nAll Engines:")
        for engine_name, stats in summary.items():
            print(f"\n{engine_name.upper()}:")
            print(f"  Success Rate: {stats['successful_samples']}/{stats['total_samples']}")
            print(f"  Avg Confidence: {stats['avg_confidence']:.3f}")
            print(f"  Avg Time: {stats['avg_time']:.2f}s")
            print(f"  Total Tokens: {stats['total_tokens']}")
            print(f"  Low Confidence: {stats['low_confidence_tokens']}")
        
        print("\n" + "="*60)

def main():
    sample_paths = [
        "Dataset/Pay Slips/BIRO-Sample-Payslip_Robson.pdf",
        "Dataset/Bank Statements/test ocr bank statement bank islam.pdf"
    ]
    
    existing_samples = [p for p in sample_paths if Path(p).exists()]
    
    if not existing_samples:
        logger.error("No sample files found! Please provide valid sample paths.")
        return
    
    logger.info(f"Found {len(existing_samples)} sample files")
    
    comparator = OCRComparator()
    results = comparator.compare_on_samples(existing_samples)
    
    comparator.save_results(results)
    comparator.print_summary(results)

if __name__ == "__main__":
    main()
