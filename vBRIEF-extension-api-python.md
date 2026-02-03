# vBRIEF Extension Proposal: Python API Library

> **EARLY DRAFT**: This is an initial proposal and subject to change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Python API Library  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This document describes a Python library implementation for working with vBRIEF documents. The library provides Pythonic interfaces for creating, parsing, manipulating, and validating vBRIEF TodoLists and Plans in both JSON and TRON formats.

The library enables:
- **Type-safe operations** with Python type hints and dataclasses
- **Format conversion** between JSON and TRON
- **Schema validation** with Pydantic models
- **Builder patterns** for fluent document construction
- **Query interfaces** with Python idioms (list comprehensions, filters)
- **Framework integration** (FastAPI, Django, Flask, Jupyter)
- **Async support** for modern Python applications

## Motivation

**Why a Python library?**
- Python dominates AI/ML, data science, and agentic system development
- Popular in DevOps, scripting, and automation tooling
- Rich ecosystem for web APIs and CLI applications
- First-class support in Jupyter notebooks for interactive development
- Strong typing with dataclasses and Pydantic
- Excellent for rapid prototyping and production systems

**Use cases**:
- Agentic systems (LangChain, AutoGPT, CrewAI, etc.)
- AI/ML workflows (task tracking for model training, experiments)
- Web APIs (FastAPI, Django REST framework, Flask)
- CLI tools for vBRIEF management
- Jupyter notebooks for interactive planning
- Data pipelines and workflow orchestration (Airflow, Prefect)
- VS Code extensions and IDE integrations

## Architecture

### Package Structure

```
vbrief-python/
├── src/
│   └── vbrief/
│       ├── __init__.py
│       ├── core/              # Core types and models
│       │   ├── __init__.py
│       │   ├── document.py
│       │   ├── todo.py
│       │   ├── plan.py
│       │   └── types.py
│       ├── extensions/        # Extension implementations
│       │   ├── __init__.py
│       │   ├── timestamps.py
│       │   ├── identifiers.py
│       │   ├── metadata.py
│       │   ├── hierarchical.py
│       │   ├── workflow.py
│       │   ├── participants.py
│       │   ├── resources.py
│       │   ├── recurring.py
│       │   ├── security.py
│       │   ├── version.py
│       │   ├── forking.py
│       │   └── ace.py
│       ├── parser/            # Parsing and serialization
│       │   ├── __init__.py
│       │   ├── json_parser.py
│       │   ├── tron_parser.py
│       │   └── auto.py
│       ├── builder/           # Fluent builders
│       │   ├── __init__.py
│       │   ├── todo_builder.py
│       │   └── plan_builder.py
│       ├── validator/         # Schema validation
│       │   ├── __init__.py
│       │   └── schemas.py
│       ├── query/             # Query and filtering
│       │   ├── __init__.py
│       │   ├── todo_query.py
│       │   └── plan_query.py
│       ├── mutator/           # Direct mutation helpers
│       │   ├── __init__.py
│       │   ├── todo_mutator.py
│       │   └── plan_mutator.py
│       ├── updater/           # Immutable and validated updates
│       │   ├── __init__.py
│       │   ├── immutable.py
│       │   ├── validated.py
│       │   └── transaction.py
│       └── integrations/      # Framework integrations
│           ├── fastapi/
│           ├── django/
│           ├── langchain/
│           └── jupyter/
├── tests/
├── examples/
├── docs/
├── pyproject.toml
└── README.md
```

## Core API Design

### Core Types (Pydantic Models)

```python
# vbrief/core/types.py

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ItemStatus(str, Enum):
    """Todo item status values."""
    PENDING = "pending"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class PlanStatus(str, Enum):
    """Plan status values."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlanItemStatus(str, Enum):
    """PlanItem status values."""
    PENDING = "pending"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Info(BaseModel):
    """Document-level metadata."""
    version: str = Field(description="Schema version")
    author: Optional[str] = Field(None, description="Document creator")
    description: Optional[str] = Field(None, description="Document description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom fields")

    class Config:
        extra = "allow"  # Allow extension fields


class TodoItem(BaseModel):
    """Single actionable task."""
    title: str = Field(description="Brief summary")
    status: ItemStatus = Field(description="Current status")

    class Config:
        extra = "allow"


class TodoList(BaseModel):
    """Collection of work items."""
    items: List[TodoItem] = Field(default_factory=list, description="Todo items")

    class Config:
        extra = "allow"


class PlanItem(BaseModel):
    """Stage of work within a plan."""
    title: str = Field(description="PlanItem name")
    status: PlanItemStatus = Field(description="Current status")

    class Config:
        extra = "allow"


class Plan(BaseModel):
    """Structured design document."""
    title: str = Field(description="Plan title")
    status: PlanStatus = Field(description="Current status")
    narratives: Dict[str, str] = Field(
        default_factory=dict,
        description="Narratives (key -> markdown string)"
    )
    items: List[PlanItem] = Field(
        default_factory=list,
        description="Plan items"
    )

    class Config:
        extra = "allow"


class Document(BaseModel):
    """Root vBRIEF document."""
    vBRIEFInfo: Info = Field(alias="vBRIEFInfo")
    todoList: Optional[TodoList] = Field(None, alias="todoList")
    plan: Optional[Plan] = None

    class Config:
        populate_by_name = True
```

### Document Class API

