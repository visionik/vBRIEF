# vSpec Conversion Guidelines (Plan-Compatible)

Systematic approach to converting specifications (RFCs, PRDs, technical docs) into a Plan-compatible vBRIEF format while preserving all normative content and context.

## Core Principle

**Preserve, don't paraphrase.** The vSpec format is designed to capture structured machine-readable requirements while maintaining human context. When in doubt, include more detail rather than less.

---

## Conversion Workflow

### 1. Pre-Conversion Analysis

Before converting, identify:

- **Document type**: RFC, PRD, technical design, API spec, architecture decision
- **Normative keywords**: MUST, SHOULD, MAY, MUST NOT, SHOULD NOT (RFC 2119), or equivalent language
- **Section structure**: Introduction, problem statement, solution, constraints, requirements, risks, metrics
- **Cross-references**: Links to other specs, standards, related work
- **Implicit context**: Background knowledge assumed by the original document

### 2. Container-Level Mapping (Plan)

Map document-level content to `plan` fields (spec profile):

#### Required Fields
```json
{
  "title": "Extract from document title or heading",
  "status": "draft | proposed | approved | running | completed | cancelled",
  "type": "prd | rfc | technical-design | architecture | api-spec"
}
```

#### Narratives (lowercase keys)
Map prose sections to narrative keys. **Preserve original text** where possible:

```json
{
  "narratives": {
    "summary": "Executive summary (1-3 paragraphs, REQUIRED)",
    "problem": "Problem statement or motivation",
    "solution": "Proposed solution or approach",
    "background": "Context, prior work, current state",
    "scope": "In scope / out of scope / constraints",
    "alternatives": "Alternative approaches considered and rejected",
    "timeline": "Milestones, phases, dependencies"
  }
}
```

**Guideline**: Keep each narrative focused (1-3 paragraphs). Use Markdown formatting. Don't truncate important context.

#### Extension Fields
Add metadata that provides traceability:

```json
{
  "author": "Original author(s)",
  "tags": ["topical", "tags", "for", "discovery"],
  "uris": [
    {"uri": "https://original-doc-url", "type": "text/html", "title": "Original source"}
  ],
  "metadata": {
    "source_format": "RFC | Markdown | Confluence | JIRA | Google Docs",
    "conversion_date": "2026-01-11",
    "original_sections": ["list", "of", "section", "headings"]
  }
}
```

### 3. Item-Level Mapping (PlanItem)

Each discrete normative statement becomes a `PlanItem` (with `kind` in metadata or as an extension field).

#### Required Fields
```json
{
  "id": "Hierarchical ID (e.g., FR-1, NVT-3, OPT-2a)",
  "kind": "requirement | risk | metric | question | decision | constraint | dependency",
  "title": "Short descriptive title (1 line)",
  "status": "pending | running | completed | blocked | cancelled"
}
```

#### Priority Field (RFC 2119 Keywords)
Map normative language to priority:

| Original Language | priority | Notes |
|-------------------|----------|-------|
| MUST, SHALL, REQUIRED | `"must"` | Absolute requirement |
| MUST NOT, SHALL NOT | `"must-not"` | Absolute prohibition |
| SHOULD, RECOMMENDED | `"should"` | Strong recommendation |
| SHOULD NOT, NOT RECOMMENDED | `"should-not"` | Strong discouragement |
| MAY, OPTIONAL | `"may"` | Truly optional |

**Anti-pattern**: Don't infer priority when the source document doesn't use normative keywords. Leave `priority` field absent or use `metadata` to note uncertainty.

#### Narrative Fields (Title Case keys)

**Critical**: This is where information loss typically occurs. Use these fields to preserve **all** context from the original requirement.

##### Core Narrative Keys

**Description** (REQUIRED for requirements)
- **What to include**: The complete normative statement from the source
- **Length**: As long as needed (multi-paragraph if necessary)
- **Format**: Preserve conditional clauses, qualifiers, exceptions
- **Anti-pattern**: Don't reduce "If X, then Y MUST do Z" to "Y MUST do Z"

Example (GOOD):
```json
{
  "Description": "If a party receives what appears to be a request to enter some mode it is already in, the request SHOULD NOT be acknowledged. This non-response is essential to prevent endless loops in the negotiation. It is REQUIRED that a response be sent to requests for a change of mode — even if the mode is not changed."
}
```

Example (BAD - loses critical nuance):
```json
{
  "Description": "Requests for current mode SHOULD NOT be acknowledged."
}
```

