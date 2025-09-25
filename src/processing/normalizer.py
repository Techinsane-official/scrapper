import re
import hashlib
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from datetime import datetime
import json

class DataNormalizer:
    """Handles data normalization across different retailers"""
    
    @staticmethod
    def normalize_price(price_str: str) -> Optional[float]:
        """Normalize price strings to float values"""
        if not price_str:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize product titles"""
        if not title:
            return ""
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common retailer-specific prefixes/suffixes
        prefixes_to_remove = [
            r'^Amazon\.com: ',
            r'^Walmart\.com: ',
            r'^Target\.com: ',
            r'^Best Buy: ',
            r'^\[.*?\] ',
            r'^\(.*?\) '
        ]
        
        for prefix in prefixes_to_remove:
            normalized = re.sub(prefix, '', normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    @staticmethod
    def normalize_brand(brand: str) -> str:
        """Normalize brand names"""
        if not brand:
            return ""
        
        # Remove common brand suffixes
        suffixes_to_remove = [
            r' Brand$',
            r'\.com$',
            r' Inc\.?$',
            r' LLC\.?$',
            r' Corp\.?$',
            r' Ltd\.?$'
        ]
        
        normalized = brand.strip()
        for suffix in suffixes_to_remove:
            normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    @staticmethod
    def normalize_availability(availability: str) -> str:
        """Normalize availability status"""
        if not availability:
            return "unknown"
        
        availability_lower = availability.lower().strip()
        
        # Map various availability strings to standard values
        availability_map = {
            'in stock': 'in_stock',
            'available': 'in_stock',
            'in-stock': 'in_stock',
            'stock': 'in_stock',
            'out of stock': 'out_of_stock',
            'out-of-stock': 'out_of_stock',
            'unavailable': 'out_of_stock',
            'not available': 'out_of_stock',
            'pre-order': 'pre_order',
            'preorder': 'pre_order',
            'coming soon': 'pre_order',
            'limited stock': 'limited_stock',
            'low stock': 'limited_stock',
            'few left': 'limited_stock'
        }
        
        return availability_map.get(availability_lower, 'unknown')
    
    @staticmethod
    def normalize_dimensions(dimensions: Dict[str, Any]) -> Dict[str, float]:
        """Normalize product dimensions"""
        if not dimensions:
            return {}
        
        normalized = {}
        dimension_keys = ['length', 'width', 'height', 'weight']
        
        for key in dimension_keys:
            if key in dimensions:
                value = dimensions[key]
                if isinstance(value, str):
                    # Extract numeric value from string
                    numeric_match = re.search(r'(\d+\.?\d*)', value)
                    if numeric_match:
                        normalized[key] = float(numeric_match.group(1))
                elif isinstance(value, (int, float)):
                    normalized[key] = float(value)
        
        return normalized
    
    @staticmethod
    def normalize_specifications(specs: Dict[str, str]) -> Dict[str, str]:
        """Normalize product specifications"""
        if not specs:
            return {}
        
        normalized = {}
        
        for key, value in specs.items():
            # Normalize key names
            normalized_key = key.lower().strip()
            normalized_key = re.sub(r'\s+', ' ', normalized_key)
            
            # Normalize values
            normalized_value = value.strip()
            if normalized_value:
                normalized[normalized_key] = normalized_value
        
        return normalized

class ProductDeduplicator:
    """Handles product deduplication and matching"""
    
    def __init__(self):
        self.similarity_threshold = 0.85
        self.title_weight = 0.4
        self.brand_weight = 0.3
        self.price_weight = 0.2
        self.spec_weight = 0.1
    
    def calculate_similarity(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> float:
        """Calculate similarity score between two products"""
        scores = []
        
        # Title similarity
        title_sim = self._text_similarity(
            product1.get('title', ''),
            product2.get('title', '')
        )
        scores.append(title_sim * self.title_weight)
        
        # Brand similarity
        brand_sim = self._text_similarity(
            product1.get('brand', ''),
            product2.get('brand', '')
        )
        scores.append(brand_sim * self.brand_weight)
        
        # Price similarity
        price_sim = self._price_similarity(
            product1.get('current_price'),
            product2.get('current_price')
        )
        scores.append(price_sim * self.price_weight)
        
        # Specifications similarity
        spec_sim = self._specifications_similarity(
            product1.get('specifications', {}),
            product2.get('specifications', {})
        )
        scores.append(spec_sim * self.spec_weight)
        
        return sum(scores)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm1 = DataNormalizer.normalize_title(text1).lower()
        norm2 = DataNormalizer.normalize_title(text2).lower()
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _price_similarity(self, price1: Optional[float], price2: Optional[float]) -> float:
        """Calculate price similarity"""
        if not price1 or not price2:
            return 0.0
        
        # Calculate percentage difference
        diff = abs(price1 - price2) / max(price1, price2)
        
        # Convert to similarity score (0-1)
        return max(0, 1 - diff)
    
    def _specifications_similarity(self, specs1: Dict[str, str], specs2: Dict[str, str]) -> float:
        """Calculate specifications similarity"""
        if not specs1 or not specs2:
            return 0.0
        
        # Find common specification keys
        common_keys = set(specs1.keys()) & set(specs2.keys())
        if not common_keys:
            return 0.0
        
        # Calculate average similarity for common specs
        similarities = []
        for key in common_keys:
            sim = self._text_similarity(specs1[key], specs2[key])
            similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def find_duplicates(self, products: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find duplicate products in a list"""
        duplicates = []
        processed = set()
        
        for i, product1 in enumerate(products):
            if i in processed:
                continue
            
            duplicate_group = [product1]
            
            for j, product2 in enumerate(products[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self.calculate_similarity(product1, product2)
                if similarity >= self.similarity_threshold:
                    duplicate_group.append(product2)
                    processed.add(j)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
                processed.add(i)
        
        return duplicates
    
    def merge_duplicates(self, duplicate_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge duplicate products into a single product"""
        if not duplicate_group:
            return {}
        
        if len(duplicate_group) == 1:
            return duplicate_group[0]
        
        # Start with the product with highest data quality score
        best_product = max(duplicate_group, key=lambda p: p.get('data_quality_score', 0))
        merged = best_product.copy()
        
        # Merge additional data from other products
        for product in duplicate_group:
            if product == best_product:
                continue
            
            # Merge additional images
            if 'additional_images' in product:
                merged_images = merged.get('additional_images', [])
                for img in product['additional_images']:
                    if img not in merged_images:
                        merged_images.append(img)
                merged['additional_images'] = merged_images
            
            # Merge features
            if 'features' in product:
                merged_features = merged.get('features', [])
                for feature in product['features']:
                    if feature not in merged_features:
                        merged_features.append(feature)
                merged['features'] = merged_features
            
            # Merge specifications (keep best product's specs as primary)
            if 'specifications' in product:
                merged_specs = merged.get('specifications', {})
                for key, value in product['specifications'].items():
                    if key not in merged_specs and value:
                        merged_specs[key] = value
                merged['specifications'] = merged_specs
        
        # Update metadata
        merged['duplicate_count'] = len(duplicate_group)
        merged['merged_at'] = datetime.now().isoformat()
        
        return merged

class DataQualityScorer:
    """Calculates data quality scores for products"""
    
    @staticmethod
    def calculate_quality_score(product: Dict[str, Any]) -> float:
        """Calculate comprehensive data quality score"""
        score = 0.0
        max_score = 1.0
        
        # Core information (40% of score)
        if product.get('title'):
            score += 0.15
        if product.get('brand'):
            score += 0.10
        if product.get('description') or product.get('bullet_points'):
            score += 0.10
        if product.get('category'):
            score += 0.05
        
        # Pricing & Availability (25% of score)
        if product.get('current_price'):
            score += 0.15
        if product.get('availability') != 'unknown':
            score += 0.10
        
        # Media (15% of score)
        if product.get('primary_image_url'):
            score += 0.10
        if product.get('additional_images'):
            score += 0.05
        
        # Specifications & Features (15% of score)
        if product.get('specifications'):
            score += 0.08
        if product.get('features'):
            score += 0.07
        
        # Social Proof (5% of score)
        if product.get('rating'):
            score += 0.03
        if product.get('review_count'):
            score += 0.02
        
        return min(score, max_score)
    
    @staticmethod
    def get_quality_grade(score: float) -> str:
        """Get quality grade based on score"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

class CurationEngine:
    """Handles product curation and filtering"""
    
    def __init__(self):
        self.default_rules = [
            {
                'name': 'minimum_rating',
                'condition': {'min_rating': 4.0},
                'action': 'include',
                'priority': 1
            },
            {
                'name': 'minimum_reviews',
                'condition': {'min_reviews': 10},
                'action': 'include',
                'priority': 2
            },
            {
                'name': 'in_stock_only',
                'condition': {'availability': 'in_stock'},
                'action': 'include',
                'priority': 3
            },
            {
                'name': 'exclude_adult_content',
                'condition': {'exclude_categories': ['adult', 'mature']},
                'action': 'exclude',
                'priority': 1
            }
        ]
    
    def apply_curation_rules(self, products: List[Dict[str, Any]], rules: List[Dict] = None) -> List[Dict[str, Any]]:
        """Apply curation rules to filter products"""
        if rules is None:
            rules = self.default_rules
        
        curated_products = []
        
        for product in products:
            curation_result = self._evaluate_product(product, rules)
            if curation_result['action'] == 'include':
                product['is_curated'] = True
                product['curation_score'] = curation_result['score']
                product['curation_reason'] = curation_result['reason']
                curated_products.append(product)
            elif curation_result['action'] == 'flag':
                product['is_curated'] = False
                product['curation_score'] = curation_result['score']
                product['curation_reason'] = curation_result['reason']
                curated_products.append(product)
        
        return curated_products
    
    def _evaluate_product(self, product: Dict[str, Any], rules: List[Dict]) -> Dict[str, Any]:
        """Evaluate a single product against curation rules"""
        score = 0.0
        reasons = []
        
        for rule in sorted(rules, key=lambda x: x['priority']):
            if self._check_condition(product, rule['condition']):
                if rule['action'] == 'include':
                    score += 1.0
                    reasons.append(f"Passed: {rule['name']}")
                elif rule['action'] == 'exclude':
                    return {
                        'action': 'exclude',
                        'score': 0.0,
                        'reason': f"Excluded by: {rule['name']}"
                    }
                elif rule['action'] == 'flag':
                    score += 0.5
                    reasons.append(f"Flagged: {rule['name']}")
        
        # Determine final action
        if score >= 2.0:
            action = 'include'
        elif score >= 1.0:
            action = 'flag'
        else:
            action = 'exclude'
        
        return {
            'action': action,
            'score': score / len(rules) if rules else 0.0,
            'reason': '; '.join(reasons) if reasons else 'No rules matched'
        }
    
    def _check_condition(self, product: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Check if product meets a condition"""
        for key, value in condition.items():
            if key == 'min_rating':
                if not product.get('rating') or product['rating'] < value:
                    return False
            elif key == 'min_reviews':
                if not product.get('review_count') or product['review_count'] < value:
                    return False
            elif key == 'availability':
                if product.get('availability') != value:
                    return False
            elif key == 'exclude_categories':
                category = product.get('category', '').lower()
                if any(excluded in category for excluded in value):
                    return False
        
        return True