```python
# vbrief/core/document.py

from typing import Optional, Union
from pathlib import Path
from .types import Document, Info, TodoList, Plan


class VAgendaDocument:
    """Main interface for working with vBRIEF documents."""
    
    def __init__(self, data: Document):
        self._data = data

    @classmethod
    def create_todo_list(cls, version: str = "0.4") -> "VAgendaDocument":
        """Create a new TodoList document."""
        doc = Document(
            vBRIEFInfo=Info(version=version),
            todoList=TodoList()
        )
        return cls(doc)

    @classmethod
    def create_plan(cls, title: str, version: str = "0.4") -> "VAgendaDocument":
        """Create a new Plan document."""
        doc = Document(
            vBRIEFInfo=Info(version=version),
            plan=Plan(
                title=title,
                status=PlanStatus.DRAFT,
                narratives={}
            )
        )
        return cls(doc)

    @classmethod
    def from_json(cls, json_str: str) -> "VAgendaDocument":
        """Parse from JSON string."""
        doc = Document.model_validate_json(json_str)
        return cls(doc)

    @classmethod
    def from_tron(cls, tron_str: str) -> "VAgendaDocument":
        """Parse from TRON string."""
        from ..parser.tron_parser import TRONParser
        parser = TRONParser()
        doc = parser.parse(tron_str)
        return cls(doc)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "VAgendaDocument":
        """Load from file (auto-detect format)."""
        path = Path(path)
        content = path.read_text()
        
        # Auto-detect format
        if path.suffix == ".json":
            return cls.from_json(content)
        elif path.suffix == ".tron":
            return cls.from_tron(content)
        else:
            # Try both formats
            try:
                return cls.from_json(content)
            except Exception:
                return cls.from_tron(content)

    @classmethod
    def parse(cls, content: str) -> "VAgendaDocument":
        """Auto-detect format and parse."""
        try:
            return cls.from_json(content)
        except Exception:
            return cls.from_tron(content)

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert to JSON string."""
        return self._data.model_dump_json(
            indent=indent,
            by_alias=True,
            exclude_none=True
        )

    def to_tron(self) -> str:
        """Convert to TRON string."""
        from ..parser.tron_parser import TRONSerializer
        serializer = TRONSerializer()
        return serializer.serialize(self._data)

    def to_file(self, path: Union[str, Path], format: Optional[str] = None):
        """Save to file."""
        path = Path(path)
        
        if format is None:
            # Infer from extension
            format = path.suffix.lstrip(".")
        
        if format == "json":
            content = self.to_json()
        elif format == "tron":
            content = self.to_tron()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        path.write_text(content)

    @property
    def data(self) -> Document:
        """Access underlying document."""
        return self._data

    @property
    def todo_list(self) -> Optional[TodoList]:
        """Get TodoList if present."""
        return self._data.todoList

    @property
    def plan(self) -> Optional[Plan]:
        """Get Plan if present."""
        return self._data.plan

    def validate(self) -> List[str]:
        """Validate document and return errors."""
        from ..validator.schemas import validate_document
        return validate_document(self._data)
```

### Builder API

```python
# vbrief/builder/todo_builder.py

from typing import List, Optional
from ..core.types import Document, Info, TodoList, TodoItem, ItemStatus


class TodoListBuilder:
    """Fluent builder for TodoList documents."""
    
    def __init__(self, version: str = "0.4"):
        self._info = Info(version=version)
        self._items: List[TodoItem] = []

    def author(self, name: str) -> "TodoListBuilder":
        """Set document author."""
        self._info.author = name
        return self

    def description(self, desc: str) -> "TodoListBuilder":
        """Set document description."""
        self._info.description = desc
        return self

    def add_item(
        self,
        title: str,
        status: ItemStatus = ItemStatus.PENDING
    ) -> "TodoListBuilder":
        """Add a todo item."""
        self._items.append(TodoItem(title=title, status=status))
        return self

    def add_items(self, items: List[TodoItem]) -> "TodoListBuilder":
        """Add multiple items."""
        self._items.extend(items)
        return self

    def build(self) -> Document:
        """Build the document."""
        return Document(
            vBRIEFInfo=self._info,
            todoList=TodoList(items=self._items)
        )

    def build_document(self) -> "VAgendaDocument":
        """Build and wrap in VAgendaDocument."""
        from ..core.document import VAgendaDocument
        return VAgendaDocument(self.build())


# vbrief/builder/plan_builder.py

from typing import Dict, Optional
from ..core.types import Document, Info, Plan, PlanStatus


class PlanBuilder:
    """Fluent builder for Plan documents."""
    
    def __init__(self, title: str, version: str = "0.4"):
        self._info = Info(version=version)
        self._plan = Plan(
            title=title,
            status=PlanStatus.DRAFT,
            narratives={}
        )

    def author(self, name: str) -> "PlanBuilder":
        """Set document author."""
        self._info.author = name
        return self

    def status(self, status: PlanStatus) -> "PlanBuilder":
        """Set plan status."""
        self._plan.status = status
        return self

    def narrative(self, key: str, content: str) -> "PlanBuilder":
        """Add a narrative (key -> markdown string)."""
        self._plan.narratives[key] = content
        return self

    def proposal(self, content: str) -> "PlanBuilder":
        """Add proposal narrative (required)."""
        return self.narrative("proposal", content)

    def problem(self, content: str) -> "PlanBuilder":
        """Add problem narrative."""
        return self.narrative("problem", content)

    def background(self, content: str) -> "PlanBuilder":
        """Add background narrative."""
        return self.narrative("background", content)

    def build(self) -> Document:
        """Build the document."""
        return Document(
            vBRIEFInfo=self._info,
            plan=self._plan
        )

    def build_document(self) -> "VAgendaDocument":
        """Build and wrap in VAgendaDocument."""
        from ..core.document import VAgendaDocument
        return VAgendaDocument(self.build())


# Convenience functions
def todo(version: str = "0.4") -> TodoListBuilder:
    """Create a TodoList builder."""
    return TodoListBuilder(version)


def plan(title: str, version: str = "0.4") -> PlanBuilder:
    """Create a Plan builder."""
    return PlanBuilder(title, version)
```

### Query API