**Acceptance Criteria** (REQUIRED for requirements)
- **What to include**: Testable, observable conditions that verify compliance
- **Format**: Bullet list (newline-separated, prefixed with `-`)
- **Coverage**: Must cover all clauses in Description
- **Source**: Extract from original text or derive from normative statements

Example:
```json
{
  "Acceptance Criteria": "- No acknowledgment sent if already in requested mode\n- Acknowledgment MUST be sent for mode change requests (even if mode unchanged)\n- Implementation prevents negotiation loops"
}
```

**Rationale**
- **What to include**: Why this requirement exists, what problem it solves
- **Source**: Often in parenthetical remarks, footnotes, or surrounding prose
- **When to use**: When the original document explains motivation

Example:
```json
{
  "Rationale": "This non-response is essential to prevent endless loops in the negotiation. The symmetry of the negotiation syntax can potentially lead to nonterminating acknowledgment loops."
}
```

**Context**
- **What to include**: Background information, assumptions, prior art
- **When to use**: When understanding requires knowledge not in Description

**Impact** (for risks)
- **What to include**: What happens if the risk occurs

**Mitigation** (for risks)
- **What to include**: How to prevent or reduce the risk

**Target**, **Baseline**, **Measurement** (for metrics)
- **What to include**: Success targets, starting values, measurement methods

**Options** (for questions)
- **What to include**: Possible answers or approaches being considered

**Decision**, **Alternatives Rejected** (for decisions)
- **What to include**: What was decided and why alternatives were rejected

##### Custom Narrative Keys

Use Title Case custom keys when the standard set doesn't fit:

```json
{
  "narrative": {
    "Description": "...",
    "Acceptance Criteria": "...",
    "Backward Compatibility": "Legacy systems must continue to work during migration",
    "Security Considerations": "Implementers must validate all inputs to prevent injection attacks",
    "Performance Implications": "This approach trades memory for latency (2x RAM, 50% faster)"
  }
}
```

#### Metadata Field

Use `metadata` for:
- **Structured data** that doesn't fit narrative prose
- **Traceability** to original document sections
- **Domain-specific fields** (numeric codes, categories, effort estimates)

```json
{
  "metadata": {
    "category": "functional | non-functional | constraint",
    "subcategory": "authentication | performance | security",
    "source_section": "3.2.1",
    "source_page": "p. 5",
    "rfc_section": "GENERAL CONSIDERATIONS",
    "code": 240,
    "effort_hours": 40,
    "team": "backend"
  }
}
```

### 4. Handling Compound Requirements

When a single paragraph contains multiple distinct normatives:

**Option A**: Split into multiple vSpecItems
```json
[
  {
    "id": "OPT-2a",
    "kind": "requirement",
    "title": "Option negotiation: No ack for same-mode requests",
    "priority": "should-not",
    "narrative": {
      "Description": "If a party receives what appears to be a request to enter some mode it is already in, the request SHOULD NOT be acknowledged.",
      "Rationale": "This non-response is essential to prevent endless loops in the negotiation."
    }
  },
  {
    "id": "OPT-2b",
    "kind": "requirement",
    "title": "Option negotiation: Must respond to mode-change requests",
    "priority": "must",
    "narrative": {
      "Description": "It is REQUIRED that a response be sent to requests for a change of mode — even if the mode is not changed.",
      "Rationale": "Ensures requester knows request was processed, even if rejected."
    }
  }
]
```

**Option B**: Keep as single item with both clauses in Description
```json
{
  "id": "OPT-2",
  "kind": "requirement",
  "title": "Option negotiation: Acknowledgment rules prevent loops",
  "priority": "should-not",
  "narrative": {
    "Description": "If a party receives what appears to be a request to enter some mode it is already in, the request SHOULD NOT be acknowledged. This non-response is essential to prevent endless loops in the negotiation. It is REQUIRED that a response be sent to requests for a change of mode — even if the mode is not changed.",
    "Acceptance Criteria": "- No acknowledgment sent if already in requested mode\n- Acknowledgment MUST be sent for change-of-mode requests\n- Prevents negotiation loops"
  }
}
```

**When to split**: If the two clauses have different priorities, actors, or acceptance criteria.

**When to keep together**: If they form a coherent rule (e.g., "don't do X, but do Y").

### 5. Handling Implicit Information

Some requirements have implicit context that must be made explicit:

