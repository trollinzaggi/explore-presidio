"""
Utility functions for the bias anonymizer.
"""

import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import re


class JsonPath:
    """Utility class for working with JSON paths."""
    
    @staticmethod
    def parse(path: str) -> List[Union[str, int]]:
        """
        Parse a JSON path string into components.
        
        Args:
            path: Path string (e.g., "employee.skills[0].name")
            
        Returns:
            List of path components
        """
        # Handle different separators
        path = path.replace("->", ".").replace("/", ".")
        
        components = []
        parts = path.split(".")
        
        for part in parts:
            # Check for array indices
            if "[" in part and "]" in part:
                # Extract key and indices
                match = re.match(r"([^[]+)(\[.*\])", part)
                if match:
                    key = match.group(1)
                    indices = re.findall(r"\[(\d+)\]", match.group(2))
                    
                    if key:
                        components.append(key)
                    for idx in indices:
                        components.append(int(idx))
            else:
                if part:
                    components.append(part)
        
        return components
    
    @staticmethod
    def match(path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern (supports wildcards).
        
        Args:
            path: JSON path
            pattern: Pattern to match (supports * and **)
            
        Returns:
            True if path matches pattern
        """
        # Convert pattern to regex
        pattern = pattern.replace("**", ".*")
        pattern = pattern.replace("*", "[^.]+")
        pattern = f"^{pattern}$"
        
        return bool(re.match(pattern, path))


def deep_get(data: Dict, path: Union[str, List]) -> Any:
    """
    Get value from nested dictionary using path.
    
    Args:
        data: Dictionary to search
        path: Path as string or list of components
        
    Returns:
        Value at path or None if not found
    """
    if isinstance(path, str):
        components = JsonPath.parse(path)
    else:
        components = path
    
    current = data
    for component in components:
        if isinstance(current, dict) and component in current:
            current = current[component]
        elif isinstance(current, list) and isinstance(component, int):
            if 0 <= component < len(current):
                current = current[component]
            else:
                return None
        else:
            return None
    
    return current


def deep_set(data: Dict, path: Union[str, List], value: Any):
    """
    Set value in nested dictionary using path.
    
    Args:
        data: Dictionary to modify
        path: Path as string or list of components
        value: Value to set
    """
    if isinstance(path, str):
        components = JsonPath.parse(path)
    else:
        components = path
    
    if not components:
        return
    
    current = data
    for i, component in enumerate(components[:-1]):
        if isinstance(current, dict):
            if component not in current:
                # Determine if next component is int (array index)
                next_component = components[i + 1]
                if isinstance(next_component, int):
                    current[component] = []
                else:
                    current[component] = {}
            current = current[component]
        elif isinstance(current, list) and isinstance(component, int):
            while len(current) <= component:
                current.append({})
            current = current[component]
    
    # Set the final value
    last_component = components[-1]
    if isinstance(current, dict):
        current[last_component] = value
    elif isinstance(current, list) and isinstance(last_component, int):
        while len(current) <= last_component:
            current.append(None)
        current[last_component] = value


def flatten_json(data: Dict, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten nested JSON into a single-level dictionary.
    
    Args:
        data: Nested dictionary
        parent_key: Parent key for recursion
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(flatten_json(value, new_key, sep).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    list_key = f"{new_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        items.extend(flatten_json(item, list_key, sep).items())
                    else:
                        items.append((list_key, item))
            else:
                items.append((new_key, value))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            list_key = f"{parent_key}[{i}]"
            if isinstance(item, (dict, list)):
                items.extend(flatten_json(item, list_key, sep).items())
            else:
                items.append((list_key, item))
    else:
        items.append((parent_key, data))
    
    return dict(items)


def unflatten_json(data: Dict[str, Any], sep: str = ".") -> Dict:
    """
    Unflatten a single-level dictionary back to nested JSON.
    
    Args:
        data: Flattened dictionary
        sep: Separator used in keys
        
    Returns:
        Nested dictionary
    """
    result = {}
    
    for flat_key, value in data.items():
        deep_set(result, flat_key, value)
    
    return result


def load_json_file(file_path: Union[str, Path]) -> Dict:
    """
    Load JSON from file with error handling.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict, file_path: Union[str, Path], indent: int = 2):
    """
    Save JSON to file with error handling.
    
    Args:
        data: JSON data to save
        file_path: Path to save file
        indent: JSON indentation level
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_all_paths(data: Dict) -> List[str]:
    """
    Get all paths in a JSON structure.
    
    Args:
        data: JSON data
        
    Returns:
        List of all paths
    """
    flattened = flatten_json(data)
    return list(flattened.keys())


def filter_paths(paths: List[str], patterns: List[str]) -> List[str]:
    """
    Filter paths based on patterns.
    
    Args:
        paths: List of paths
        patterns: List of patterns to match
        
    Returns:
        Filtered list of paths
    """
    filtered = []
    for path in paths:
        for pattern in patterns:
            if JsonPath.match(path, pattern):
                filtered.append(path)
                break
    return filtered
