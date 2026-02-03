# Extension Documentation Structure Analysis

**Date**: 2025-12-28  
**Status**: Recommendation

## Current State

9 separate extension documents totaling ~10,400 lines:

| Document | Lines | Category | Purpose |
|----------|-------|----------|---------|
| `vBRIEF-extension-common.md` | 1,320 | Core | Extensions 1-12 (timestamps, IDs, metadata, etc.) |
| `vBRIEF-extension-security.md` | 1,201 | Domain | Security, permissions, access control |
| `vBRIEF-extension-MCP.md` | 1,668 | Integration | Model Context Protocol integration |
| `vBRIEF-extension-playbooks.md` | 534 | Core | Playbook format & patterns |
| `vBRIEF-extension-beads.md` | 753 | Integration | Beads framework integration |
| `vBRIEF-extension-claude.md` | 515 | Integration | Claude-specific features |
| `vBRIEF-extension-api-python.md` | 1,928 | API | Python library design |
| `vBRIEF-extension-api-typescript.md` | 1,989 | API | TypeScript library design |
| `vBRIEF-extension-api-go.md` | 493 | API | Go library status (implemented) |

## Analysis

### Natural Groupings

**Group 1: Core Extensions** (~3,055 lines)
- `extension-common.md` - Extensions 1-12
- `extension-security.md` - Security features
- `extension-playbooks.md` - Long-term memory

These define the vBRIEF spec itself.

**Group 2: Integrations** (~2,936 lines)
- `extension-MCP.md` - MCP protocol
- `extension-beads.md` - Beads framework
- `extension-claude.md` - Claude AI

These show how to integrate vBRIEF with specific tools/systems.

**Group 3: API Designs** (~4,410 lines)
- `extension-api-python.md` - Python implementation
- `extension-api-typescript.md` - TypeScript implementation  
- `extension-api-go.md` - Go implementation (already done)

These are language-specific API proposals/designs.

## Recommendation: **Keep Separate**

### Rationale

**1. Different Audiences**
- Core extensions: Anyone implementing vBRIEF
- Integrations: Users of specific tools (MCP/Beads/Claude)
- API designs: Language-specific implementers

**2. Independent Evolution**
- Each integration evolves with its external dependency
- API designs are proposals that may become separate repos
- Core extensions change with spec versions

**3. Navigation Benefits**
- Clear filenames make finding content easy
- Single consolidated file would be 10K+ lines
- Users can read only what's relevant to them

**4. Maintenance**
- Easier to update one integration without touching others
- Clear ownership per file (e.g., Python team owns api-python.md)
- Git history stays focused per concern

**5. Documentation Tools**
- Many doc generators work better with separate files
- Can build navigation/ToC from file structure
- Each file can have its own frontmatter/metadata

## Minor Improvements

### 1. Add Navigation Index

Create `extensions/README.md`:
```markdown
# vBRIEF Extensions

## Core Extensions
- [Common Extensions](./vBRIEF-extension-common.md) - Extensions 1-12
- [Security](./vBRIEF-extension-security.md) - Access control, permissions
- [Playbooks](./vBRIEF-extension-playbooks.md) - Long-term memory patterns

## Integrations
- [Model Context Protocol (MCP)](./vBRIEF-extension-MCP.md)
- [Beads Framework](./vBRIEF-extension-beads.md)
- [Claude AI](./vBRIEF-extension-claude.md)

## API Implementations
- [Python API](./vBRIEF-extension-api-python.md)
- [TypeScript API](./vBRIEF-extension-api-typescript.md)
- [Go API](./vBRIEF-extension-api-go.md) - ✅ Implemented
```

### 2. Move to `extensions/` Directory

Create clear separation:
```
vBRIEF/
├── extensions/
│   ├── README.md               # Navigation index
│   ├── common.md               # Core extensions
│   ├── security.md
│   ├── playbooks.md
│   ├── mcp.md                  # Integrations
│   ├── beads.md
│   ├── claude.md
│   └── api/                    # API designs
│       ├── python.md
│       ├── typescript.md
│       └── go.md
```

### 3. Cross-Reference Improvements

Add "See Also" sections:
- Common.md → references Security, Playbooks
- MCP.md → references Common (for extensions it uses)
- API docs → reference Common & relevant integrations

## Implementation

```yaml
docs:extensions:organize:
  desc: Organize extension documentation
  cmds:
    - mkdir -p extensions/api
    - cp vBRIEF-extension-common.md extensions/common.md
    - cp vBRIEF-extension-security.md extensions/security.md
    - cp vBRIEF-extension-playbooks.md extensions/playbooks.md
    - cp vBRIEF-extension-MCP.md extensions/mcp.md
    - cp vBRIEF-extension-beads.md extensions/beads.md
    - cp vBRIEF-extension-claude.md extensions/claude.md
    - cp vBRIEF-extension-api-python.md extensions/api/python.md
    - cp vBRIEF-extension-api-typescript.md extensions/api/typescript.md
    - cp vBRIEF-extension-api-go.md extensions/api/go.md
    # Create navigation index
    - cat > extensions/README.md < navigation_template.md
```

## Conclusion

**Do NOT consolidate.** The current separation is actually well-structured once organized into an `extensions/` directory with proper navigation.

Benefits of keeping separate:
- ✅ Clear audience targeting
- ✅ Independent evolution
- ✅ Easy navigation
- ✅ Better maintainability
- ✅ Focused git history

The only change needed is better organization and a navigation index.