#### Scope/Applicability
Original: "The NVT printer recognizes code 10."
Enhanced:
```json
{
  "Description": "The NVT printer MUST recognize code 10 (Line Feed/LF) and move the printer to the next print line, keeping the same horizontal position.",
  "Context": "This applies to all TELNET implementations. The NVT (Network Virtual Terminal) is the canonical terminal abstraction defined in this RFC."
}
```

#### Timing/Ordering
Original: "Command must be inserted in the data stream."
Enhanced:
```json
{
  "Description": "Whenever one party sends an option command to a second party, whether as a request or an acknowledgment, and use of the option will have any effect on the processing of the data being sent from the first party to the second, then the command MUST be inserted in the data stream at the point where it is desired that it take effect.",
  "Rationale": "Ensures correct ordering of data and mode changes. The receiver processes the option at the correct position in the stream.",
  "Acceptance Criteria": "- Option commands placed in-stream at the effect point\n- Commands sent before affected data\n- Receiver processes option before subsequent data"
}
```

#### Exception Cases
Original: "Party may not send a request to announce mode."
Enhanced:
```json
{
  "Description": "Parties MUST only request a change in option status; i.e., a party MUST NOT send out a request merely to announce what mode it is in.",
  "Rationale": "Prevents gratuitous status announcements that waste bandwidth and risk triggering spurious negotiations.",
  "Acceptance Criteria": "- Requests only sent when desiring a mode change\n- No unsolicited status announcements via option commands"
}
```

---

## Common Anti-Patterns to Avoid

### 1. Over-Paraphrasing
❌ **Bad**: "Commands must be in-stream."
✅ **Good**: "Whenever one party sends an option command to a second party, whether as a request or an acknowledgment, and use of the option will have any effect on the processing of the data being sent from the first party to the second, then the command MUST be inserted in the data stream at the point where it is desired that it take effect."

### 2. Dropping Qualifiers
❌ **Bad**: "Request SHOULD NOT be acknowledged."
✅ **Good**: "If a party receives what appears to be a request to enter some mode it is already in, the request SHOULD NOT be acknowledged."

### 3. Losing Rationale
❌ **Bad**: Description only, no Rationale field.
✅ **Good**: Description + Rationale field with "This non-response is essential to prevent endless loops in the negotiation."

### 4. Incomplete Acceptance Criteria
❌ **Bad**: "- Request not acknowledged"
✅ **Good**: "- No acknowledgment sent if already in requested mode\n- Acknowledgment MUST be sent for change-of-mode requests\n- Prevents negotiation loops"

### 5. Missing Second Clause
❌ **Bad**: Only captures "SHOULD NOT acknowledge same mode."
✅ **Good**: Captures both "SHOULD NOT acknowledge same mode" AND "MUST respond to mode-change requests."

### 6. Ambiguous Priority
❌ **Bad**: `priority: "should-not"` when document has both SHOULD NOT and MUST clauses.
✅ **Good**: Split into two items (OPT-2a with `should-not`, OPT-2b with `must`) OR keep combined and note in Description.

---

## Validation Checklist

Before finalizing a vSpec conversion, verify:

### Container Level
- [ ] All major sections from original document mapped to narratives
- [ ] `summary` narrative is present and captures key points
- [ ] `scope` narrative clarifies boundaries (in-scope / out-scope / constraints)
- [ ] `uris` field links back to original source
- [ ] `author`, `tags`, `metadata` fields populated for traceability

### Item Level
For each vSpecItem:
- [ ] `title` is descriptive and unique
- [ ] `kind` is appropriate (requirement vs. decision vs. risk vs. constraint)
- [ ] `priority` matches original normative keywords (or is absent if unclear)
- [ ] `narrative["Description"]` contains **complete** normative text
- [ ] All conditional clauses preserved ("if X, then Y")
- [ ] All qualifiers preserved ("whether as a request or an acknowledgment")
- [ ] `narrative["Rationale"]` captures **why** (if present in source)
- [ ] `narrative["Acceptance Criteria"]` covers **all** clauses in Description
- [ ] Compound requirements either split appropriately or kept together with clear criteria
- [ ] `metadata` captures traceability (source section, page, code, etc.)

### Cross-Cutting
- [ ] No information from original document was dropped
- [ ] All normative statements (MUST/SHOULD/MAY) are captured
- [ ] All rationale, context, and "why" information is preserved
- [ ] Related items reference each other (via `dependencies` or cross-references in narratives)
- [ ] Implicit information is made explicit (scope, timing, exceptions)

