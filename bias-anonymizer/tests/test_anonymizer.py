"""
Unit tests for the bias anonymizer.
"""

import pytest
import json
import sys
import os

# Add src to path
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
except NameError:
    # Fallback if __file__ is not defined
    sys.path.insert(0, os.path.join(os.getcwd(), '..', 'src'))

from bias_anonymizer import JSONAnonymizer, AnonymizerConfig
from bias_anonymizer.exceptions import ValidationError


class TestJSONAnonymizer:
    """Test cases for JSONAnonymizer class."""
    
    def test_simple_anonymization(self):
        """Test basic anonymization of PII."""
        data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567"
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(data)
        
        assert "John Doe" not in json.dumps(result)
        assert "john.doe@example.com" not in json.dumps(result)
        assert "555-123-4567" not in json.dumps(result)
    
    def test_bias_detection_and_removal(self):
        """Test detection and removal of bias terms."""
        data = {
            "description": "Young white male engineer from wealthy family"
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(data)
        
        result_text = result["description"].lower()
        assert "young" not in result_text
        assert "white" not in result_text
        assert "male" not in result_text
        assert "wealthy" not in result_text
        assert "engineer" in result_text  # Should keep job-relevant term
    
    def test_nested_structure_preservation(self):
        """Test that nested JSON structure is preserved."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "name": "Jane Smith",
                        "value": "test"
                    }
                }
            }
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(data)
        
        # Check structure is preserved
        assert "level1" in result
        assert "level2" in result["level1"]
        assert "level3" in result["level1"]["level2"]
        assert "value" in result["level1"]["level2"]["level3"]
        
        # Check PII is removed
        assert "Jane Smith" not in json.dumps(result)
    
    def test_selective_anonymization(self):
        """Test anonymization of specific keys only."""
        data = {
            "public_info": {
                "name": "Public Name",
                "title": "Software Engineer"
            },
            "private_info": {
                "ssn": "123-45-6789",
                "salary": "$100,000"
            }
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(
            data,
            keys_to_anonymize=["private_info.ssn", "private_info.salary"]
        )
        
        # Public info should remain
        assert result["public_info"]["name"] == "Public Name"
        assert result["public_info"]["title"] == "Software Engineer"
        
        # Private info should be anonymized
        assert "123-45-6789" not in json.dumps(result)
        assert "$100,000" not in result["private_info"]["salary"]
    
    def test_array_handling(self):
        """Test handling of arrays in JSON."""
        data = {
            "employees": [
                {"name": "Alice Johnson", "age": "young professional"},
                {"name": "Bob Smith", "age": "senior employee"},
                {"name": "Charlie Brown", "age": "middle-aged"}
            ]
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(data)
        
        assert len(result["employees"]) == 3
        for employee in result["employees"]:
            assert "Alice" not in json.dumps(employee)
            assert "Bob" not in json.dumps(employee)
            assert "Charlie" not in json.dumps(employee)
            assert "young" not in employee.get("age", "")
            assert "senior" not in employee.get("age", "")
            assert "middle-aged" not in employee.get("age", "")
    
    def test_custom_configuration(self):
        """Test custom configuration settings."""
        config = AnonymizerConfig(
            detect_bias=True,
            detect_pii=False,  # Only detect bias, not PII
            confidence_threshold=0.9
        )
        
        data = {
            "bio": "Young Hispanic woman",
            "email": "test@example.com"  # Should not be detected
        }
        
        anonymizer = JSONAnonymizer(config=config)
        result = anonymizer.anonymize(data)
        
        # Bias terms should be removed
        assert "Young" not in result["bio"]
        assert "Hispanic" not in result["bio"]
        
        # Email should remain (PII detection disabled)
        assert "test@example.com" in result["email"]
    
    def test_analysis_without_anonymization(self):
        """Test analysis feature without modifying data."""
        data = {
            "name": "John Doe",
            "description": "Experienced male engineer"
        }
        
        anonymizer = JSONAnonymizer()
        analysis = anonymizer.analyze(data)
        
        assert analysis["total_entities"] > 0
        assert "PERSON" in str(analysis["entities_by_type"])
        assert len(analysis["bias_categories"]) > 0
    
    def test_empty_input_handling(self):
        """Test handling of empty inputs."""
        anonymizer = JSONAnonymizer()
        
        # Empty dict
        result = anonymizer.anonymize({})
        assert result == {}
        
        # Dict with empty strings
        result = anonymizer.anonymize({"key": ""})
        assert result == {"key": ""}
        
        # Dict with None values
        result = anonymizer.anonymize({"key": None})
        assert result == {"key": None}
    
    def test_json_string_input(self):
        """Test handling of JSON string input."""
        json_string = '{"name": "John Doe", "age": "45-year-old"}'
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(json_string)
        
        assert isinstance(result, str)
        result_dict = json.loads(result)
        assert "John Doe" not in result
        assert "45-year-old" not in result
    
    def test_special_characters_handling(self):
        """Test handling of special characters in text."""
        data = {
            "text": "Name: María García-López, Age: 30-year-old, Email: maria@español.com"
        }
        
        anonymizer = JSONAnonymizer()
        result = anonymizer.anonymize(data)
        
        assert "María" not in result["text"]
        assert "García-López" not in result["text"]
        assert "30-year-old" not in result["text"]
    
    def test_comprehensive_bias_categories(self):
        """Test all bias categories are detected."""
        test_cases = {
            "gender": "He is a male employee",
            "race": "Asian candidate from China",
            "age": "Young millennial developer",
            "disability": "Wheelchair user needs accommodation",
            "marital": "Married with children",
            "nationality": "US citizen only",
            "orientation": "LGBTQ-friendly workplace",
            "religion": "Christian values important",
            "political": "Conservative Republican voter",
            "economic": "From wealthy family",
            "pregnancy": "Currently on maternity leave",
            "union": "Non-union position",
            "health": "No mental health issues",
            "criminal": "Clean criminal record required"
        }
        
        anonymizer = JSONAnonymizer()
        
        for category, text in test_cases.items():
            result = anonymizer.anonymize({"text": text})
            analysis = anonymizer.analyze({"text": text})
            
            # Check that bias was detected
            assert len(analysis["bias_categories"]) > 0, f"Failed to detect bias in: {text}"
            
            # Check that bias terms were removed/reduced
            assert len(result["text"]) < len(text), f"Failed to anonymize: {text}"


class TestConfiguration:
    """Test configuration handling."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            AnonymizerConfig(confidence_threshold=1.5)  # Invalid threshold
        
        with pytest.raises(ValueError):
            AnonymizerConfig(batch_size=-1)  # Invalid batch size
        
        with pytest.raises(ValueError):
            AnonymizerConfig(bias_categories=["invalid_category"])
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "detect_bias": True,
            "detect_pii": False,
            "confidence_threshold": 0.8
        }
        
        config = AnonymizerConfig.from_dict(config_dict)
        assert config.detect_bias == True
        assert config.detect_pii == False
        assert config.confidence_threshold == 0.8