```python
# vbrief/query/todo_query.py

from typing import Callable, List, Optional
from ..core.types import TodoItem, ItemStatus


class TodoQuery:
    """Query interface for filtering TodoItems."""
    
    def __init__(self, items: List[TodoItem]):
        self._items = items

    def by_status(self, status: ItemStatus) -> "TodoQuery":
        """Filter by status."""
        filtered = [item for item in self._items if item.status == status]
        return TodoQuery(filtered)

    def by_title(self, pattern: str, case_sensitive: bool = False) -> "TodoQuery":
        """Filter by title pattern."""
        if case_sensitive:
            filtered = [item for item in self._items if pattern in item.title]
        else:
            pattern_lower = pattern.lower()
            filtered = [
                item for item in self._items
                if pattern_lower in item.title.lower()
            ]
        return TodoQuery(filtered)

    def where(self, predicate: Callable[[TodoItem], bool]) -> "TodoQuery":
        """Filter with custom predicate."""
        filtered = [item for item in self._items if predicate(item)]
        return TodoQuery(filtered)

    def map(self, func: Callable[[TodoItem], Any]) -> List[Any]:
        """Map items to new values."""
        return [func(item) for item in self._items]

    def all(self) -> List[TodoItem]:
        """Get all matching items."""
        return self._items

    def first(self) -> Optional[TodoItem]:
        """Get first matching item."""
        return self._items[0] if self._items else None

    def count(self) -> int:
        """Get count of matching items."""
        return len(self._items)

    def exists(self) -> bool:
        """Check if any items match."""
        return len(self._items) > 0

    # Pythonic iteration support
    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]


def query(items: List[TodoItem]) -> TodoQuery:
    """Create a query for todo items."""
    return TodoQuery(items)
```

### Validator API

```python
# vbrief/validator/schemas.py

from typing import List
from pydantic import ValidationError
from ..core.types import Document


def validate_document(doc: Document) -> List[str]:
    """
    Validate a document and return list of error messages.
    
    Returns:
        Empty list if valid, list of error messages otherwise.
    """
    try:
        # Pydantic validation happens automatically
        doc.model_validate(doc.model_dump())
        return []
    except ValidationError as e:
        return [f"{err['loc']}: {err['msg']}" for err in e.errors()]


def validate_or_raise(doc: Document):
    """Validate and raise exception on error."""
    errors = validate_document(doc)
    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")
```

### Mutation API

The library supports document modification through Pythonic patterns: direct mutation (for simple cases), context managers (for transactional updates), and validated mutators (for safety-critical operations).

#### Direct Mutation Helpers

```python
# vbrief/mutator/todo_mutator.py

from typing import Callable, List, Optional
from ..core.types import TodoList, TodoItem, ItemStatus


class TodoListMutator:
    """Helper for mutating TodoList."""
    
    def __init__(self, todo_list: TodoList):
        self._list = todo_list
    
    def add_item(self, title: str, status: ItemStatus = ItemStatus.PENDING) -> TodoItem:
        """Add an item to the list."""
        item = TodoItem(title=title, status=status)
        self._list.items.append(item)
        return item
    
    def remove_item(self, index: int) -> TodoItem:
        """Remove an item by index."""
        if index < 0 or index >= len(self._list.items):
            raise IndexError(f"Index out of range: {index}")
        return self._list.items.pop(index)
    
    def update_item(self, index: int, **updates) -> TodoItem:
        """Update an item by index."""
        if index < 0 or index >= len(self._list.items):
            raise IndexError(f"Index out of range: {index}")
        
        item = self._list.items[index]
        for key, value in updates.items():
            setattr(item, key, value)
        return item
    
    def find_and_update(
        self,
        predicate: Callable[[TodoItem], bool],
        **updates
    ) -> int:
        """Find and update items matching predicate."""
        count = 0
        for item in self._list.items:
            if predicate(item):
                for key, value in updates.items():
                    setattr(item, key, value)
                count += 1
        return count
    
    def clear(self) -> None:
        """Clear all items."""
        self._list.items.clear()


# vbrief/mutator/plan_mutator.py

from typing import Optional
from ..core.types import Plan, PlanStatus


class PlanMutator:
    """Helper for mutating Plan."""
    
    def __init__(self, plan: Plan):
        self._plan = plan
    
    def set_narrative(self, key: str, content: str) -> str:
        """Add or update a narrative."""
        self._plan.narratives[key] = content
        return content
    
    def remove_narrative(self, key: str) -> Optional[str]:
        """Remove a narrative."""
        return self._plan.narratives.pop(key, None)
    
    def update_narrative(self, key: str, content: str) -> str:
        """Update narrative content."""
        if key not in self._plan.narratives:
            raise KeyError(f"Narrative not found: {key}")
        self._plan.narratives[key] = content
        return content
    
    def set_status(self, status: PlanStatus) -> None:
        """Set plan status."""
        self._plan.status = status


def mutate_todo_list(todo_list: TodoList) -> TodoListMutator:
    """Create a mutator for a TodoList."""
    return TodoListMutator(todo_list)


def mutate_plan(plan: Plan) -> PlanMutator:
    """Create a mutator for a Plan."""
    return PlanMutator(plan)
```

#### Immutable Update Helpers