---

## Example: Converting RFC Text (Detailed)

### Original RFC Text
```
b. If a party receives what appears to be a request to enter some
mode it is already in, the request should not be acknowledged.
This non-response is essential to prevent endless loops in the
negotiation.  It is required that a response be sent to requests
for a change of mode -- even if the mode is not changed.
```

### Conversion Process

**Step 1**: Identify normative keywords
- "should not be acknowledged" → SHOULD NOT
- "is required" → MUST

**Step 2**: Identify distinct requirements
- Clause 1: SHOULD NOT acknowledge same-mode requests
- Clause 2: MUST respond to change-of-mode requests

**Step 3**: Extract rationale
- "This non-response is essential to prevent endless loops"

**Step 4**: Decide: split or combine?
- These are related but have different priorities
- Option: Combine with compound acceptance criteria

**Step 5**: Create vSpecItem

```json
{
  "id": "OPT-2",
  "kind": "requirement",
  "title": "Option negotiation: Selective acknowledgment prevents loops",
  "status": "completed",
  "priority": "should-not",
  "narrative": {
    "Description": "If a party receives what appears to be a request to enter some mode it is already in, the request SHOULD NOT be acknowledged. This non-response is essential to prevent endless loops in the negotiation. It is REQUIRED that a response be sent to requests for a change of mode — even if the mode is not changed.",
    "Rationale": "The symmetry of the negotiation syntax can potentially lead to nonterminating acknowledgment loops. By not acknowledging same-mode requests, implementations prevent these loops. However, change-of-mode requests must receive a response so the requester knows the request was processed.",
    "Acceptance Criteria": "- If request is for current mode: SHOULD NOT send acknowledgment\n- If request is for different mode: MUST send response (accept or reject)\n- Even if mode doesn't change (request rejected), response MUST be sent\n- Implementation prevents negotiation loops"
  },
  "metadata": {
    "category": "option-negotiation-rule",
    "rfc_section": "GENERAL CONSIDERATIONS",
    "rule_label": "3.b"
  }
}
```

**Step 6**: Validate
- ✅ Complete original text in Description
- ✅ Rationale extracted and expanded
- ✅ Both SHOULD NOT and MUST clauses in Acceptance Criteria
- ✅ "Even if the mode is not changed" clause preserved
- ✅ Anti-loop rationale explicit

---

## Tools and Automation

### Recommended Approach
1. **Manual first pass**: Human converts document section-by-section
2. **LLM-assisted extraction**: Use AI to extract normative statements, but **always verify**
3. **Validation script**: Automated check for missing fields, short Descriptions, missing Rationale

### Validation Script Heuristics
```python
def validate_vspec_item(item):
    warnings = []
    
    # Check Description length (if too short, likely paraphrased)
    desc = item.get('narrative', {}).get('Description', '')
    if item['kind'] == 'requirement' and len(desc) < 50:
        warnings.append(f"{item['id']}: Description suspiciously short")
    
    # Check for missing Rationale when "prevent" or "essential" in Description
    if any(word in desc.lower() for word in ['prevent', 'essential', 'avoid', 'because']):
        if 'Rationale' not in item.get('narrative', {}):
            warnings.append(f"{item['id']}: Rationale likely missing (detected reason-words in Description)")
    
    # Check for compound normatives
    normatives = ['MUST', 'SHOULD', 'MAY', 'MUST NOT', 'SHOULD NOT']
    count = sum(desc.upper().count(n) for n in normatives)
    if count > 1 and len(item.get('narrative', {}).get('Acceptance Criteria', '').split('\n')) < count:
        warnings.append(f"{item['id']}: Multiple normatives but acceptance criteria may be incomplete")
    
    return warnings
```

---

## Summary

**Golden Rule**: When converting to vSpec, treat it as **structured preservation**, not summarization.

The vSpec format exists to make requirements machine-readable and traceable while keeping them human-understandable. Information loss defeats this purpose.

**Key practices**:
1. Preserve complete normative text in `Description`
2. Extract rationale to `Rationale` field
3. Cover all clauses in `Acceptance Criteria`
4. Use `metadata` for traceability
5. Split compound requirements only when priorities differ
6. Make implicit information explicit in narrative fields
7. Validate that no information was dropped

**When in doubt**: Include more detail, not less. Future readers (and tools) will thank you.
