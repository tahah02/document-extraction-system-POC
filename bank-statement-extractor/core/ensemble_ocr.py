import logging
from typing import List, Dict, Any, Optional, Tuple
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from pathlib import Path
import json
import json
from datetime import datetime
from datetime import datetime

from core.ocr_engine import get_ocr_engine
from core.text_postprocessor import TextPostprocessor
from core.text_postprocessor import TextPostprocessor


logger = logging.getLogger(__name__)

class EnsembleOCR:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ocr_config = config.get("ocr", {})
        self.primary_engine_name = self.ocr_config.get("primary_engine", "paddleocr")
        self.fallback_engine_names = self.ocr_config.get("fallback_engines", [])
        self.retry_threshold = self.ocr_config.get("retry_threshold", 0.6)
        self.retry_enabled = self.ocr_config.get("retry_on_low_confidence", True)
        
        self.primary_engine = None
        self.fallback_engines = {}
        self._initialize_engines()
        
        self.postprocessor = TextPostprocessor(config)
        
    def _initialize_engines(self):
        try:
            logger.info(f"Initializing primary OCR engine: {self.primary_engine_name}")
            engine_config = self.ocr_config.get("engines", {}).get(self.primary_engine_name, {})
            lang = engine_config.get("lang", "en")
            self.primary_engine = get_ocr_engine(self.primary_engine_name, lang)
            
            if self.retry_enabled:
                for engine_name in self.fallback_engine_names:
                    try:
                        logger.info(f"Initializing fallback OCR engine: {engine_name}")
                        engine_config = self.ocr_config.get("engines", {}).get(engine_name, {})
                        lang = engine_config.get("lang", "en")
                        self.fallback_engines[engine_name] = get_ocr_engine(engine_name, lang)
                    except Exception as e:
                        logger.warning(f"Failed to initialize fallback engine {engine_name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCR engines: {str(e)}")
            raise
    
    def extract_text_with_tokens(self, image_path: str, page: int = 0,
                                 save_debug: bool = True, 
                                 upload_id: str = None) -> Tuple[str, List[Dict[str, Any]]]:
        logger.info(f"Extracting text with primary engine: {self.primary_engine_name}")
        tokens = self._extract_tokens(self.primary_engine, image_path, page, self.primary_engine_name)
        
        tokens = self.postprocessor.process_tokens(tokens)
        
        if self.retry_enabled:
            low_confidence_tokens = [
                t for t in tokens 
                if t.get("confidence", 1.0) < self.retry_threshold
            ]
            
            if low_confidence_tokens:
                logger.info(f"Found {len(low_confidence_tokens)} low-confidence tokens, retrying with fallback engines")
                tokens = self._retry_low_confidence_tokens(
                    tokens, low_confidence_tokens, image_path, page
                )
            
            # Apply ensemble voting for all tokens to improve accuracy
            logger.info(f"Applying ensemble voting across {len(self.fallback_engines)} fallback engines")
            tokens = self._apply_ensemble_voting(tokens, image_path, page)
        
        full_text = self._tokens_to_text(tokens)
        
        if save_debug and upload_id:
            self._save_token_debug(tokens, image_path, upload_id)
        
        return full_text, tokens
    
    def _extract_tokens(self, engine, image_path: str, page: int, 
                       engine_name: str) -> List[Dict[str, Any]]:
        try:
            raw_data = engine.extract_text_with_coordinates(image_path)
            tokens = []
            
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
                    'x0': normalized_bbox[0],
                    'y0': normalized_bbox[1],
                    'x1': normalized_bbox[2],
                    'y1': normalized_bbox[3],
                    'confidence': item['confidence'],
                    'page': page,
                    'engine': engine_name,
                    '_used_by': None
                }
                tokens.append(token)
            
            return tokens
            
        except Exception as e:
            logger.error(f"Token extraction failed with {engine_name}: {str(e)}")
            return []
    
    def _retry_low_confidence_tokens(self, all_tokens: List[Dict[str, Any]],
                                    low_conf_tokens: List[Dict[str, Any]],
                                    image_path: str, page: int) -> List[Dict[str, Any]]:
        if not self.fallback_engines:
            return all_tokens
        
        token_map = {id(t): t for t in all_tokens}
        
        for fallback_name, fallback_engine in self.fallback_engines.items():
            if not low_conf_tokens:
                break
            
            logger.info(f"Retrying {len(low_conf_tokens)} tokens with {fallback_name}")
            
            try:
                fallback_tokens = self._extract_tokens(
                    fallback_engine, image_path, page, fallback_name
                )
                
                replaced_count = 0
                for low_token in low_conf_tokens[:]:
                    best_match = self._find_matching_token(low_token, fallback_tokens)
                    
                    if best_match and best_match['confidence'] > low_token['confidence']:
                        token_map[id(low_token)].update(best_match)
                        low_conf_tokens.remove(low_token)
                        replaced_count += 1
                        logger.debug(f"Replaced token '{low_token['text']}' (conf: {low_token['confidence']:.2f}) "
                                   f"with '{best_match['text']}' (conf: {best_match['confidence']:.2f})")
                
                logger.info(f"Replaced {replaced_count} tokens using {fallback_name}")
                
            except Exception as e:
                logger.error(f"Fallback extraction failed with {fallback_name}: {str(e)}")
        
        return list(token_map.values())
    
    def _find_matching_token(self, target_token: Dict[str, Any],
                            candidate_tokens: List[Dict[str, Any]],
                            iou_threshold: float = 0.5) -> Optional[Dict[str, Any]]:
        target_bbox = target_token['bbox']
        best_match = None
        best_iou = 0
        
        for candidate in candidate_tokens:
            iou = self._calculate_iou(target_bbox, candidate['bbox'])
            if iou > iou_threshold and iou > best_iou:
                best_iou = iou
                best_match = candidate
        
        return best_match
    
    def _apply_ensemble_voting(self, primary_tokens: List[Dict[str, Any]],
                              image_path: str, page: int) -> List[Dict[str, Any]]:
        """Apply majority voting across all OCR engines for improved accuracy"""
        if not self.fallback_engines:
            return primary_tokens
        
        logger.info(f"Starting ensemble voting with {len(self.fallback_engines)} engines")
        
        # Collect results from all engines
        all_engine_results = {self.primary_engine_name: primary_tokens}
        
        for engine_name, engine in self.fallback_engines.items():
            try:
                fallback_tokens = self._extract_tokens(engine, image_path, page, engine_name)
                all_engine_results[engine_name] = fallback_tokens
                logger.info(f"Collected {len(fallback_tokens)} tokens from {engine_name}")
            except Exception as e:
                logger.warning(f"Failed to collect tokens from {engine_name}: {str(e)}")
        
        # Apply voting for each primary token
        voted_tokens = []
        for primary_token in primary_tokens:
            voted_token = self._vote_token(primary_token, all_engine_results)
            voted_tokens.append(voted_token)
        
        logger.info(f"Ensemble voting completed: {len(voted_tokens)} tokens processed")
        return voted_tokens
    
    def _vote_token(self, primary_token: Dict[str, Any],
                   all_engine_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Apply majority voting for a single token across all engines"""
        target_bbox = primary_token['bbox']
        text_votes = {}
        confidence_sum = 0
        vote_count = 0
        
        # Collect votes from all engines
        for engine_name, tokens in all_engine_results.items():
            matching_token = None
            best_iou = 0
            
            for token in tokens:
                iou = self._calculate_iou(target_bbox, token['bbox'])
                if iou > 0.5 and iou > best_iou:
                    best_iou = iou
                    matching_token = token
            
            if matching_token:
                text = matching_token['text'].strip()
                text_votes[text] = text_votes.get(text, 0) + 1
                confidence_sum += matching_token.get('confidence', 0.8)
                vote_count += 1
        
        # Determine winning text by majority vote
        if text_votes:
            winning_text = max(text_votes.items(), key=lambda x: x[1])[0]
            vote_percentage = (text_votes[winning_text] / vote_count * 100) if vote_count > 0 else 0
            
            if winning_text != primary_token['text']:
                logger.debug(f"Ensemble voting changed '{primary_token['text']}' → '{winning_text}' "
                           f"({vote_percentage:.0f}% agreement)")
            
            # Update token with voted text and average confidence
            voted_token = primary_token.copy()
            voted_token['text'] = winning_text
            voted_token['confidence'] = confidence_sum / vote_count if vote_count > 0 else primary_token.get('confidence', 0.8)
            voted_token['vote_count'] = vote_count
            voted_token['vote_agreement'] = vote_percentage
            
            return voted_token
        
        return primary_token
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        x_inter_min = max(x1_min, x2_min)
        y_inter_min = max(y1_min, y2_min)
        x_inter_max = min(x1_max, x2_max)
        y_inter_max = min(y1_max, y2_max)
        
        if x_inter_max < x_inter_min or y_inter_max < y_inter_min:
            return 0.0
        
        inter_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)
        
        bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
        bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = bbox1_area + bbox2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def _tokens_to_text(self, tokens: List[Dict[str, Any]]) -> str:
        if not tokens:
            return ""
        
        sorted_tokens = sorted(tokens, key=lambda t: (t['y0'], t['x0']))
        
        lines = []
        current_line = []
        current_y = None
        y_tolerance = 10
        
        for token in sorted_tokens:
            if current_y is None or abs(token['y0'] - current_y) < y_tolerance:
                current_line.append(token['text'])
                current_y = token['y0']
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [token['text']]
                current_y = token['y0']
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _save_token_debug(self, tokens: List[Dict[str, Any]], 
                         image_path: str, upload_id: str):
        try:
            debug_path = Path(self.config.get("preprocessing", {}).get("debug_output_path", "output/debug"))
            debug_path = debug_path / upload_id
            debug_path.mkdir(parents=True, exist_ok=True)
            
            config_version = self.config.get("config_version", "unknown").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(image_path).stem
            
            tokens_file = debug_path / f"tokens_{base_name}_v{config_version}_{timestamp}.json"
            
            def convert_to_serializable(obj):
                import numpy as np
                if isinstance(obj, (np.integer, np.int32, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float32, np.float64)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                return obj
            
            json_tokens = []
            for token in tokens:
                json_token = {
                    'text': token['text'],
                    'bbox': convert_to_serializable(token['bbox']),
                    'confidence': convert_to_serializable(token['confidence']),
                    'page': convert_to_serializable(token['page']),
                    'engine': token.get('engine', 'unknown')
                }
                if 'original_text' in token:
                    json_token['original_text'] = token['original_text']
                if 'postprocessed' in token:
                    json_token['postprocessed'] = token['postprocessed']
                json_tokens.append(json_token)
            
            debug_data = {
                'config_version': self.config.get('config_version'),
                'timestamp': timestamp,
                'image_path': image_path,
                'primary_engine': self.primary_engine_name,
                'total_tokens': len(tokens),
                'tokens': json_tokens
            }
            
            debug_data = convert_to_serializable(debug_data)
            
            with open(tokens_file, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved token debug info: {tokens_file}")
            
        except Exception as e:
            logger.error(f"Failed to save token debug info: {str(e)}")