```python
# vbrief/updater/immutable.py

from typing import Callable, Dict
from copy import deepcopy
from ..core.types import Document, TodoItem, ItemStatus, PlanStatus


class ImmutableUpdater:
    """Immutable update helpers using deep copy."""
    
    @staticmethod
    def add_item(
        doc: Document,
        title: str,
        status: ItemStatus = ItemStatus.PENDING
    ) -> Document:
        """Add item to TodoList (immutable)."""
        if not doc.todoList:
            raise ValueError("Document has no TodoList")
        
        new_doc = deepcopy(doc)
        new_doc.todoList.items.append(TodoItem(title=title, status=status))
        return new_doc
    
    @staticmethod
    def remove_item(doc: Document, index: int) -> Document:
        """Remove item from TodoList (immutable)."""
        if not doc.todoList:
            raise ValueError("Document has no TodoList")
        
        new_doc = deepcopy(doc)
        if index < 0 or index >= len(new_doc.todoList.items):
            raise IndexError(f"Index out of range: {index}")
        new_doc.todoList.items.pop(index)
        return new_doc
    
    @staticmethod
    def update_item(doc: Document, index: int, **updates) -> Document:
        """Update item in TodoList (immutable)."""
        if not doc.todoList:
            raise ValueError("Document has no TodoList")
        
        new_doc = deepcopy(doc)
        if index < 0 or index >= len(new_doc.todoList.items):
            raise IndexError(f"Index out of range: {index}")
        
        item = new_doc.todoList.items[index]
        for key, value in updates.items():
            setattr(item, key, value)
        return new_doc
    
    @staticmethod
    def find_and_update(
        doc: Document,
        predicate: Callable[[TodoItem], bool],
        **updates
    ) -> Document:
        """Find and update items (immutable)."""
        if not doc.todoList:
            raise ValueError("Document has no TodoList")
        
        new_doc = deepcopy(doc)
        for item in new_doc.todoList.items:
            if predicate(item):
                for key, value in updates.items():
                    setattr(item, key, value)
        return new_doc
    
    @staticmethod
    def set_narrative(
        doc: Document,
        key: str,
        content: str
    ) -> Document:
        """Set narrative in Plan (immutable)."""
        if not doc.plan:
            raise ValueError("Document has no Plan")
        
        new_doc = deepcopy(doc)
        new_doc.plan.narratives[key] = content
        return new_doc
    
    @staticmethod
    def set_plan_status(doc: Document, status: PlanStatus) -> Document:
        """Update plan status (immutable)."""
        if not doc.plan:
            raise ValueError("Document has no Plan")
        
        new_doc = deepcopy(doc)
        new_doc.plan.status = status
        return new_doc
```

#### Validated Updater

```python
# vbrief/updater/validated.py

from typing import Callable, List, Optional, Any
from dataclasses import dataclass
from copy import deepcopy
from ..core.types import Document, TodoItem, ItemStatus, PlanStatus
from ..validator.schemas import validate_document


@dataclass
class UpdateResult:
    """Result of an update operation."""
    success: bool
    document: Optional[Document] = None
    errors: Optional[List[str]] = None


class ValidatedUpdater:
    """Validated updater with automatic validation and rollback."""
    
    def __init__(self, doc: Document, validate: bool = True):
        self._doc = doc
        self._validate = validate
    
    def get_document(self) -> Document:
        """Get the current document."""
        return self._doc
    
    def validate(self) -> List[str]:
        """Validate current state."""
        if not self._validate:
            return []
        return validate_document(self._doc)
    
    def add_item(
        self,
        title: str,
        status: ItemStatus = ItemStatus.PENDING
    ) -> UpdateResult:
        """Add item with validation."""
        if not self._doc.todoList:
            return UpdateResult(
                success=False,
                errors=["Document has no TodoList"]
            )
        
        item = TodoItem(title=title, status=status)
        self._doc.todoList.items.append(item)
        
        errors = self.validate()
        if errors:
            # Rollback
            self._doc.todoList.items.pop()
            return UpdateResult(success=False, errors=errors)
        
        return UpdateResult(success=True, document=self._doc)
    
    def update_item(self, index: int, **updates) -> UpdateResult:
        """Update item with validation."""
        if not self._doc.todoList:
            return UpdateResult(
                success=False,
                errors=["Document has no TodoList"]
            )
        
        if index < 0 or index >= len(self._doc.todoList.items):
            return UpdateResult(
                success=False,
                errors=[f"Index out of range: {index}"]
            )
        
        # Save original for rollback
        item = self._doc.todoList.items[index]
        original = {key: getattr(item, key) for key in updates}
        
        # Apply updates
        for key, value in updates.items():
            setattr(item, key, value)
        
        errors = self.validate()
        if errors:
            # Rollback
            for key, value in original.items():
                setattr(item, key, value)
            return UpdateResult(success=False, errors=errors)
        
        return UpdateResult(success=True, document=self._doc)
    
    def find_and_update(
        self,
        predicate: Callable[[TodoItem], bool],
        **updates
    ) -> UpdateResult:
        """Find and update with validation."""
        if not self._doc.todoList:
            return UpdateResult(
                success=False,
                errors=["Document has no TodoList"]
            )
        
        # Find matching items and save originals
        matches = []
        originals = {}
        for i, item in enumerate(self._doc.todoList.items):
            if predicate(item):
                matches.append(i)
                originals[i] = {key: getattr(item, key) for key in updates}
        
        if not matches:
            return UpdateResult(
                success=False,
                errors=["No matching items found"]
            )
        
        # Apply updates
        for i in matches:
            item = self._doc.todoList.items[i]
            for key, value in updates.items():
                setattr(item, key, value)
        
        errors = self.validate()
        if errors:
            # Rollback all changes
            for i in matches:
                item = self._doc.todoList.items[i]
                for key, value in originals[i].items():
                    setattr(item, key, value)
            return UpdateResult(success=False, errors=errors)
        
        return UpdateResult(success=True, document=self._doc)
    
    def remove_item(self, index: int) -> UpdateResult:
        """Remove item with validation."""
        if not self._doc.todoList:
            return UpdateResult(
                success=False,
                errors=["Document has no TodoList"]
            )
        
        if index < 0 or index >= len(self._doc.todoList.items):
            return UpdateResult(
                success=False,
                errors=[f"Index out of range: {index}"]
            )
        
        removed = self._doc.todoList.items.pop(index)
        
        errors = self.validate()
        if errors:
            # Rollback
            self._doc.todoList.items.insert(index, removed)
            return UpdateResult(success=False, errors=errors)
        
        return UpdateResult(success=True, document=self._doc)
    
    def set_narrative(
        self,
        key: str,
        content: str
    ) -> UpdateResult:
        """Set plan narrative with validation."""
        if not self._doc.plan:
            return UpdateResult(
                success=False,
                errors=["Document has no Plan"]
            )
        
        original = self._doc.plan.narratives.get(key)
        self._doc.plan.narratives[key] = content
        
        errors = self.validate()
        if errors:
            # Rollback
            if original:
                self._doc.plan.narratives[key] = original
            else:
                del self._doc.plan.narratives[key]
            return UpdateResult(success=False, errors=errors)
        
        return UpdateResult(success=True, document=self._doc)
    
    def transaction(self, func: Callable[["ValidatedUpdater"], UpdateResult]) -> UpdateResult:
        """Execute multiple operations in a transaction."""
        # Create snapshot for rollback
        snapshot = deepcopy(self._doc)
        
        result = func(self)
        
        if not result.success:
            # Rollback to snapshot
            self._doc = snapshot
        
        return result


def create_updater(doc: Document, validate: bool = True) -> ValidatedUpdater:
    """Create a validated updater."""
    return ValidatedUpdater(doc, validate)
```

