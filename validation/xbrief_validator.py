#!/usr/bin/env python3
"""
xBRIEF Document Validator

Validates complete xBRIEF documents against the current version for:
1. JSON Schema (structural validation)
2. DAG constraints (cycle detection, reference validation)
3. Conformance criteria from specification
""" 

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re

try:
    from libxbrief.compat.policy import (
        CURRENT_VERSION as _POLICY_CURRENT_VERSION,
        VALID_STATUSES as _POLICY_VALID_STATUSES,
    )
    _IMPORTED_CURRENT_VERSION = _POLICY_CURRENT_VERSION
    _IMPORTED_VALID_STATUSES = _POLICY_VALID_STATUSES
except ImportError:
    _IMPORTED_CURRENT_VERSION = None
    _IMPORTED_VALID_STATUSES = None

# Single source of truth for the version this validator enforces.
CURRENT_VERSION: str = _IMPORTED_CURRENT_VERSION or "0.8"

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not installed. Schema validation disabled.")
    print("Install with: pip install jsonschema")

# Import DAG validator
sys.path.insert(0, str(Path(__file__).parent))
from dag_validator import validate_plan_dag  # noqa: E402


class ConformanceValidator:
    """Validates xBRIEF conformance criteria for the current version."""

    # Import shared set from policy; fall back to inline definition if libxbrief not installed.
    VALID_STATUSES = _IMPORTED_VALID_STATUSES or {
        "draft", "proposed", "approved", "pending",
        "running", "completed", "blocked", "failed", "cancelled", "auto",
    }
    
    HIERARCHICAL_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$')
    
    URI_PATTERN = re.compile(r'^(#[a-zA-Z0-9_.-]+|file://.*|https://.*)$')
    
    def __init__(self, doc: Dict):
        self.doc = doc
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate conformance criteria.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self._check_version()
        self._check_plan_required_fields()
        self._check_status_values()
        self._check_hierarchical_ids()
        self._check_uri_syntax()
        self._check_narrative_keys()
        
        return (len(self.errors) == 0, self.errors, self.warnings)
    
    def _check_version(self):
        """Conformance #1: Contains xBRIEFInfo with the current version."""
        xbrief_info = self.doc.get("xBRIEFInfo")
        if not xbrief_info:
            self.errors.append("Missing required field: xBRIEFInfo")
            return

        version = xbrief_info.get("version")
        if version != CURRENT_VERSION:
            self.errors.append(f"Invalid version: expected '{CURRENT_VERSION}', got '{version}'")
    
    def _check_plan_required_fields(self):
        """Conformance #2-3: Contains exactly one plan with required fields"""
        if "plan" not in self.doc:
            self.errors.append("Missing required field: plan")
            return
        
        plan = self.doc["plan"]
        
        # Check for removed container types
        if "todoList" in self.doc:
            self.errors.append("TodoList container is not part of the Plan model. Use Plan instead.")
        if "playbook" in self.doc:
            self.errors.append("Playbook container is not part of the Plan model. Use Plan with narratives instead.")
        
        # Required fields
        if "title" not in plan:
            self.errors.append("Plan missing required field: title")
        if "status" not in plan:
            self.errors.append("Plan missing required field: status")
        if "items" not in plan:
            self.errors.append("Plan missing required field: items")
        elif not isinstance(plan["items"], list):
            self.errors.append("Plan.items must be an array")
    
    def _check_status_values(self):
        """Conformance #4: All status values use defined enum"""
        plan = self.doc.get("plan", {})
        
        # Check plan status
        plan_status = plan.get("status")
        if plan_status and plan_status not in self.VALID_STATUSES:
            self.errors.append(f"Invalid plan status: '{plan_status}'. Must be one of {self.VALID_STATUSES}")
        
        # Check item statuses
        self._check_item_statuses(plan.get("items", []), [])
    
    def _check_item_statuses(self, items: List[Dict], path: List[str]):
        """Recursively check item status values."""
        for i, item in enumerate(items):
            item_path = path + [f"items[{i}]"]
            status = item.get("status")

            if status and status not in self.VALID_STATUSES:
                path_str = ".".join(item_path)
                self.errors.append(f"Invalid status at {path_str}: '{status}'. Must be one of {self.VALID_STATUSES}")

            # Check nested items (preferred v0.8 field) and legacy subItems
            for nested_field in ("items", "subItems"):
                nested = item.get(nested_field, [])
                if nested:
                    self._check_item_statuses(nested, item_path + [nested_field])
    
    def _check_hierarchical_ids(self):
        """Conformance #6: Hierarchical IDs follow dot notation"""
        plan = self.doc.get("plan", {})
        
        # Check plan ID
        plan_id = plan.get("id")
        if plan_id and not self.HIERARCHICAL_ID_PATTERN.match(plan_id):
            self.errors.append(f"Invalid plan ID format: '{plan_id}'. Must match pattern: [a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)*")
        
        # Check item IDs
        self._check_item_ids(plan.get("items", []), [])
    
    def _check_item_ids(self, items: List[Dict], path: List[str]):
        """Recursively check item ID format."""
        for i, item in enumerate(items):
            item_path = path + [f"items[{i}]"]
            item_id = item.get("id")
            
            if item_id and not self.HIERARCHICAL_ID_PATTERN.match(item_id):
                path_str = ".".join(item_path)
                self.errors.append(f"Invalid ID format at {path_str}: '{item_id}'. Must match pattern: [a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)*")
            
            # Check nested items (v0.8 preferred "items" and legacy "subItems")
            for nested_field in ("items", "subItems"):
                nested = item.get(nested_field, [])
                if nested:
                    self._check_item_ids(nested, item_path + [nested_field])
    
    def _check_uri_syntax(self):
        """Conformance #9: planRef URIs follow syntax"""
        plan = self.doc.get("plan", {})
        self._check_item_uris(plan.get("items", []), [])
    
    def _check_item_uris(self, items: List[Dict], path: List[str]):
        """Recursively check planRef URI syntax."""
        for i, item in enumerate(items):
            item_path = path + [f"items[{i}]"]
            plan_ref = item.get("planRef")
            
            if plan_ref and not self.URI_PATTERN.match(plan_ref):
                path_str = ".".join(item_path)
                self.errors.append(f"Invalid planRef URI at {path_str}: '{plan_ref}'. Must match: #item-id, file://..., or https://...")
            
            # Check nested items (v0.8 preferred "items" and legacy "subItems")
            for nested_field in ("items", "subItems"):
                nested = item.get(nested_field, [])
                if nested:
                    self._check_item_uris(nested, item_path + [nested_field])
    
    def _check_narrative_keys(self):
        """Conformance #10: Narrative keys SHOULD use TitleCase"""
        plan = self.doc.get("plan", {})
        narratives = plan.get("narratives", {})
        
        for key in narratives.keys():
            # Check if key is TitleCase (starts with uppercase, no spaces)
            if not key[0].isupper():
                self.warnings.append(f"Narrative key '{key}' SHOULD use TitleCase (e.g., '{key.title()}')")
            
            if " " in key:
                self.warnings.append(f"Narrative key '{key}' SHOULD not contain spaces")


