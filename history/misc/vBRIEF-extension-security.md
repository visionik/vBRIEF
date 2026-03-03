# vBRIEF Extension Proposal: Security & Privacy

> **VERY EARLY DRAFT**: This is an initial proposal and subject to significant change. Comments, feedback, and suggestions are strongly encouraged. Please provide input via GitHub issues or discussions.

**Extension Name**: Security & Privacy  
**Version**: 0.1 (Draft)  
**Status**: Proposal  
**Author**: Jonathan Taylor (visionik@pobox.com)  
**Date**: 2025-12-27

## Overview

This extension defines security and privacy mechanisms for vBRIEF documents, inspired by [vCon (Virtualized Conversations)](https://datatracker.ietf.org/wg/vcon/about/) which standardizes security for conversational data. Like vCon, vBRIEF documents can exist in three security modes: **unsigned** (trusted environments), **signed** (integrity verification), and **encrypted** (confidentiality protection).

Additionally, this extension addresses privacy compliance requirements (GDPR, CCPA, HIPAA) through redaction mechanisms, consent tracking, and data minimization patterns.

## Motivation

**Security requirements for vBRIEF:**
- **Data integrity**: Verify that todos, plans, and playbooks haven't been tampered with
- **Authentication**: Confirm the identity of document creators and modifiers
- **Confidentiality**: Protect sensitive information (business strategies, security plans, proprietary learnings)
- **Non-repudiation**: Provide proof of authorship for important decisions and plans
- **Access control**: Enable different visibility levels for different users/agents

**Privacy requirements:**
- **GDPR compliance**: Right to access, right to be forgotten, right to rectification
- **Data minimization**: Only include necessary information
- **Consent management**: Track permissions for data processing
- **Redaction**: Remove or mask sensitive information while preserving structure
- **Audit trails**: Track who accessed or modified personal data

**Integration goal**: Make vBRIEF documents securable and privacy-compliant by default, enabling use in enterprise, healthcare, legal, and regulated environments.

## Dependencies

**Required**:
- Core vBRIEF types (vBRIEFInfo, TodoList, TodoItem, Plan, PlanItem, Narrative)
- Extension 1 (Timestamps) - for temporal validity and expiration
- Extension 2 (Identifiers) - for tracking entities and consent

**Recommended**:
- Extension 6 (Participants) - for user identity and roles
- Extension 10 (Version Control) - for tracking modifications
- Extension 12 (Playbooks) - for redacted learnings in playbooks

## Security Modes

vBRIEF documents can exist in three forms, analogous to vCon:

### 1. Unsigned (Trusted Environments)

Plain vBRIEF document with no cryptographic protection.

**Use cases**:
- Local development
- Single-user scenarios
- Internal trusted networks
- Testing and debugging

**Example structure**:
```json
{
  "vBRIEFInfo": {
    "version": "0.4",
    "securityMode": "unsigned"
  },
  "todoList": {
    "items": [...]
  }
}
```

### 2. Signed (Integrity Verification)

vBRIEF document wrapped in JSON Web Signature (JWS) [RFC 7515].

**Use cases**:
- Verify document hasn't been modified
- Prove authorship of plans or decisions
- Detect tampering in transit
- Non-repudiation for important work
- Multi-agent environments where trust verification is needed

**Structure**: JWS Compact Serialization
```
eyJhbGciOiJFUzI1NiIsInR5cCI6Ikp...  (header)
.
eyJ2QWdlbmRhSW5mbyI6eyJ2ZXJzaW9...  (payload: base64url-encoded vBRIEF)
.
MEUCIQDKZokl-...                      (signature)
```

**Header example**:
```json
{
  "alg": "ES256",
  "typ": "vBRIEF+jws",
  "kid": "agent-key-2024-12-27",
  "iat": 1735348800
}
```

**Verification workflow**:
1. Parse JWS compact serialization
2. Decode header and payload
3. Verify signature using public key (from `kid`)
4. Validate timestamp (`iat`) is recent
5. Parse payload as vBRIEF document

### 3. Encrypted (Confidentiality Protection)

vBRIEF document wrapped in JSON Web Encryption (JWE) [RFC 7516].

**Use cases**:
- Sensitive business plans
- Security incident response plans
- Healthcare-related tasks
- Proprietary strategies in playbooks
- Regulated data (PII, PHI, financial)
- Zero-knowledge storage (server can't read contents)

**Structure**: JWE Compact Serialization
```
eyJhbGciOiJSU0EtT0FFUCIsImVuYy...  (header)
.
GciOiJSU0EtT0FFUCIsImVuYyI6IkE...  (encrypted key)
.
48V1_ALb6US04U3b...                  (IV)
.
5eym8TW_c8SuK0ltJ3rpYIzOeDQz7TA...  (ciphertext: encrypted vBRIEF)
.
XFBoMYUZodetZdvTiFvSkQ                (auth tag)
```

**Header example**:
```json
{
  "alg": "RSA-OAEP",
  "enc": "A256GCM",
  "typ": "vBRIEF+jwe",
  "kid": "recipient-key-abc123"
}
```

**Decryption workflow**:
1. Parse JWE compact serialization
2. Decrypt content encryption key (CEK) using recipient's private key
3. Use CEK to decrypt ciphertext
4. Parse decrypted payload as vBRIEF document

## New Types

### SecurityInfo

Document-level security metadata.

```javascript
SecurityInfo {
  mode: enum              # "unsigned" | "signed" | "encrypted"
  algorithm?: string      # "ES256" | "RS256" | "RSA-OAEP" | etc.
  keyId?: string          # Reference to key used (JWK kid)
  signedBy?: string       # Identity of signer (email, DID, etc.)
  signedAt?: datetime     # When signature was created
  encryptedFor?: string[] # Intended recipients (key IDs or identities)
  expiresAt?: datetime    # Signature/encryption expiry
}
```

### RedactionInfo

Tracks what was redacted and why.

```javascript
RedactionInfo {
  type: enum              # "hash" | "mask" | "remove"
  reason?: string         # Why redacted (e.g., "PII", "confidential")
  redactedBy?: string     # Who performed redaction
  redactedAt?: datetime   # When redaction occurred
  hash?: string           # Hash of original content (if type = "hash")
  recoverable: boolean    # Can authorized users recover original?
}
```

### ConsentRecord

Tracks consent for data processing (GDPR Article 6, 7).

```javascript
ConsentRecord {
  subject: string         # User/entity who gave consent
  purpose: string[]       # What data can be used for
  grantedAt: datetime     # When consent was given
  expiresAt?: datetime    # When consent expires
  revocable: boolean      # Can consent be withdrawn?
  revokedAt?: datetime    # When/if consent was revoked
  scope: string[]         # Which parts of document (IDs)
  legalBasis?: string     # GDPR legal basis (e.g., "consent", "legitimate interest")
  proof?: string          # Evidence of consent (signature, recording URL)
}
```

### AccessControl

Per-document or per-item access rules.

```javascript
AccessControl {
  owner: string           # Primary owner identity
  readers?: string[]      # Who can read (user IDs, emails, roles)
  writers?: string[]      # Who can modify
  admins?: string[]       # Who can change permissions
  public: boolean         # Is this publicly accessible?
  inheritFrom?: string    # Inherit permissions from parent
}
```

## vBRIEFInfo Extensions

```javascript
vBRIEFInfo {
  // Core fields...
  security?: SecurityInfo      # Security mode and metadata
  accessControl?: AccessControl # Who can access this document
  consents?: ConsentRecord[]   # Consent records for data subjects
  redactionPolicy?: string     # Policy governing redactions
}
```

## TodoItem Extensions

```javascript
TodoItem {
  // Prior extensions...
  redacted?: RedactionInfo     # If this item was redacted
  accessControl?: AccessControl # Item-specific access rules
  containsPII?: boolean        # Flag for privacy-sensitive data
  dataSubjects?: string[]      # People whose data is referenced
}
```

## Plan Extensions

```javascript
Plan {
  // Prior extensions...
  classification?: enum        # "public" | "internal" | "confidential" | "secret"
  redacted?: RedactionInfo     # If plan was redacted
  accessControl?: AccessControl # Plan-specific access rules
  dataRetention?: duration     # How long to keep (ISO 8601)
  legalHold?: boolean          # Prevent deletion for legal reasons
}
```

## PlanItem Extensions

```javascript
PlanItem {
  // Prior extensions...
  accessControl?: AccessControl # PlanItem-specific access rules
}
```

## Narrative Extensions

```javascript
Narrative {
  // Prior extensions...
  redacted?: RedactionInfo     # If narrative was redacted
}
```

## Playbook extensions

For Extension 12 (Playbooks):

```javascript
Learning {
  // Prior extensions...
  classification?: enum        # Security level of learning
  redacted?: RedactionInfo     # If learning was redacted
  shareableWith?: string[]     # Who can see this learning
}
```

## Usage Patterns

### Pattern 1: Signed Plan for Approval

**Use case**: Create a technical design plan, sign it, share for stakeholder approval.

```typescript
// 1. Create unsigned plan
const plan: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    author: "alice@example.com"
  },
  plan: {
    title: "Database Migration to PostgreSQL",
    status: "proposed",
    narratives: {
      proposal: {
        content: "Migrate from MySQL to PostgreSQL for better JSON support..."
      }
    },
    items: [...]
  }
};

// 2. Sign the plan
import { SignJWT } from 'jose';

const privateKey = await loadPrivateKey("alice-signing-key");
const jwt = await new SignJWT(plan)
  .setProtectedHeader({ 
    alg: 'ES256', 
    typ: 'vBRIEF+jws',
    kid: 'alice-key-2024'
  })
  .setIssuedAt()
  .setExpirationTime('30d')
  .sign(privateKey);

// 3. Share signed JWS
await shareWithStakeholders(jwt);

// 4. Recipients verify signature
import { jwtVerify } from 'jose';

const publicKey = await loadPublicKey("alice-key-2024");
const { payload } = await jwtVerify(jwt, publicKey);
// payload is now verified vBRIEF plan
```

### Pattern 2: Encrypted TodoList for Security Team

**Use case**: Security incident response checklist with sensitive information.

```typescript
// 1. Create sensitive todo list
const todoList: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    classification: "confidential"
  },
  todoList: {
    items: [
      {
        title: "Patch vulnerability CVE-2024-1234",
        status: "inProgress",
        description: "Critical RCE in auth module..."
      },
      {
        title: "Notify affected customers",
        status: "pending",
        description: "Customer list in private/customers.csv"
      }
    ]
  }
};

// 2. Encrypt for security team
import { CompactEncrypt } from 'jose';

const recipientPublicKey = await loadPublicKey("security-team-2024");
const jwe = await new CompactEncrypt(
  new TextEncoder().encode(JSON.stringify(todoList))
)
  .setProtectedHeader({ 
    alg: 'RSA-OAEP', 
    enc: 'A256GCM',
    typ: 'vBRIEF+jwe',
    kid: 'security-team-2024'
  })
  .encrypt(recipientPublicKey);

// 3. Store encrypted document
await store.save("incident-2024-12-27.jwe", jwe);

// 4. Security team decrypts
import { compactDecrypt } from 'jose';

const privateKey = await loadPrivateKey("security-team-2024");
const { plaintext } = await compactDecrypt(jwe, privateKey);
const decrypted = JSON.parse(new TextDecoder().decode(plaintext));
// decrypted is now the original vBRIEF document
```

### Pattern 3: Redaction for Public Sharing

**Use case**: Share a project plan publicly but redact proprietary details.

```typescript
// Original plan (internal)
const internalPlan: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    classification: "internal"
  },
  plan: {
    title: "Q1 2025 Product Launch",
    narratives: {
      proposal: {
        content: "Launch new AI-powered feature..."
      },
      decision: {
        content: "Use OpenAI GPT-4 API (cost: $50k/mo, negotiated rate)..."
      }
    }
  }
};

// Redact sensitive narratives
const publicPlan: VAgendaDocument = {
  ...internalPlan,
  vBRIEFInfo: {
    ...internalPlan.vBRIEFInfo,
    classification: "public"
  },
  plan: {
    ...internalPlan.plan,
    narratives: {
      proposal: internalPlan.plan.narratives.proposal,
      decision: {
        content: "[REDACTED: Vendor selection and pricing details]",
        redacted: {
          type: "remove",
          reason: "confidential",
          redactedBy: "alice@example.com",
          redactedAt: "2024-12-27T12:00:00Z",
          hash: "sha256:abc123...",  // Hash of original
          recoverable: true  // Authorized users can see original
        }
      }
    }
  }
};

// Share public version
await publishToGitHub(publicPlan);
```

### Pattern 4: GDPR Right to Access

**Use case**: User requests all their data (GDPR Article 15).

```typescript
// System searches for user's data
const userEmail = "bob@example.com";

// Find all vBRIEF documents mentioning user
const documents = await searchDocuments({
  author: userEmail,
  assignee: userEmail,
  dataSubjects: userEmail
});

// Package for export
const exportPackage = {
  request: {
    subject: userEmail,
    requestedAt: new Date().toISOString(),
    type: "right_to_access"
  },
  documents: documents.map(doc => ({
    ...doc,
    _metadata: {
      retrieved: new Date().toISOString(),
      source: "vBRIEF system"
    }
  }))
};

// Send to user
await emailExport(userEmail, exportPackage);
```

### Pattern 5: GDPR Right to Be Forgotten

**Use case**: User requests deletion of their data (GDPR Article 17).

```typescript
const userEmail = "charlie@example.com";

// Find all references
const documents = await searchDocuments({
  author: userEmail,
  assignee: userEmail,
  dataSubjects: userEmail,
  participantEmails: userEmail
});

// Redact or delete
for (const doc of documents) {
  if (doc.vBRIEFInfo.legalHold) {
    // Cannot delete - legal hold active
    console.warn(`Cannot delete ${doc.id} - legal hold`);
    continue;
  }
  
  // Option 1: Full deletion
  await deleteDocument(doc.id);
  
  // Option 2: Redaction (preserves structure)
  const redacted = redactUserData(doc, userEmail);
  await updateDocument(doc.id, redacted);
}

// Log deletion for compliance
await auditLog.record({
  action: "right_to_be_forgotten",
  subject: userEmail,
  documentsAffected: documents.length,
  timestamp: new Date().toISOString()
});
```

### Pattern 6: Consent Management

**Use case**: Track user consent for AI analysis of their work.

```typescript
// User grants consent for AI analysis
const consent: ConsentRecord = {
  subject: "alice@example.com",
  purpose: ["ai_analysis", "productivity_insights"],
  grantedAt: "2024-12-27T10:00:00Z",
  expiresAt: "2025-12-27T10:00:00Z",
  revocable: true,
  scope: ["todoList", "plan"],  // What can be analyzed
  legalBasis: "consent",
  proof: "signed_form_abc123.pdf"
};

// Add to document
const doc: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    consents: [consent]
  },
  todoList: {
    items: [...]
  }
};

// Before running AI analysis, check consent
function canAnalyze(doc: VAgendaDocument, purpose: string): boolean {
  const now = new Date();
  
  return doc.vBRIEFInfo.consents?.some(consent => 
    consent.purpose.includes(purpose) &&
    !consent.revokedAt &&
    (!consent.expiresAt || new Date(consent.expiresAt) > now)
  ) ?? false;
}

if (canAnalyze(doc, "ai_analysis")) {
  await runAIAnalysis(doc);
} else {
  throw new Error("No valid consent for AI analysis");
}
```

### Pattern 7: Multi-Level Classification

**Use case**: Organization with different security levels.

```typescript
// Public roadmap plan
const publicPlan: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    classification: "public",
    accessControl: {
      owner: "product-team",
      public: true
    }
  },
  plan: {
    title: "Q1 2025 Public Roadmap",
    classification: "public",
    items: [...]
  }
};

// Internal implementation plan (linked to public)
const internalPlan: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    classification: "internal",
    accessControl: {
      owner: "engineering",
      readers: ["engineering", "product"],
      public: false
    }
  },
  plan: {
    title: "Q1 2025 Implementation Details",
    classification: "internal",
    narratives: {
      proposal: {
        content: "Detailed technical approach..."
      }
    },
    items: [
      {
        title: "Backend API Development",
        classification: "internal"
      }
    ]
  }
};

// Confidential security hardening plan
const confidentialPlan: VAgendaDocument = {
  vBRIEFInfo: {
    version: "0.4",
    classification: "confidential",
    accessControl: {
      owner: "security-team",
      readers: ["security-team", "cto"],
      public: false
    }
  },
  plan: {
    title: "Security Hardening Q1 2025",
    classification: "confidential",
    items: [
      {
        title: "Penetration Testing",
        classification: "confidential",
        accessControl: {
          readers: ["security-team"]  // Even more restricted
        }
      }
    ]
  }
};

// Check access before displaying
function canAccess(doc: VAgendaDocument, user: User): boolean {
  const ac = doc.vBRIEFInfo.accessControl;
  
  if (ac?.public) return true;
  if (ac?.owner === user.id) return true;
  if (ac?.readers?.includes(user.role)) return true;
  if (ac?.readers?.includes(user.id)) return true;
  
  return false;
}
```

## Implementation Notes

### Signing Implementation

```typescript
// Sign a vBRIEF document
import { SignJWT, importPKCS8 } from 'jose';

async function signDocument(
  doc: VAgendaDocument,
  privateKeyPem: string,
  keyId: string
): Promise<string> {
  const privateKey = await importPKCS8(privateKeyPem, 'ES256');
  
  const jws = await new SignJWT(doc)
    .setProtectedHeader({
      alg: 'ES256',
      typ: 'vBRIEF+jws',
      kid: keyId
    })
    .setIssuedAt()
    .setExpirationTime('30d')
    .sign(privateKey);
  
  return jws;
}

// Verify a signed vBRIEF document
import { jwtVerify, importSPKI } from 'jose';

async function verifyDocument(
  jws: string,
  publicKeyPem: string
): Promise<VAgendaDocument> {
  const publicKey = await importSPKI(publicKeyPem, 'ES256');
  
  const { payload } = await jwtVerify(jws, publicKey, {
    typ: 'vBRIEF+jws'
  });
  
  return payload as VAgendaDocument;
}
```

### Encryption Implementation

```typescript
// Encrypt a vBRIEF document
import { CompactEncrypt, importSPKI } from 'jose';

async function encryptDocument(
  doc: VAgendaDocument,
  recipientPublicKeyPem: string,
  recipientKeyId: string
): Promise<string> {
  const publicKey = await importSPKI(recipientPublicKeyPem, 'RSA-OAEP');
  
  const jwe = await new CompactEncrypt(
    new TextEncoder().encode(JSON.stringify(doc))
  )
    .setProtectedHeader({
      alg: 'RSA-OAEP',
      enc: 'A256GCM',
      typ: 'vBRIEF+jwe',
      kid: recipientKeyId
    })
    .encrypt(publicKey);
  
  return jwe;
}

// Decrypt a vBRIEF document
import { compactDecrypt, importPKCS8 } from 'jose';

async function decryptDocument(
  jwe: string,
  privateKeyPem: string
): Promise<VAgendaDocument> {
  const privateKey = await importPKCS8(privateKeyPem, 'RSA-OAEP');
  
  const { plaintext } = await compactDecrypt(jwe, privateKey);
  
  return JSON.parse(new TextDecoder().decode(plaintext));
}
```

### Redaction Implementation

```typescript
// Redact sensitive content
function redactContent(
  original: string,
  type: 'hash' | 'mask' | 'remove',
  reason: string
): { content: string, redactionInfo: RedactionInfo } {
  let content: string;
  let hash: string | undefined;
  
  switch (type) {
    case 'hash':
      // Replace with hash of original
      hash = sha256(original);
      content = `[REDACTED: ${hash.substring(0, 16)}...]`;
      break;
    
    case 'mask':
      // Show length but mask content
      const length = original.length;
      content = '*'.repeat(Math.min(length, 50));
      if (length > 50) content += `... (${length} chars)`;
      break;
    
    case 'remove':
      // Replace with placeholder
      content = `[REDACTED: ${reason}]`;
      break;
  }
  
  const redactionInfo: RedactionInfo = {
    type,
    reason,
    redactedBy: getCurrentUser(),
    redactedAt: new Date().toISOString(),
    hash,
    recoverable: type === 'hash' || type === 'mask'
  };
  
  return { content, redactionInfo };
}

// Apply redaction to a document
function redactDocument(
  doc: VAgendaDocument,
  redactionRules: Array<{
    path: string[];  // e.g., ["plan", "narratives", "decision"]
    type: 'hash' | 'mask' | 'remove';
    reason: string;
  }>
): VAgendaDocument {
  const redacted = structuredClone(doc);
  
  for (const rule of redactionRules) {
    // Navigate to target field
    let current: any = redacted;
    for (let i = 0; i < rule.path.length - 1; i++) {
      current = current[rule.path[i]];
    }
    
    const field = rule.path[rule.path.length - 1];
    const original = current[field];
    
    // Redact the content
    const { content, redactionInfo } = redactContent(
      typeof original === 'string' ? original : JSON.stringify(original),
      rule.type,
      rule.reason
    );
    
    // Update document
    if (typeof original === 'string') {
      current[field] = content;
    } else {
      current[field] = {
        ...original,
        content
      };
    }
    
    // Add redaction metadata
    current[`${field}Redacted`] = redactionInfo;
  }
  
  return redacted;
}
```

### Access Control Implementation

```typescript
interface User {
  id: string;
  email: string;
  roles: string[];
}

class AccessControlService {
  canRead(doc: VAgendaDocument, user: User): boolean {
    const ac = doc.vBRIEFInfo.accessControl;
    if (!ac) return true;  // No AC = public
    
    if (ac.public) return true;
    if (ac.owner === user.id) return true;
    if (ac.readers?.includes(user.id)) return true;
    if (ac.readers?.some(r => user.roles.includes(r))) return true;
    if (ac.admins?.includes(user.id)) return true;
    
    return false;
  }
  
  canWrite(doc: VAgendaDocument, user: User): boolean {
    const ac = doc.vBRIEFInfo.accessControl;
    if (!ac) return true;
    
    if (ac.owner === user.id) return true;
    if (ac.writers?.includes(user.id)) return true;
    if (ac.writers?.some(r => user.roles.includes(r))) return true;
    if (ac.admins?.includes(user.id)) return true;
    
    return false;
  }
  
  canAdmin(doc: VAgendaDocument, user: User): boolean {
    const ac = doc.vBRIEFInfo.accessControl;
    if (!ac) return true;
    
    if (ac.owner === user.id) return true;
    if (ac.admins?.includes(user.id)) return true;
    
    return false;
  }
  
  filterDocumentForUser(
    doc: VAgendaDocument,
    user: User
  ): VAgendaDocument | null {
    // Check document-level access
    if (!this.canRead(doc, user)) return null;
    
    const filtered = structuredClone(doc);
    
    // Filter todo items
    if (filtered.todoList) {
      filtered.todoList.items = filtered.todoList.items.filter(item => {
        const itemAC = item.accessControl;
        if (!itemAC) return true;
        
        // Apply same logic as document-level
        return this.canRead({ vBRIEFInfo: { accessControl: itemAC } } as any, user);
      });
    }
    
    // Filter plan phases
    if (filtered.plan) {
      filtered.plan.items = filtered.plan.items?.filter(item => {
        const itemAC = item.accessControl;
        if (!itemAC) return true;
        
        return this.canRead({ vBRIEFInfo: { accessControl: itemAC } } as any, user);
      });
    }
    
    return filtered;
  }
}
```

## Security Considerations

### Key Management

**DO**:
- Use hardware security modules (HSM) for private keys in production
- Rotate keys regularly (recommended: yearly)
- Use separate keys for signing vs encryption
- Store public keys in accessible key servers
- Use JWK (JSON Web Key) format for key distribution

**DON'T**:
- Hardcode keys in source code
- Share private keys between users/systems
- Use weak algorithms (e.g., RS256 with <2048 bit keys)
- Store unencrypted private keys in version control

### Algorithm Selection

**Recommended algorithms**:
- **Signing**: ES256 (ECDSA P-256), ES384, or ES512
- **Encryption**: RSA-OAEP with A256GCM or ECDH-ES+A256KW with A256GCM

**Why ES256 over RS256?**:
- Smaller keys (256-bit EC vs 2048-bit RSA)
- Faster signing and verification
- Better security per bit

### Signature Validation

Always validate:
1. Signature is cryptographically valid
2. Key ID (`kid`) matches expected signer
3. Issued-at (`iat`) timestamp is recent
4. Expiration (`exp`) hasn't passed
5. Algorithm (`alg`) is allowed

### Encryption Best Practices

- Use authenticated encryption (GCM mode)
- Never reuse IVs/nonces
- Encrypt content encryption key (CEK) per recipient
- Use forward secrecy (ephemeral keys)
- Consider hybrid encryption for multi-recipient scenarios

### Redaction Considerations

**Types of redaction**:
1. **Hash**: Verifiable but not recoverable without original
2. **Mask**: Shows structure but hides content
3. **Remove**: Complete deletion with placeholder

**When to use each**:
- **Hash**: When you need to prove content hasn't changed without revealing it
- **Mask**: When showing data exists but hiding specifics (e.g., "user has 5 todos")
- **Remove**: When compliance requires no trace of original

**Redaction attacks to prevent**:
- Length-based inference (mask or remove to prevent)
- Frequency analysis (don't use deterministic masking)
- Side-channel leaks (redact associated metadata)

## Privacy Compliance

### GDPR Compliance

**Article 6** (Lawfulness):
- Track legal basis for processing in `ConsentRecord.legalBasis`
- Common values: "consent", "contract", "legal_obligation", "legitimate_interest"

**Article 15** (Right to Access):
- Implement search across all vBRIEF documents
- Export user's data in machine-readable format
- Include metadata about data processing

**Article 17** (Right to Be Forgotten):
- Delete or redact user data on request
- Respect legal holds (`legalHold: true`)
- Log all deletions for audit

**Article 25** (Data Protection by Design):
- Default to minimal data collection (`containsPII: false`)
- Use encryption for sensitive data
- Implement access controls by default

### CCPA Compliance

**Right to Know**:
- Same as GDPR Article 15

**Right to Delete**:
- Same as GDPR Article 17

**Right to Opt-Out**:
- Track via `ConsentRecord.revocable: true`
- Respect `revokedAt` timestamp

### HIPAA Compliance

For healthcare-related vBRIEF documents:

**PHI Protection**:
- Always use encrypted mode for PHI
- Implement audit logging for all access
- Set `dataRetention` policies (HIPAA requires 6 years)

**Minimum Necessary Rule**:
- Use fine-grained access control
- Redact PHI when sharing with non-authorized users
- Document purpose in `ConsentRecord.purpose`

## Relationship to Existing Extensions

### Extension 1 (Timestamps)

Security extension uses timestamps for:
- Signature issuance and expiration
- Consent grant and revocation times
- Redaction timestamps
- Access audit trails

### Extension 2 (Identifiers)

Required for:
- Tracking entities in access control
- Identifying data subjects for GDPR
- Referencing keys (`kid` in JWS/JWE)
- Consent scope (which items/phases)

### Extension 6 (Participants)

Complements access control:
- Participants can have roles (reader, writer, admin)
- Participant identity used for access checks
- Consent tied to specific participants

### Extension 10 (Version Control)

Security events generate version control entries:
- Document signing
- Encryption/decryption
- Redactions
- Access control changes

### Extension 11 (Multi-Agent Forking)

Security in forked scenarios:
- Forks can have different access controls
- Signature chains track provenance
- Encrypted forks may use different keys

### Extension 12 (Playbooks)

Playbook security:
- Learnings can be classified
- Redact proprietary strategies
- Control sharing of institutional knowledge

## File Formats and MIME Types

### Unsigned

**TRON**: `.tron` / `application/vnd.vbrief+tron`  
**JSON**: `.json` / `application/vnd.vbrief+json`

### Signed (JWS)

**Compact**: `.jws` / `application/jose`  
**Full**: `.jws` / `application/jose+json`

### Encrypted (JWE)

**Compact**: `.jwe` / `application/jose`  
**Full**: `.jwe` / `application/jose+json`

### Signed + Encrypted

Nest JWE inside JWS or vice versa:

**Encrypt then Sign** (recommended):
```
sign(encrypt(vBRIEF))
```
- Provides authenticity and confidentiality
- Signature validates encrypted content
- File extension: `.jws` (outermost format)

**Sign then Encrypt**:
```
encrypt(sign(vBRIEF))
```
- Hides signature from intermediaries
- File extension: `.jwe` (outermost format)

## Open Questions

1. **Key Distribution**: Should vBRIEF define a key discovery mechanism or rely on external PKI?

2. **Selective Disclosure**: Should we support ZKP (zero-knowledge proofs) for proving properties without revealing data?

3. **Quantum Resistance**: When should we recommend post-quantum algorithms?

4. **Blockchain Integration**: Should redaction hashes be anchored in blockchain for tamper-evidence?

5. **Homomorphic Encryption**: Can we enable analysis on encrypted vBRIEF documents?

6. **Multi-Recipient Encryption**: Should we define a standard for encrypting once for multiple recipients (like JWE with multiple recipients)?

## Migration Path

### Phase 1: Unsigned (Current State)

All documents are unsigned. Focus on schema validation and data quality.

### Phase 2: Signed Documents

- Add JWS signing for important plans and decisions
- Implement signature verification in tools
- Establish key management practices

### Phase 3: Encrypted Documents

- Add JWE encryption for sensitive data
- Implement access control checks
- Deploy key management infrastructure

### Phase 4: Privacy Compliance

- Implement redaction mechanisms
- Add consent tracking
- Build GDPR/CCPA compliance tools

### Phase 5: Advanced Security

- Zero-knowledge proofs
- Post-quantum algorithms
- Homomorphic encryption

## Community Feedback

We're seeking feedback on:

1. **Algorithm choices**: Are ES256 and RSA-OAEP the right defaults?
2. **Key management**: Should vBRIEF define key distribution or use existing PKI?
3. **Redaction granularity**: Is field-level redaction sufficient or do we need finer control?
4. **Compliance scope**: Are GDPR, CCPA, HIPAA sufficient or should we add others?
5. **Performance**: How do signing/encryption impact large documents (e.g., 100+ item todo lists)?
6. **Multi-tenant**: How should security work in shared vBRIEF servers?

Please provide feedback via:
- GitHub issues: https://github.com/visionik/vBRIEF/issues
- GitHub discussions: https://github.com/visionik/vBRIEF/discussions
- Email: visionik@pobox.com

## References

### Standards
- **RFC 7515**: JSON Web Signature (JWS) - https://www.rfc-editor.org/rfc/rfc7515
- **RFC 7516**: JSON Web Encryption (JWE) - https://www.rfc-editor.org/rfc/rfc7516
- **RFC 7517**: JSON Web Key (JWK) - https://www.rfc-editor.org/rfc/rfc7517
- **RFC 7518**: JSON Web Algorithms (JWA) - https://www.rfc-editor.org/rfc/rfc7518
- **RFC 7519**: JSON Web Token (JWT) - https://www.rfc-editor.org/rfc/rfc7519

### Related Standards
- **vCon**: Virtualized Conversations - https://datatracker.ietf.org/wg/vcon/about/
- **vCard**: RFC 6350 - https://www.rfc-editor.org/rfc/rfc6350
- **iCalendar**: RFC 5545 - https://www.rfc-editor.org/rfc/rfc5545

### Privacy Regulations
- **GDPR**: EU General Data Protection Regulation - https://gdpr.eu/
- **CCPA**: California Consumer Privacy Act - https://oag.ca.gov/privacy/ccpa
- **HIPAA**: Health Insurance Portability and Accountability Act - https://www.hhs.gov/hipaa/

### vBRIEF
- **Core Specification**: README.md
- **Extension 1 (Timestamps)**: README.md#extension-1-timestamps
- **Extension 2 (Identifiers)**: README.md#extension-2-identifiers
- **Extension 6 (Participants)**: README.md#extension-6-participants--collaboration
- **Extension 10 (Version Control)**: README.md#extension-10-version-control--sync
- **Extension 12 (Playbooks)**: README.md#extension-12-playbooks

### Libraries
- **jose** (JavaScript): https://github.com/panva/jose
- **PyJWT** (Python): https://pyjwt.readthedocs.io/
- **go-jose** (Go): https://github.com/go-jose/go-jose

## Acknowledgments

This extension is inspired by the security model of vCon (Virtualized Conversations), an IETF working group standardizing conversation data containers. vCon's three-mode security approach (unsigned, signed, encrypted) provides a proven pattern for protecting structured data while maintaining interoperability.

Thank you to the vCon community for pioneering these security patterns in a similar domain.