#### Context Manager for Transactions

```python
# vbrief/updater/transaction.py

from typing import Optional
from contextlib import contextmanager
from copy import deepcopy
from ..core.types import Document
from ..validator.schemas import validate_document


@contextmanager
def transaction(doc: Document, validate: bool = True):
    """
    Context manager for transactional document updates.
    
    Usage:
        with transaction(doc) as txn:
            txn.todoList.items.append(TodoItem(title="New", status=ItemStatus.PENDING))
            txn.todoList.items[0].status = ItemStatus.COMPLETED
    
    If validation fails or an exception is raised, changes are rolled back.
    """
    snapshot = deepcopy(doc)
    
    try:
        yield doc
        
        # Validate after all changes
        if validate:
            errors = validate_document(doc)
            if errors:
                # Rollback
                doc.__dict__.update(snapshot.__dict__)
                raise ValueError(f"Validation failed: {'; '.join(errors)}")
    
    except Exception:
        # Rollback on any exception
        doc.__dict__.update(snapshot.__dict__)
        raise
```

## Extension Support

Extensions use Pydantic's model inheritance:

```python
# vbrief/extensions/identifiers.py

from pydantic import Field
from ..core.types import TodoItem as CoreTodoItem, TodoList as CoreTodoList
from ..core.types import Plan as CorePlan, PlanItem as CorePlanItem


class TodoItemWithId(CoreTodoItem):
    """TodoItem with identifier extension."""
    id: str = Field(description="Unique identifier")


class TodoListWithId(CoreTodoList):
    """TodoList with identifier extension."""
    id: str = Field(description="Unique identifier")


class PlanWithId(CorePlan):
    """Plan with identifier extension."""
    id: str = Field(description="Unique identifier")


class PlanItemWithId(CorePlanItem):
    """PlanItem with identifier extension."""
    id: str = Field(description="Unique identifier")


# vbrief/extensions/timestamps.py

from datetime import datetime
from typing import Optional
from pydantic import Field
from ..core.types import Info as CoreInfo, TodoItem as CoreTodoItem


class InfoWithTimestamps(CoreInfo):
    """Info with timestamp extension."""
    created: datetime = Field(description="Creation time")
    updated: datetime = Field(description="Last update time")
    timezone: Optional[str] = Field(None, description="IANA timezone")


class TodoItemWithTimestamps(CoreTodoItem):
    """TodoItem with timestamp extension."""
    created: datetime = Field(description="Creation time")
    updated: datetime = Field(description="Last update time")


# vbrief/extensions/metadata.py

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import Field
from ..core.types import TodoItem as CoreTodoItem, TodoList as CoreTodoList


class Priority(str, Enum):
    """Item priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TodoItemWithMetadata(CoreTodoItem):
    """TodoItem with metadata extension."""
    description: Optional[str] = Field(None, description="Detailed context")
    priority: Optional[Priority] = Field(None, description="Priority level")
    tags: Optional[List[str]] = Field(None, description="Categorical labels")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom fields")


class TodoListWithMetadata(CoreTodoList):
    """TodoList with metadata extension."""
    title: Optional[str] = Field(None, description="List title")
    description: Optional[str] = Field(None, description="List description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
```

## Usage Examples

### Example 1: Creating a TodoList

```python
from vbrief import todo, VAgendaDocument, ItemStatus

# Using builder
doc = (todo("0.4")
    .author("agent-alpha")
    .add_item("Implement authentication", ItemStatus.PENDING)
    .add_item("Write API documentation", ItemStatus.PENDING)
    .build_document())

# Convert to JSON
print(doc.to_json())

# Convert to TRON
print(doc.to_tron())

# Save to file
doc.to_file("tasks.tron")
```

### Example 2: Parsing and Querying

```python
from vbrief import VAgendaDocument, query, ItemStatus

# Load and parse
doc = VAgendaDocument.from_file("tasks.tron")

# Query pending items
pending = query(doc.todo_list.items).by_status(ItemStatus.PENDING).all()

print(f"Pending items: {len(pending)}")
for item in pending:
    print(f"  - {item.title}")

# Use Pythonic iteration
for item in query(doc.todo_list.items).by_status(ItemStatus.PENDING):
    print(item.title)
```

### Example 3: Creating a Plan

```python
from vbrief import plan, PlanStatus

doc = (plan("Add user authentication", "0.4")
    .status(PlanStatus.DRAFT)
    .proposal(
        "Proposed Changes",
        "Implement JWT-based authentication with refresh tokens"
    )
    .problem(
        "Problem Statement",
        "Current system lacks secure authentication"
    )
    .build_document())

print(doc.to_tron())
```

### Example 4: Using Extensions