def validate_document(file_path: str, schema_path: str = None) -> int:
    """
    Validate a xBRIEF document.
    
    Args:
        file_path: Path to xBRIEF JSON document
        schema_path: Optional path to JSON Schema file
        
    Returns:
        Exit code (0 = valid, 1 = invalid)
    """
    # Load document
    try:
        with open(file_path, 'r') as f:
            doc = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return 1
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return 1
    
    print(f"Validating: {file_path}")
    print()
    
    all_valid = True
    
    # 1. JSON Schema validation
    if JSONSCHEMA_AVAILABLE and schema_path:
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            jsonschema.validate(doc, schema)
            print("✓ JSON Schema validation passed")
        except jsonschema.ValidationError as e:
            print("✗ JSON Schema validation failed:")
            print(f"  {e.message}")
            if e.path:
                path = ".".join(str(p) for p in e.path)
                print(f"  at: {path}")
            all_valid = False
        except FileNotFoundError:
            print(f"⚠ Schema file not found: {schema_path}")
    
    # 2. Conformance validation
    conformance = ConformanceValidator(doc)
    is_valid, errors, warnings = conformance.validate()
    
    if is_valid:
        print("✓ Conformance validation passed")
    else:
        print("✗ Conformance validation failed:")
        for error in errors:
            print(f"  - {error}")
        all_valid = False
    
    if warnings:
        print("⚠ Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # 3. DAG validation
    plan = doc.get("plan", {})
    edges = plan.get("edges", [])
    
    if edges:
        is_valid, dag_errors = validate_plan_dag(plan)
        if is_valid:
            print("✓ DAG validation passed")
        else:
            print("✗ DAG validation failed:")
            for error in dag_errors:
                print(f"  - {error}")
            all_valid = False
    else:
        print("○ No edges to validate (DAG validation skipped)")
    
    _ver = CURRENT_VERSION
    print()
    if all_valid:
        print(f"\u2713 Document is xBRIEF v{_ver} conformant")
        return 0
    else:
        print(f"\u2717 Document is NOT xBRIEF v{_ver} conformant")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: xbrief_validator.py <file.xbrief.json> [schema.json]")
        print()
        print("Examples:")
        print("  xbrief_validator.py plan.xbrief.json")
        print("  xbrief_validator.py plan.xbrief.json xbrief-core.schema.json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Auto-detect schema if not provided
    if not schema_path:
        # Look for schema in standard location
        script_dir = Path(__file__).parent
        potential_schema = script_dir.parent / "schemas" / "xbrief-core.schema.json"
        if potential_schema.exists():
            schema_path = str(potential_schema)
    
    exit_code = validate_document(file_path, schema_path)
    sys.exit(exit_code)
