import cv2
import numpy as np
import numpy as np
from PIL import Image
from PIL import Image
import logging
import logging
from pathlib import Path
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from datetime import datetime


logger = logging.getLogger(__name__)

class ImagePreprocessor:
    
    def __init__(self, config: Dict[str, Any], template: str = "default"):
        self.config = config
        self.template = template
        self.preprocessing_config = self._get_preprocessing_config()
        self.steps_config = self.preprocessing_config.get("steps", {})
        
    def _get_preprocessing_config(self) -> Dict[str, Any]:
        base_config = self.config.get("preprocessing", {})
        
        template_config = self.config.get("templates", {}).get(self.template, {})
        if "preprocessing" in template_config:
            template_preprocessing = template_config["preprocessing"]
            
            if "steps" in template_preprocessing:
                base_steps = base_config.get("steps", {})
                template_steps = template_preprocessing["steps"]
                
                for step_name, step_config in template_steps.items():
                    if step_name in base_steps:
                        base_steps[step_name].update(step_config)
                    else:
                        base_steps[step_name] = step_config
        
        return base_config
    
    def preprocess(self, image_path: str, save_debug: bool = True, 
                   upload_id: str = None) -> Tuple[str, Dict[str, Any]]:
        if not self.preprocessing_config.get("enabled", True):
            logger.info("Preprocessing disabled, returning original image")
            return image_path, {"preprocessing_applied": False}
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            original_image = image.copy()
            metadata = {
                "original_shape": image.shape,
                "config_version": self.config.get("config_version", "unknown"),
                "template": self.template,
                "steps_applied": [],
                "timestamp": datetime.now().isoformat()
            }
            
            steps = self._get_ordered_steps()
            
            for step_name, step_func in steps:
                step_config = self.steps_config.get(step_name, {})
                if step_config.get("enabled", False):
                    logger.info(f"Applying preprocessing step: {step_name}")
                    image = step_func(image, step_config)
                    metadata["steps_applied"].append(step_name)
            
            preprocessed_path = self._save_preprocessed_image(
                image, image_path, upload_id, metadata
            )
            
            if save_debug and self.preprocessing_config.get("save_debug_artifacts", True):
                self._save_debug_artifacts(
                    original_image, image, image_path, upload_id, metadata
                )
            
            metadata["preprocessed_path"] = preprocessed_path
            return preprocessed_path, metadata
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            return image_path, {"preprocessing_applied": False, "error": str(e)}
    
    def _get_ordered_steps(self):
        steps_map = {
            "grayscale": self._apply_grayscale,
            "denoise": self._apply_denoise,
            "contrast_enhancement": self._apply_contrast_enhancement,
            "sharpening": self._apply_sharpening,
            "binarization": self._apply_binarization,
            "morphology": self._apply_morphology
        }
        
        ordered = []
        for step_name, step_func in steps_map.items():
            if step_name in self.steps_config:
                order = self.steps_config[step_name].get("order", 999)
                ordered.append((order, step_name, step_func))
        
        ordered.sort(key=lambda x: x[0])
        return [(name, func) for _, name, func in ordered]
    
    def _apply_grayscale(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _apply_denoise(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        method = config.get("method", "bilateral")
        
        if method == "bilateral":
            d = config.get("bilateral_d", 9)
            sigma_color = config.get("bilateral_sigma_color", 75)
            sigma_space = config.get("bilateral_sigma_space", 75)
            
            if len(image.shape) == 2:
                return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
            else:
                return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        elif method == "median":
            ksize = config.get("median_ksize", 3)
            return cv2.medianBlur(image, ksize)
        
        return image
    
    def _apply_contrast_enhancement(self, image: np.ndarray, 
                                    config: Dict[str, Any]) -> np.ndarray:
        method = config.get("method", "clahe")
        
        if method == "clahe":
            clip_limit = config.get("clahe_clip_limit", 2.0)
            tile_grid_size = tuple(config.get("clahe_tile_grid_size", [8, 8]))
            
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            return clahe.apply(image)
        
        return image
    
    def _apply_sharpening(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        kernel_size = config.get("kernel_size", 3)
        sigma = config.get("sigma", 1.0)
        amount = config.get("amount", 1.5)
        
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
        
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        
        return sharpened
    
    def _apply_binarization(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        method = config.get("method", "adaptive")
        
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if method == "adaptive":
            adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C \
                if config.get("adaptive_method") == "gaussian" \
                else cv2.ADAPTIVE_THRESH_MEAN_C
            
            block_size = config.get("block_size", 11)
            c = config.get("c", 2)
            
            return cv2.adaptiveThreshold(
                image, 255, adaptive_method, 
                cv2.THRESH_BINARY, block_size, c
            )
        
        elif method == "otsu" or config.get("otsu_enabled", False):
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        
        return image
    
    def _apply_morphology(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        operation = config.get("operation", "close")
        kernel_shape = config.get("kernel_shape", "rect")
        kernel_size = tuple(config.get("kernel_size", [2, 2]))
        
        if kernel_shape == "rect":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        elif kernel_shape == "ellipse":
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_size)
        
        if operation == "close":
            return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        elif operation == "open":
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        elif operation == "dilate":
            return cv2.dilate(image, kernel)
        elif operation == "erode":
            return cv2.erode(image, kernel)
        
        return image
    
    def _save_preprocessed_image(self, image: np.ndarray, original_path: str,
                                 upload_id: str, metadata: Dict[str, Any]) -> str:
        original_path_obj = Path(original_path)
        
        if upload_id:
            output_dir = Path("document-extraction-poc/uploads/processed") / upload_id
        else:
            output_dir = original_path_obj.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config_version = metadata.get("config_version", "unknown").replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"preprocessed_{original_path_obj.stem}_v{config_version}_{timestamp}.png"
        
        output_path = output_dir / filename
        cv2.imwrite(str(output_path), image)
        
        logger.info(f"Saved preprocessed image: {output_path}")
        return str(output_path)
    
    def _save_debug_artifacts(self, original: np.ndarray, preprocessed: np.ndarray,
                             original_path: str, upload_id: str, 
                             metadata: Dict[str, Any]) -> None:
        try:
            debug_path = Path(self.preprocessing_config.get("debug_output_path", "output/debug"))
            
            if upload_id:
                debug_path = debug_path / upload_id
            
            debug_path.mkdir(parents=True, exist_ok=True)
            
            config_version = metadata.get("config_version", "unknown").replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(original_path).stem
            
            original_file = debug_path / f"original_{base_name}_v{config_version}_{timestamp}.png"
            cv2.imwrite(str(original_file), original)
            
            preprocessed_file = debug_path / f"preprocessed_{base_name}_v{config_version}_{timestamp}.png"
            cv2.imwrite(str(preprocessed_file), preprocessed)
            
            import json
            metadata_file = debug_path / f"metadata_{base_name}_v{config_version}_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved debug artifacts to: {debug_path}")
            
        except Exception as e:
            logger.error(f"Failed to save debug artifacts: {str(e)}")