```python
from datetime import datetime
from vbrief.extensions.identifiers import TodoItemWithId
from vbrief.extensions.timestamps import TodoItemWithTimestamps
from vbrief.extensions.metadata import TodoItemWithMetadata, Priority

# Create item with multiple extensions (using composition)
item_data = {
    "id": "item-001",
    "title": "Complete API documentation",
    "status": "inProgress",
    "created": datetime.now(),
    "updated": datetime.now(),
    "description": "Document all REST endpoints",
    "priority": Priority.HIGH,
    "tags": ["docs", "api"]
}

# Use the most complete model
class ExtendedTodoItem(TodoItemWithId, TodoItemWithTimestamps, TodoItemWithMetadata):
    pass

item = ExtendedTodoItem(**item_data)
print(item.model_dump_json(indent=2))
```

### Example 5: FastAPI Integration

```python
# app.py

from fastapi import FastAPI, HTTPException
from vbrief import VAgendaDocument, todo, ItemStatus
from vbrief.core.types import TodoItem

app = FastAPI()

# In-memory storage (use database in production)
documents = {}

@app.post("/todos", status_code=201)
async def create_todo_list(author: str = None):
    """Create a new todo list."""
    doc = todo().author(author).build_document()
    doc_id = str(len(documents))
    documents[doc_id] = doc
    return {"id": doc_id, "document": doc.data}

@app.get("/todos/{doc_id}")
async def get_todo_list(doc_id: str):
    """Get a todo list."""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Not found")
    return documents[doc_id].data

@app.post("/todos/{doc_id}/items")
async def add_item(doc_id: str, title: str, status: ItemStatus = ItemStatus.PENDING):
    """Add item to todo list."""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Not found")
    
    doc = documents[doc_id]
    doc.todo_list.items.append(TodoItem(title=title, status=status))
    return doc.data

@app.get("/todos/{doc_id}/items")
async def get_items(doc_id: str, status: ItemStatus = None):
    """Get items, optionally filtered by status."""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Not found")
    
    doc = documents[doc_id]
    items = doc.todo_list.items
    
    if status:
        items = [item for item in items if item.status == status]
    
    return {"items": items}
```

### Example 6: LangChain Integration

```python
from langchain.tools import tool
from vbrief import VAgendaDocument, todo, ItemStatus

# Global document (use database in production)
current_doc = todo().build_document()

@tool
def add_todo(title: str, status: str = "pending") -> str:
    """Add a todo item to the current list."""
    status_enum = ItemStatus(status)
    current_doc.todo_list.items.append(
        TodoItem(title=title, status=status_enum)
    )
    return f"Added: {title}"

@tool
def list_todos(status: str = None) -> str:
    """List all todo items, optionally filtered by status."""
    items = current_doc.todo_list.items
    
    if status:
        status_enum = ItemStatus(status)
        items = [item for item in items if item.status == status_enum]
    
    result = []
    for item in items:
        result.append(f"- {item.title} ({item.status.value})")
    
    return "\n".join(result) if result else "No items"

@tool
def complete_todo(title: str) -> str:
    """Mark a todo item as completed."""
    for item in current_doc.todo_list.items:
        if item.title == title:
            item.status = ItemStatus.COMPLETED
            return f"Completed: {title}"
    return f"Not found: {title}"

# Use with LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0)
tools = [add_todo, list_todos, complete_todo]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Agent can now manage todos
agent.run("Add a task to implement authentication")
agent.run("What are my pending tasks?")
agent.run("Mark the authentication task as complete")
```

### Example 7: Jupyter Notebook Usage

```python
# In Jupyter notebook

from vbrief import VAgendaDocument, query, ItemStatus
import matplotlib.pyplot as plt

# Load document
doc = VAgendaDocument.from_file("project.tron")

# Quick stats
items = doc.todo_list.items
status_counts = {}
for item in items:
    status_counts[item.status.value] = status_counts.get(item.status.value, 0) + 1

# Visualize
plt.bar(status_counts.keys(), status_counts.values())
plt.title("Todo Status Distribution")
plt.xlabel("Status")
plt.ylabel("Count")
plt.show()

# Interactive filtering
pending = query(items).by_status(ItemStatus.PENDING).all()
for i, item in enumerate(pending, 1):
    print(f"{i}. {item.title}")
```

### Example 8: Django Integration

```python
# models.py

from django.db import models
from vbrief import VAgendaDocument

class VAgendaProject(models.Model):
    name = models.CharField(max_length=200)
    document_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def document(self):
        """Get VAgendaDocument instance."""
        return VAgendaDocument.from_json(self.document_json)
    
    @document.setter
    def document(self, doc: VAgendaDocument):
        """Set VAgendaDocument instance."""
        self.document_json = doc.to_json()


# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import VAgendaProject
from vbrief import todo

class CreateTodoListView(APIView):
    def post(self, request):
        doc = todo().author(request.user.username).build_document()
        project = VAgendaProject(
            name=request.data.get("name", "Untitled"),
            document_json=doc.to_json()
        )
        project.save()
        return Response({"id": project.id})
```

### Example 9: Direct Mutations

```python
from vbrief import VAgendaDocument, ItemStatus
from vbrief.mutator import mutate_todo_list

# Load existing document
doc = VAgendaDocument.from_file("tasks.tron")

# Use mutator for direct changes
mutator = mutate_todo_list(doc.todo_list)

# Add new item
mutator.add_item("New urgent task", ItemStatus.PENDING)

# Update first item
mutator.update_item(0, status=ItemStatus.COMPLETED)

# Find and update multiple items
count = mutator.find_and_update(
    lambda item: item.status == ItemStatus.PENDING,
    status=ItemStatus.IN_PROGRESS
)
print(f"Updated {count} items")

# Save back
doc.to_file("tasks.tron")
```

### Example 10: Immutable Updates

