"""
OCR Processor Preprocessor
==========================

Preprocessor for extracting text from images using OCR.
"""

from typing import Dict, Any, Optional
import logging
from PIL import Image as PILImage
import io

from .base import Preprocessor

logger = logging.getLogger(__name__)


class OCRProcessor(Preprocessor):
    """
    Extract text from images using OCR.
    
    This preprocessor uses OCR to extract text from images and adds
    the extracted text to the data dictionary. Supports multiple OCR
    engines and confidence scoring.
    """
    
    def __init__(self, 
                 ocr_engine: str = 'tesseract',
                 confidence_threshold: float = 0.5,
                 language: str = 'eng',
                 preserve_original: bool = True):
        """
        Initialize OCRProcessor.
        
        Args:
            ocr_engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr')
            confidence_threshold: Minimum confidence score for text extraction
            language: Language code for OCR (e.g., 'eng', 'spa', 'fra')
            preserve_original: Whether to preserve original image in data
        """
        self.ocr_engine = ocr_engine.lower()
        self.confidence_threshold = confidence_threshold
        self.language = language
        self.preserve_original = preserve_original
        
        # Initialize OCR engine
        self._ocr_client = None
        self._initialize_ocr_engine()
        
        logger.debug(f"OCRProcessor initialized: engine={ocr_engine}, confidence={confidence_threshold}, lang={language}")
    
    def _initialize_ocr_engine(self):
        """Initialize the selected OCR engine."""
        try:
            if self.ocr_engine == 'tesseract':
                self._initialize_tesseract()
            elif self.ocr_engine == 'easyocr':
                self._initialize_easyocr()
            elif self.ocr_engine == 'paddleocr':
                self._initialize_paddleocr()
            else:
                raise ValueError(f"Unsupported OCR engine: {self.ocr_engine}")
        except ImportError as e:
            logger.warning(f"OCR engine {self.ocr_engine} not available: {e}")
            self._ocr_client = None
    
    def _initialize_tesseract(self):
        """Initialize Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            self._ocr_client = pytesseract
            logger.debug("Tesseract OCR initialized successfully")
        except ImportError:
            raise ImportError("pytesseract not installed. Install with: pip install pytesseract")
        except Exception as e:
            raise RuntimeError(f"Tesseract not found or not properly installed: {e}")
    
    def _initialize_easyocr(self):
        """Initialize EasyOCR."""
        try:
            import easyocr
            self._ocr_client = easyocr.Reader([self.language])
            logger.debug("EasyOCR initialized successfully")
        except ImportError:
            raise ImportError("easyocr not installed. Install with: pip install easyocr")
    
    def _initialize_paddleocr(self):
        """Initialize PaddleOCR."""
        try:
            from paddleocr import PaddleOCR
            self._ocr_client = PaddleOCR(use_angle_cls=True, lang=self.language)
            logger.debug("PaddleOCR initialized successfully")
        except ImportError:
            raise ImportError("paddleocr not installed. Install with: pip install paddleocr")
    
    @property
    def processor_name(self) -> str:
        """Return the processor name."""
        return f"ocr_processor_{self.ocr_engine}"
    
    def get_required_keys(self) -> list[str]:
        """OCR processor requires 'image' key."""
        return ['image']
    
    def can_process(self, data: Dict[str, Any]) -> bool:
        """
        Check if data contains a valid image and OCR is available.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data contains processable image and OCR is available
        """
        if self._ocr_client is None:
            logger.debug("OCR engine not available, cannot process")
            return False
        
        if 'image' not in data:
            return False
        
        image = data['image']
        return self._is_valid_image(image)
    
    def _is_valid_image(self, image) -> bool:
        """
        Check if image data is valid and processable.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            True if image is valid
        """
        try:
            if isinstance(image, str):
                # File path
                return len(image) > 0
            elif isinstance(image, PILImage.Image):
                # PIL Image
                return True
            elif isinstance(image, bytes):
                # Raw bytes
                return len(image) > 0
            else:
                return False
        except Exception:
            return False
    
    def _load_image(self, image) -> PILImage.Image:
        """
        Load image from various formats into PIL Image.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If image format is unsupported
            RuntimeError: If image loading fails
        """
        try:
            if isinstance(image, str):
                # Image file path
                return PILImage.open(image)
            elif isinstance(image, PILImage.Image):
                # Already a PIL Image
                return image
            elif isinstance(image, bytes):
                # Raw bytes
                return PILImage.open(io.BytesIO(image))
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {e}") from e
    
    def _extract_text_tesseract(self, image: PILImage.Image) -> Dict[str, Any]:
        """
        Extract text using Tesseract OCR.
        
        Args:
            image: PIL Image to process
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Get detailed OCR data with confidence scores
            ocr_data = self._ocr_client.image_to_data(
                image, 
                lang=self.language,
                output_type=self._ocr_client.Output.DICT
            )
            
            # Filter by confidence threshold
            filtered_text = []
            confidences = []
            
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) >= (self.confidence_threshold * 100):
                    text = ocr_data['text'][i].strip()
                    if text:
                        filtered_text.append(text)
                        confidences.append(int(conf))
            
            extracted_text = ' '.join(filtered_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'extracted_text': extracted_text,
                'confidence': avg_confidence / 100.0,
                'word_count': len(filtered_text),
                'engine': 'tesseract'
            }
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'word_count': 0,
                'engine': 'tesseract',
                'error': str(e)
            }
    
    def _extract_text_easyocr(self, image: PILImage.Image) -> Dict[str, Any]:
        """
        Extract text using EasyOCR.
        
        Args:
            image: PIL Image to process
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Convert PIL image to numpy array for EasyOCR
            import numpy as np
            image_array = np.array(image)
            
            # Perform OCR
            results = self._ocr_client.readtext(image_array)
            
            # Filter by confidence threshold
            filtered_text = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold:
                    filtered_text.append(text.strip())
                    confidences.append(confidence)
            
            extracted_text = ' '.join(filtered_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'extracted_text': extracted_text,
                'confidence': avg_confidence,
                'word_count': len(filtered_text),
                'engine': 'easyocr'
            }
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'word_count': 0,
                'engine': 'easyocr',
                'error': str(e)
            }
    
    def _extract_text_paddleocr(self, image: PILImage.Image) -> Dict[str, Any]:
        """
        Extract text using PaddleOCR.
        
        Args:
            image: PIL Image to process
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Convert PIL image to numpy array for PaddleOCR
            import numpy as np
            image_array = np.array(image)
            
            # Perform OCR
            results = self._ocr_client.ocr(image_array, cls=True)
            
            # Extract text and confidence scores
            filtered_text = []
            confidences = []
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        text = line[1][0] if isinstance(line[1], tuple) else str(line[1])
                        confidence = line[1][1] if isinstance(line[1], tuple) and len(line[1]) > 1 else 1.0
                        
                        if confidence >= self.confidence_threshold:
                            filtered_text.append(text.strip())
                            confidences.append(confidence)
            
            extracted_text = ' '.join(filtered_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'extracted_text': extracted_text,
                'confidence': avg_confidence,
                'word_count': len(filtered_text),
                'engine': 'paddleocr'
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR failed: {e}")
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'word_count': 0,
                'engine': 'paddleocr',
                'error': str(e)
            }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data by extracting text from images using OCR.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Data dictionary with extracted text added
            
        Raises:
            RuntimeError: If OCR processing fails
        """
        if not self.can_process(data):
            logger.debug("OCRProcessor: Cannot process data, skipping")
            return data
        
        try:
            # Make a copy to avoid modifying original
            processed_data = data.copy()
            
            # Load image
            image = self._load_image(data['image'])
            
            # Extract text using selected OCR engine
            if self.ocr_engine == 'tesseract':
                ocr_result = self._extract_text_tesseract(image)
            elif self.ocr_engine == 'easyocr':
                ocr_result = self._extract_text_easyocr(image)
            elif self.ocr_engine == 'paddleocr':
                ocr_result = self._extract_text_paddleocr(image)
            else:
                raise RuntimeError(f"Unsupported OCR engine: {self.ocr_engine}")
            
            # Add extracted text to data
            if ocr_result['extracted_text']:
                # Combine with existing text if present
                existing_text = processed_data.get('text', '')
                if existing_text:
                    processed_data['text'] = f"{existing_text} {ocr_result['extracted_text']}"
                else:
                    processed_data['text'] = ocr_result['extracted_text']
                
                # Add OCR metadata
                processed_data['_ocr_info'] = {
                    'engine': ocr_result['engine'],
                    'confidence': ocr_result['confidence'],
                    'word_count': ocr_result['word_count'],
                    'extracted_text_length': len(ocr_result['extracted_text'])
                }
                
                if 'error' in ocr_result:
                    processed_data['_ocr_info']['error'] = ocr_result['error']
                
                logger.debug(f"OCR extracted {ocr_result['word_count']} words with {ocr_result['confidence']:.2f} confidence")
            else:
                logger.debug("No text extracted from image")
                processed_data['_ocr_info'] = {
                    'engine': ocr_result['engine'],
                    'confidence': 0.0,
                    'word_count': 0,
                    'extracted_text_length': 0
                }
            
            # Optionally remove original image to save memory
            if not self.preserve_original:
                processed_data.pop('image', None)
                processed_data['_ocr_info']['original_image_removed'] = True
            
            # Add preprocessing metadata
            processed_data = self._add_preprocessing_metadata(processed_data)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise RuntimeError(f"OCR processing failed: {e}") from e