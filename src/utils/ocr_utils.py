"""
OCR Utilities - Shared OCR processing functions for financial documents

Provides optimized OCR capabilities for:
- Invoice processing and data extraction
- Receipt recognition and parsing
- Financial document digitization
- Multi-format support (PDF, images)
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF
import io
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import re


class DocumentPreprocessor:
    """Advanced document preprocessing for improved OCR accuracy."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def enhance_image_quality(self, image: np.ndarray) -> np.ndarray:
        """Apply comprehensive image enhancement for better OCR results."""
        # Convert to PIL for enhanced processing
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.5)

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(2.0)

        # Apply slight blur to reduce noise
        pil_image = pil_image.filter(ImageFilter.MedianFilter(size=3))

        # Convert back to OpenCV format
        enhanced = np.array(pil_image)
        if len(enhanced.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)

        return enhanced

    def detect_and_correct_skew(self, image: np.ndarray) -> np.ndarray:
        """Detect and correct document skew angle."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Use Hough line transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

        if lines is not None:
            angles = []
            for rho, theta in lines[:10]:  # Use top 10 lines
                angle = theta * 180 / np.pi
                # Convert to angle relative to horizontal
                if angle > 90:
                    angle = angle - 180
                angles.append(angle)

            # Calculate median angle for stability
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # Only correct if significant skew
                    return self._rotate_image(image, -median_angle)

        return image

    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by specified angle."""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        # Calculate rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Calculate new dimensions
        cos_angle = abs(rotation_matrix[0, 0])
        sin_angle = abs(rotation_matrix[0, 1])
        new_w = int((h * sin_angle) + (w * cos_angle))
        new_h = int((h * cos_angle) + (w * sin_angle))

        # Adjust rotation matrix for new dimensions
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]

        # Perform rotation
        rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h),
                                borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from document image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

        # Apply Gaussian blur to reduce remaining noise
        cleaned = cv2.GaussianBlur(cleaned, (3, 3), 0)

        return cleaned

    def enhance_text_regions(self, image: np.ndarray) -> np.ndarray:
        """Enhance text regions specifically for better OCR."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Apply adaptive threshold to enhance text
        enhanced = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Apply morphological opening to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel)

        return enhanced


class TextExtractor:
    """Optimized text extraction with multiple OCR strategies."""

    def __init__(self):
        self.preprocessor = DocumentPreprocessor()
        self.logger = logging.getLogger(__name__)

    def extract_from_image(self, image: np.ndarray, config: Optional[str] = None) -> Dict[str, Any]:
        """Extract text from image using optimized OCR pipeline."""
        try:
            # Apply preprocessing
            enhanced = self.preprocessor.enhance_image_quality(image)
            deskewed = self.preprocessor.detect_and_correct_skew(enhanced)
            denoised = self.preprocessor.remove_noise(deskewed)
            text_enhanced = self.preprocessor.enhance_text_regions(denoised)

            # Configure Tesseract for document processing
            if not config:
                config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-/$#@()[]{}%& '

            # Extract text with confidence scores
            text = pytesseract.image_to_string(text_enhanced, config=config)

            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(text_enhanced, config=config, output_type=pytesseract.Output.DICT)

            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100,  # Normalize to 0-1
                'word_count': len(text.split()),
                'processing_method': 'enhanced_ocr',
                'ocr_data': ocr_data
            }

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e)
            }

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF with fallback to OCR for image-based PDFs."""
        results = {
            'pages': [],
            'total_text': '',
            'extraction_method': 'hybrid',
            'page_count': 0
        }

        try:
            doc = fitz.open(pdf_path)
            results['page_count'] = len(doc)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_result = {'page_number': page_num + 1}

                # Try direct text extraction first
                direct_text = page.get_text().strip()

                if direct_text and len(direct_text) > 50:  # Sufficient text found
                    page_result.update({
                        'text': direct_text,
                        'confidence': 1.0,
                        'method': 'direct_extraction'
                    })
                else:
                    # Fallback to OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution
                    img_data = pix.tobytes("ppm")
                    image = Image.open(io.BytesIO(img_data))
                    img_array = np.array(image)

                    ocr_result = self.extract_from_image(img_array)
                    page_result.update({
                        'text': ocr_result['text'],
                        'confidence': ocr_result['confidence'],
                        'method': 'ocr_extraction'
                    })

                results['pages'].append(page_result)
                results['total_text'] += page_result['text'] + '\n'

            doc.close()
            return results

        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {e}")
            return {
                'error': str(e),
                'total_text': '',
                'pages': []
            }

    def extract_structured_data(self, image: np.ndarray, data_types: List[str]) -> Dict[str, List[str]]:
        """Extract specific data types from document (amounts, dates, etc.)."""
        # First extract all text
        extraction_result = self.extract_from_image(image)
        text = extraction_result['text']

        structured_data = {}

        for data_type in data_types:
            if data_type == 'amounts':
                structured_data['amounts'] = self._extract_amounts(text)
            elif data_type == 'dates':
                structured_data['dates'] = self._extract_dates(text)
            elif data_type == 'emails':
                structured_data['emails'] = self._extract_emails(text)
            elif data_type == 'phone_numbers':
                structured_data['phone_numbers'] = self._extract_phone_numbers(text)
            elif data_type == 'addresses':
                structured_data['addresses'] = self._extract_addresses(text)

        return structured_data

    def _extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text."""
        patterns = [
            r'\$[\d,]+\.?\d*',  # $123.45, $1,234
            r'[\d,]+\.\d{2}',   # 123.45
            r'USD\s*[\d,]+\.?\d*',  # USD 123.45
        ]

        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            amounts.extend(matches)

        return list(set(amounts))  # Remove duplicates

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        patterns = [
            r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',  # MM/DD/YYYY, MM-DD-YYYY
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{2,4}',  # DD Month YYYY
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{2,4}'  # Month DD, YYYY
        ]

        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if isinstance(matches[0], tuple) if matches else False:
                dates.extend([' '.join(match) for match in matches])
            else:
                dates.extend(matches)

        return list(set(dates))

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)

    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        patterns = [
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',    # 123-456-7890
            r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-123-456-7890
        ]

        phone_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)

        return list(set(phone_numbers))

    def _extract_addresses(self, text: str) -> List[str]:
        """Extract addresses from text."""
        # Simple address pattern - can be enhanced
        pattern = r'\d+\s+[A-Za-z\s.,#-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Circle|Cir|Plaza|Pl).*?(?=\n|$)'

        addresses = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        return [addr.strip() for addr in addresses]


class DocumentLayoutAnalyzer:
    """Analyze document layout to improve field extraction."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect and classify text regions in document."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Apply morphological operations to detect text blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        dilated = cv2.dilate(gray, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        text_regions = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out very small regions
            if w > 50 and h > 20:
                region = {
                    'id': i,
                    'bbox': (x, y, w, h),
                    'area': w * h,
                    'aspect_ratio': w / h,
                    'position': self._classify_position(x, y, image.shape[1], image.shape[0])
                }
                text_regions.append(region)

        # Sort by reading order (top to bottom, left to right)
        text_regions.sort(key=lambda r: (r['bbox'][1], r['bbox'][0]))

        return text_regions

    def _classify_position(self, x: int, y: int, img_width: int, img_height: int) -> str:
        """Classify position of text region in document."""
        # Divide document into regions
        h_third = img_height / 3
        w_third = img_width / 3

        if y < h_third:
            if x < w_third:
                return 'top_left'
            elif x < 2 * w_third:
                return 'top_center'
            else:
                return 'top_right'
        elif y < 2 * h_third:
            if x < w_third:
                return 'middle_left'
            elif x < 2 * w_third:
                return 'middle_center'
            else:
                return 'middle_right'
        else:
            if x < w_third:
                return 'bottom_left'
            elif x < 2 * w_third:
                return 'bottom_center'
            else:
                return 'bottom_right'

    def extract_region_text(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract text from specific regions."""
        extractor = TextExtractor()
        region_texts = {}

        for region in regions:
            x, y, w, h = region['bbox']
            roi = image[y:y+h, x:x+w]

            result = extractor.extract_from_image(roi)
            region_texts[f"region_{region['id']}_{region['position']}"] = result['text']

        return region_texts


def create_ocr_config(document_type: str = 'invoice') -> str:
    """Create optimized Tesseract configuration for specific document types."""
    base_config = '--oem 3'

    if document_type == 'invoice':
        # Optimized for invoices with mixed text and numbers
        return f'{base_config} --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-/$#@()[]{{}}%& '

    elif document_type == 'receipt':
        # Optimized for receipts (often have poor print quality)
        return f'{base_config} --psm 6 -c preserve_interword_spaces=1'

    elif document_type == 'bank_statement':
        # Optimized for tabular data
        return f'{base_config} --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-$()[]{{}}%& '

    elif document_type == 'check':
        # Optimized for checks with specific layouts
        return f'{base_config} --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-/$& '

    else:
        # General document processing
        return f'{base_config} --psm 6'


def batch_process_documents(file_paths: List[str], output_dir: str = 'processed_docs') -> Dict[str, Any]:
    """Process multiple documents in batch for improved efficiency."""
    results = {
        'total_files': len(file_paths),
        'successfully_processed': 0,
        'failed': 0,
        'processing_times': [],
        'files': []
    }

    Path(output_dir).mkdir(exist_ok=True)
    extractor = TextExtractor()

    for file_path in file_paths:
        file_result = {'file_path': file_path}
        start_time = cv2.getTickCount()

        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.pdf':
                result = extractor.extract_from_pdf(file_path)
                file_result['text'] = result['total_text']
                file_result['method'] = 'pdf_extraction'
                file_result['page_count'] = result['page_count']

            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                image = cv2.imread(file_path)
                result = extractor.extract_from_image(image)
                file_result['text'] = result['text']
                file_result['confidence'] = result['confidence']
                file_result['method'] = 'image_ocr'

            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            # Save extracted text
            output_file = Path(output_dir) / f"{Path(file_path).stem}_extracted.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(file_result['text'])

            file_result['output_file'] = str(output_file)
            file_result['success'] = True
            results['successfully_processed'] += 1

        except Exception as e:
            file_result['success'] = False
            file_result['error'] = str(e)
            results['failed'] += 1

        # Calculate processing time
        processing_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        file_result['processing_time_seconds'] = round(processing_time, 2)
        results['processing_times'].append(processing_time)

        results['files'].append(file_result)

    # Calculate summary statistics
    if results['processing_times']:
        results['avg_processing_time'] = round(sum(results['processing_times']) / len(results['processing_times']), 2)
        results['total_processing_time'] = round(sum(results['processing_times']), 2)

    return results