```python
from vbrief import VAgendaDocument, ItemStatus
from vbrief.updater import ImmutableUpdater

# Load document
doc = VAgendaDocument.from_file("tasks.tron")

# Immutable updates (functional style)
original_data = doc.data

# Add item (returns new document)
updated = ImmutableUpdater.add_item(
    original_data,
    "New task",
    ItemStatus.PENDING
)

# Update first item (returns new document)
updated = ImmutableUpdater.update_item(updated, 0, status=ItemStatus.COMPLETED)

# Find and update (returns new document)
updated = ImmutableUpdater.find_and_update(
    updated,
    lambda item: item.status == ItemStatus.PENDING,
    status=ItemStatus.IN_PROGRESS
)

# Original is unchanged
print(f"Original: {len(original_data.todoList.items)} items")
print(f"Updated: {len(updated.todoList.items)} items")

# Create new document from updated data
new_doc = VAgendaDocument(updated)
print(new_doc.to_json(indent=2))
```

### Example 11: Validated Updates

```python
from vbrief import VAgendaDocument, ItemStatus
from vbrief.updater import create_updater

# Load document
doc = VAgendaDocument.from_file("tasks.tron")

# Create validated updater
updater = create_updater(doc.data)

# Add item with validation
result = updater.add_item("New task", ItemStatus.PENDING)
if not result.success:
    print(f"Validation failed: {result.errors}")

# Find and update with validation
result = updater.find_and_update(
    lambda item: item.status == ItemStatus.PENDING,
    status=ItemStatus.IN_PROGRESS
)

if result.success:
    print("All updates validated successfully")
    updated_doc = VAgendaDocument(updater.get_document())
    updated_doc.to_file("tasks.tron")
else:
    print(f"Updates rolled back: {result.errors}")
```

### Example 12: Transactional Updates with Context Manager

```python
from vbrief import VAgendaDocument, ItemStatus
from vbrief.updater import transaction
from vbrief.core.types import TodoItem

# Load document
doc = VAgendaDocument.from_file("tasks.tron")

# Use context manager for transactional updates
try:
    with transaction(doc.data) as txn:
        # All these operations happen together
        txn.todoList.items.append(
            TodoItem(title="Task 2", status=ItemStatus.PENDING)
        )
        txn.todoList.items.append(
            TodoItem(title="Task 3", status=ItemStatus.PENDING)
        )
        txn.todoList.items[0].status = ItemStatus.COMPLETED
        
    print("Transaction completed successfully")
    doc.to_file("tasks.tron")
    
except ValueError as e:
    print(f"Transaction rolled back: {e}")
```

### Example 13: Transactional Updates with ValidatedUpdater

```python
from vbrief import todo, ItemStatus
from vbrief.updater import create_updater

# Create initial document
initial_doc = todo("0.4").add_item("Task 1", ItemStatus.PENDING).build()

# Perform multiple updates atomically
updater = create_updater(initial_doc)

def batch_updates(upd):
    """Function that performs multiple updates."""
    result = upd.add_item("Task 2", ItemStatus.PENDING)
    if not result.success:
        return result
    
    result = upd.add_item("Task 3", ItemStatus.PENDING)
    if not result.success:
        return result
    
    result = upd.update_item(0, status=ItemStatus.IN_PROGRESS)
    return result

result = updater.transaction(batch_updates)

if result.success:
    print("Transaction completed")
    print(f"Total items: {len(result.document.todoList.items)}")
else:
    print(f"Transaction rolled back: {result.errors}")
    print(f"Original items: {len(initial_doc.todoList.items)}")
```

## CLI Tool Design

```bash
# Install
pip install vbrief

# Create a new TodoList
vbrief create todo --version 0.4 --output tasks.tron

# Add an item
vbrief add item tasks.tron "Implement auth" --status pending

# List items
vbrief list tasks.tron

# Filter by status
vbrief list tasks.tron --status pending

# Update item status
vbrief update tasks.tron 0 --status completed

# Convert formats
vbrief convert tasks.tron tasks.json --format json

# Validate document
vbrief validate tasks.tron

# Create a plan
vbrief create plan --title "Auth Implementation" --output plan.tron

# Add narrative
vbrief add narrative plan.tron proposal "Proposed Changes" "Use JWT tokens..."

# Serve web UI
vbrief serve tasks.tron --port 8000

# Watch file and validate on change
vbrief watch tasks.tron --validate
```

## Testing Strategy

### Unit Tests (pytest)

```python
# tests/test_builder.py

import pytest
from vbrief import todo, ItemStatus

def test_todo_builder_creates_valid_document():
    doc = (todo("0.4")
        .author("test-author")
        .add_item("Task 1", ItemStatus.PENDING)
        .build_document())
    
    assert doc.data.vBRIEFInfo.version == "0.4"
    assert doc.data.vBRIEFInfo.author == "test-author"
    assert len(doc.todo_list.items) == 1
    assert doc.todo_list.items[0].title == "Task 1"

def test_todo_builder_supports_chaining():
    builder = todo("0.4")
    result = (builder
        .author("author")
        .add_item("Item 1")
        .add_item("Item 2"))
    
    assert result is builder

def test_todo_builder_multiple_items():
    doc = (todo()
        .add_item("Item 1")
        .add_item("Item 2")
        .add_item("Item 3")
        .build_document())
    
    assert len(doc.todo_list.items) == 3
```

### Integration Tests

```python
# tests/test_round_trip.py

import pytest
from vbrief import todo, VAgendaDocument, ItemStatus

def test_json_round_trip():
    original = (todo("0.4")
        .add_item("Task 1", ItemStatus.PENDING)
        .build_document())
    
    json_str = original.to_json()
    parsed = VAgendaDocument.from_json(json_str)
    reparsed_json = parsed.to_json()
    
    assert json_str == reparsed_json

def test_tron_round_trip():
    original = (todo("0.4")
        .add_item("Task 1", ItemStatus.PENDING)
        .build_document())
    
    tron_str = original.to_tron()
    parsed = VAgendaDocument.from_tron(tron_str)
    reparsed_tron = parsed.to_tron()
    
    assert tron_str == reparsed_tron

def test_json_to_tron_conversion():
    doc = todo("0.4").add_item("Task").build_document()
    
    json_str = doc.to_json()
    tron_str = doc.to_tron()
    
    from_json = VAgendaDocument.from_json(json_str)
    from_tron = VAgendaDocument.from_tron(tron_str)
    
    assert from_json.data == from_tron.data
```

