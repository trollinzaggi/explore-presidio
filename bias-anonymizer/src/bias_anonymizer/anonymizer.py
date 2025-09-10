"""
Main anonymizer module for processing JSON data.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from pathlib import Path
import copy
from collections import defaultdict

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from .config import AnonymizerConfig
from .bias_recognizers import BiasRecognizerFactory
from .exceptions import AnonymizerException, ValidationError
from .utils import JsonPath, deep_get, deep_set

logger = logging.getLogger(__name__)


class JSONAnonymizer:
    """
    Main class for anonymizing JSON data with bias and PII detection.
    
    This class provides comprehensive anonymization capabilities for structured JSON data,
    detecting both PII (Personal Identifiable Information) and bias-inducing terms.
    """
    
    def __init__(self, config: Optional[AnonymizerConfig] = None):
        """
        Initialize the JSON Anonymizer.
        
        Args:
            config: Configuration object for the anonymizer. If None, uses defaults.
        """
        self.config = config or AnonymizerConfig()
        self._setup_engines()
        self._stats = defaultdict(int)
        
    def _setup_engines(self):
        """Set up Presidio analyzer and anonymizer engines."""
        # Initialize analyzer
        self.analyzer = AnalyzerEngine()
        
        # Initialize anonymizer
        self.anonymizer = AnonymizerEngine()
        
        # Add custom recognizers
        if self.config.detect_bias:
            self._add_bias_recognizers()
        
        if self.config.custom_recognizers:
            self._add_custom_recognizers()
    
    def _add_bias_recognizers(self):
        """Add bias word recognizers to the analyzer."""
        factory = BiasRecognizerFactory()
        
        if self.config.bias_categories:
            # Add recognizers for specific categories
            for category in self.config.bias_categories:
                recognizer = factory.create_recognizer(category)
                if recognizer:
                    self.analyzer.registry.add_recognizer(recognizer)
        else:
            # Add comprehensive recognizer for all categories
            recognizer = factory.create_comprehensive_recognizer()
            self.analyzer.registry.add_recognizer(recognizer)
    
    def _add_custom_recognizers(self):
        """Add custom recognizers from configuration."""
        for recognizer in self.config.custom_recognizers:
            self.analyzer.registry.add_recognizer(recognizer)
    
    def anonymize(self,
                  data: Union[Dict, str],
                  keys_to_anonymize: Optional[List[str]] = None,
                  preserve_structure: bool = True) -> Union[Dict, str]:
        """
        Anonymize JSON data by removing bias and PII.
        
        Args:
            data: JSON data as dict or JSON string
            keys_to_anonymize: Optional list of keys to anonymize (dot notation supported)
                               If None, anonymizes all string values
            preserve_structure: Whether to preserve the JSON structure
            
        Returns:
            Anonymized JSON data in the same format as input
            
        Raises:
            ValidationError: If input data is invalid
            AnonymizerException: If anonymization fails
        """
        # Parse input if string
        input_is_string = isinstance(data, str)
        if input_is_string:
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON input: {e}")
        
        # Validate input
        if not isinstance(data, dict):
            raise ValidationError("Input must be a JSON object (dict)")
        
        # Create a deep copy to avoid modifying original
        result = copy.deepcopy(data)
        
        # Determine keys to process
        if keys_to_anonymize:
            keys_to_process = self._parse_key_paths(keys_to_anonymize)
        else:
            keys_to_process = None  # Process all
        
        # Anonymize the data
        self._anonymize_recursive(result, keys_to_process, current_path="")
        
        # Return in original format
        if input_is_string:
            return json.dumps(result, indent=2)
        return result
    
    def _parse_key_paths(self, keys: List[str]) -> Set[str]:
        """
        Parse key paths and expand wildcards.
        
        Args:
            keys: List of key paths (supports dot notation and wildcards)
            
        Returns:
            Set of normalized key paths
        """
        parsed_keys = set()
        for key in keys:
            # Normalize path separators
            key = key.replace("/", ".").replace("->", ".")
            parsed_keys.add(key)
        return parsed_keys
    
    def _should_process_path(self, current_path: str, keys_to_process: Optional[Set[str]]) -> bool:
        """
        Determine if a path should be processed.
        
        Args:
            current_path: Current path in the JSON structure
            keys_to_process: Set of paths to process, None means process all
            
        Returns:
            True if the path should be processed
        """
        if keys_to_process is None:
            return True  # Process all paths
        
        # Check exact match
        if current_path in keys_to_process:
            return True
        
        # Check if any key starts with current path (for nested processing)
        for key in keys_to_process:
            if key.startswith(current_path + ".") or current_path.startswith(key):
                return True
        
        return False
    
    def _anonymize_recursive(self,
                            data: Any,
                            keys_to_process: Optional[Set[str]],
                            current_path: str):
        """
        Recursively anonymize JSON data.
        
        Args:
            data: Current data node
            keys_to_process: Keys to process
            current_path: Current path in JSON structure
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                if self._should_process_path(new_path, keys_to_process):
                    if isinstance(value, str):
                        # Anonymize string value
                        data[key] = self._anonymize_text(value)
                        self._stats['strings_processed'] += 1
                    elif isinstance(value, (dict, list)):
                        # Recurse into nested structures
                        self._anonymize_recursive(value, keys_to_process, new_path)
                        self._stats['nested_structures'] += 1
                        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_path = f"{current_path}[{i}]"
                
                if self._should_process_path(item_path, keys_to_process) or \
                   self._should_process_path(current_path, keys_to_process):
                    if isinstance(item, str):
                        # Anonymize string value
                        data[i] = self._anonymize_text(item)
                        self._stats['strings_processed'] += 1
                    elif isinstance(item, (dict, list)):
                        # Recurse into nested structures
                        self._anonymize_recursive(item, keys_to_process, item_path)
                        self._stats['nested_structures'] += 1
    
    def _anonymize_text(self, text: str) -> str:
        """
        Anonymize a text string.
        
        Args:
            text: Text to anonymize
            
        Returns:
            Anonymized text
        """
        if not text or not text.strip():
            return text
        
        # Analyze text for PII and bias
        results = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            score_threshold=self.config.confidence_threshold
        )
        
        # Track statistics
        for result in results:
            self._stats[f'entity_{result.entity_type}'] += 1
        
        # Get operators for anonymization
        operators = self._get_operators(results)
        
        # Anonymize the text
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        
        return anonymized.text
    
    def _get_operators(self, results: List[RecognizerResult]) -> Dict[str, OperatorConfig]:
        """
        Get anonymization operators for detected entities.
        
        Args:
            results: List of detected entities
            
        Returns:
            Dictionary of operators per entity type
        """
        operators = {}
        
        for result in results:
            entity_type = result.entity_type
            
            # Check if custom operator defined
            if entity_type in self.config.operators:
                operator_type = self.config.operators[entity_type]
            elif "_BIAS" in entity_type or entity_type == "BIAS_INDICATOR":
                # Default for bias indicators is to remove
                operator_type = "remove"
            else:
                # Use default operator
                operator_type = self.config.operators.get("DEFAULT", "replace")
            
            # Create operator config
            if operator_type == "replace":
                replacement = self.config.replacements.get(
                    entity_type,
                    self.config.replacements.get("DEFAULT", f"[{entity_type}]")
                )
                operators[entity_type] = OperatorConfig("replace", {"new_value": replacement})
            elif operator_type == "remove":
                operators[entity_type] = OperatorConfig("replace", {"new_value": ""})
            elif operator_type == "mask":
                operators[entity_type] = OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 10,
                    "from_end": False
                })
            elif operator_type == "hash":
                operators[entity_type] = OperatorConfig("hash", {"hash_type": "sha256"})
            elif operator_type == "encrypt":
                operators[entity_type] = OperatorConfig("encrypt", {"key": self.config.encryption_key})
            elif operator_type == "keep":
                operators[entity_type] = OperatorConfig("keep", {})
            else:
                # Default to replace
                operators[entity_type] = OperatorConfig("replace", {"new_value": f"[{entity_type}]"})
        
        return operators
    
    def analyze(self,
                data: Union[Dict, str],
                keys_to_analyze: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze JSON data for bias and PII without anonymizing.
        
        Args:
            data: JSON data to analyze
            keys_to_analyze: Optional list of keys to analyze
            
        Returns:
            Analysis report with detected entities and statistics
        """
        # Parse input if string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON input: {e}")
        
        # Determine keys to process
        if keys_to_analyze:
            keys_to_process = self._parse_key_paths(keys_to_analyze)
        else:
            keys_to_process = None
        
        # Analyze the data
        analysis_results = {
            "total_entities": 0,
            "entities_by_type": defaultdict(int),
            "entities_by_path": defaultdict(list),
            "bias_categories": set(),
            "pii_types": set(),
            "detailed_findings": []
        }
        
        self._analyze_recursive(data, keys_to_process, "", analysis_results)
        
        # Convert sets to lists for JSON serialization
        analysis_results["bias_categories"] = list(analysis_results["bias_categories"])
        analysis_results["pii_types"] = list(analysis_results["pii_types"])
        analysis_results["entities_by_type"] = dict(analysis_results["entities_by_type"])
        analysis_results["entities_by_path"] = dict(analysis_results["entities_by_path"])
        
        return analysis_results
    
    def _analyze_recursive(self,
                          data: Any,
                          keys_to_process: Optional[Set[str]],
                          current_path: str,
                          results: Dict):
        """
        Recursively analyze JSON data.
        
        Args:
            data: Current data node
            keys_to_process: Keys to process
            current_path: Current path
            results: Results dictionary to populate
        """
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                if self._should_process_path(new_path, keys_to_process):
                    if isinstance(value, str):
                        self._analyze_text_value(value, new_path, results)
                    elif isinstance(value, (dict, list)):
                        self._analyze_recursive(value, keys_to_process, new_path, results)
                        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_path = f"{current_path}[{i}]"
                
                if self._should_process_path(item_path, keys_to_process) or \
                   self._should_process_path(current_path, keys_to_process):
                    if isinstance(item, str):
                        self._analyze_text_value(item, item_path, results)
                    elif isinstance(item, (dict, list)):
                        self._analyze_recursive(item, keys_to_process, item_path, results)
    
    def _analyze_text_value(self, text: str, path: str, results: Dict):
        """
        Analyze a text value for entities.
        
        Args:
            text: Text to analyze
            path: JSON path of the text
            results: Results dictionary to populate
        """
        if not text or not text.strip():
            return
        
        # Analyze text
        entities = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            score_threshold=self.config.confidence_threshold
        )
        
        for entity in entities:
            results["total_entities"] += 1
            results["entities_by_type"][entity.entity_type] += 1
            results["entities_by_path"][path].append({
                "type": entity.entity_type,
                "text": text[entity.start:entity.end],
                "confidence": entity.score
            })
            
            # Categorize as bias or PII
            if "_BIAS" in entity.entity_type or entity.entity_type == "BIAS_INDICATOR":
                category = entity.entity_type.replace("_BIAS", "").lower()
                results["bias_categories"].add(category)
            else:
                results["pii_types"].add(entity.entity_type)
            
            # Add to detailed findings
            results["detailed_findings"].append({
                "path": path,
                "entity_type": entity.entity_type,
                "text": text[entity.start:entity.end],
                "position": (entity.start, entity.end),
                "confidence": entity.score
            })
    
    def anonymize_file(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      keys_to_anonymize: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Anonymize a JSON file.
        
        Args:
            input_path: Path to input JSON file
            output_path: Path to output JSON file
            keys_to_anonymize: Optional list of keys to anonymize
            
        Returns:
            Statistics about the anonymization process
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # Validate input file
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not input_path.suffix.lower() == '.json':
            raise ValidationError("Input file must be a JSON file")
        
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in file: {e}")
        except Exception as e:
            raise AnonymizerException(f"Error reading file: {e}")
        
        # Reset statistics
        self._stats = defaultdict(int)
        
        # Anonymize data
        anonymized = self.anonymize(data, keys_to_anonymize)
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write output file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(anonymized, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise AnonymizerException(f"Error writing file: {e}")
        
        # Return statistics
        return dict(self._stats)
    
    def anonymize_batch(self,
                       files: List[Union[str, Path]],
                       output_dir: Union[str, Path],
                       keys_to_anonymize: Optional[List[str]] = None,
                       preserve_structure: bool = True) -> Dict[str, Any]:
        """
        Batch anonymize multiple JSON files.
        
        Args:
            files: List of input file paths
            output_dir: Directory for output files
            keys_to_anonymize: Optional list of keys to anonymize
            preserve_structure: Whether to preserve directory structure
            
        Returns:
            Summary statistics for all files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_stats = {
            "files_processed": 0,
            "files_failed": 0,
            "total_entities": 0,
            "errors": []
        }
        
        for file_path in files:
            file_path = Path(file_path)
            
            try:
                # Determine output path
                if preserve_structure and file_path.parent != Path('.'):
                    output_path = output_dir / file_path.parent.name / file_path.name
                else:
                    output_path = output_dir / file_path.name
                
                # Anonymize file
                stats = self.anonymize_file(file_path, output_path, keys_to_anonymize)
                
                total_stats["files_processed"] += 1
                for key, value in stats.items():
                    if key.startswith("entity_"):
                        total_stats["total_entities"] += value
                        
            except Exception as e:
                total_stats["files_failed"] += 1
                total_stats["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                logger.error(f"Failed to process {file_path}: {e}")
        
        return total_stats
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get current processing statistics.
        
        Returns:
            Dictionary of statistics
        """
        return dict(self._stats)