class TestUtils:
    """Test utility functions."""
    
    def test_json_path_parsing(self):
        """Test JSON path parsing."""
        from bias_anonymizer.utils import JsonPath
        
        # Simple path
        assert JsonPath.parse("key1.key2") == ["key1", "key2"]
        
        # Path with array indices
        assert JsonPath.parse("items[0].name") == ["items", 0, "name"]
        
        # Complex path
        assert JsonPath.parse("data.users[1].addresses[0].city") == [
            "data", "users", 1, "addresses", 0, "city"
        ]
    
    def test_deep_get_and_set(self):
        """Test deep get and set operations."""
        from bias_anonymizer.utils import deep_get, deep_set
        
        data = {
            "level1": {
                "level2": {
                    "value": "test"
                },
                "array": [
                    {"item": 1},
                    {"item": 2}
                ]
            }
        }
        
        # Test get
        assert deep_get(data, "level1.level2.value") == "test"
        assert deep_get(data, "level1.array[0].item") == 1
        assert deep_get(data, "nonexistent") is None
        
        # Test set
        deep_set(data, "level1.level2.new_value", "new")
        assert data["level1"]["level2"]["new_value"] == "new"
        
        deep_set(data, "level1.array[1].item", 99)
        assert data["level1"]["array"][1]["item"] == 99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