### Coverage Requirements
- Overall coverage: ≥80%
- Per-module coverage: ≥75%
- Critical paths: 100% (parser, validator)
- Exclude: CLI UI, examples

## Implementation Phases

### Phase 1: Core Foundation
- Core Pydantic models
- JSON parser/serializer
- Basic builders
- Core validation
- PyPI package setup

### Phase 2: Extensions
- Extension 1: Timestamps
- Extension 2: Identifiers
- Extension 3: Rich Metadata
- Extension 4: Hierarchical
- Extended validation

### Phase 3: TRON Support
- TRON parser implementation
- TRON serializer
- Format auto-detection
- Conversion utilities

### Phase 4: Framework Integration
- FastAPI integration
- Django integration
- LangChain tools
- Jupyter display helpers

### Phase 5: Tooling
- CLI tool (typer-based)
- VS Code extension support
- Web UI (optional)
- Documentation site

### Phase 6: Advanced Features
- Query interface with more filters
- Remaining extensions (5-12)
- Async support throughout
- Performance optimization

## Package Configuration

### pyproject.toml

```toml
[project]
name = "vbrief"
version = "0.1.0"
description = "Python library for working with vBRIEF documents"
authors = [{name = "Jonathan Taylor", email = "visionik@pobox.com"}]
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
keywords = ["vbrief", "todo", "plan", "agenda", "task", "memory", "agent"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0; python_version<'3.10'",
]

[project.optional-dependencies]
cli = ["typer>=0.9.0", "rich>=13.0.0"]
fastapi = ["fastapi>=0.100.0"]
django = ["django>=4.0"]
langchain = ["langchain>=0.1.0"]
all = ["vbrief[cli,fastapi,django,langchain]"]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
vbrief = "vbrief.cli:main"

[project.urls]
Homepage = "https://github.com/visionik/vBRIEF"
Documentation = "https://vbrief.readthedocs.io"
Repository = "https://github.com/visionik/vbrief-python"
Issues = "https://github.com/visionik/vBRIEF/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/vbrief"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "--cov=vbrief --cov-report=term-missing --cov-report=html"

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Standards and Compliance

### Code Quality
- Type hints on all public APIs
- Black for formatting
- Ruff for linting
- Mypy for type checking
- pytest for testing (≥80% coverage)
- Conventional commits

### Documentation
- Docstrings for all public APIs (Google style)
- README with quickstart
- Sphinx documentation
- Examples directory
- API reference

### Task Targets

```yaml
# Taskfile.yml additions
tasks:
  vbrief:py:install:
    desc: Install Python dependencies
    cmds:
      - pip install -e ".[dev]"

  vbrief:py:build:
    desc: Build Python package
    cmds:
      - python -m build

  vbrief:py:test:
    desc: Run Python tests
    cmds:
      - pytest

  vbrief:py:coverage:
    desc: Check test coverage
    cmds:
      - pytest --cov=vbrief --cov-report=term-missing

  vbrief:py:lint:
    desc: Lint Python code
    cmds:
      - ruff check src/ tests/
      - black --check src/ tests/

  vbrief:py:format:
    desc: Format Python code
    cmds:
      - black src/ tests/
      - ruff check --fix src/ tests/

  vbrief:py:typecheck:
    desc: Type check
    cmds:
      - mypy src/

  vbrief:cli:run:
    desc: Run CLI locally
    cmds:
      - python -m vbrief.cli {{.CLI_ARGS}}
```

## Runtime Support

The library targets:
- **Python**: ≥3.9
- **CPython**: 3.9, 3.10, 3.11, 3.12
- **PyPy**: 3.9, 3.10 (best effort)

## Open Questions

1. **TRON Parser Strategy**
   - Implement in Python or use external parser?
   - **Proposal**: Start with Python implementation, optimize later if needed

2. **Async vs Sync API**
   - Should core API be async?
   - **Proposal**: Sync core API, async variants where beneficial (file I/O, HTTP)

3. **Extension Model**
   - Use Pydantic inheritance or plugins?
   - **Proposal**: Inheritance for now, plugins if extension ecosystem grows

4. **Django vs FastAPI Priority**
   - Which framework to integrate first?
   - **Proposal**: FastAPI first (modern, async-native), Django second

5. **Dataclasses vs Pydantic**
   - Should we support plain dataclasses too?
   - **Proposal**: Pydantic only for validation benefits

## Related Work

- **Python Libraries**: pydantic, marshmallow, attrs (data modeling)
- **CLI Libraries**: typer, click, argparse
- **Similar Projects**:
  - todoist-python (Todoist API client)
  - python-jira (JIRA Python client)
  - Various task management libraries

## References

- vBRIEF Specification: https://github.com/visionik/vBRIEF
- Pydantic Documentation: https://docs.pydantic.dev/
- TRON Format: https://tron-format.github.io/
- FastAPI: https://fastapi.tiangolo.com/
- vBRIEF Go API: [vBRIEF-extension-api-go.md](./vBRIEF-extension-api-go.md)
- vBRIEF TypeScript API: [vBRIEF-extension-api-typescript.md](./vBRIEF-extension-api-typescript.md)

## Community Feedback

This is a **draft proposal**. Feedback needed:

1. Is Pydantic the right choice for data modeling?
2. Should we prioritize async support throughout?
3. What additional framework integrations would be valuable?
4. Should CLI be a separate package?
5. Are the builder patterns Pythonic enough?

**Discuss**: https://github.com/visionik/vBRIEF/discussions
