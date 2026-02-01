---
description: Documentation generation workflow. README, API docs, code comments, architecture docs.
---

# /document - Documentation Workflow

Generate and update project documentation.

## Steps

### 1. Assess Documentation Needs
Ask the user:
- What needs documentation? (API, README, architecture)
- Who's the audience? (developers, users, ops)
- What format? (Markdown, JSDoc, OpenAPI)

### 2. README Generation

Standard README structure:
```markdown
# Project Name

Brief description (1-2 sentences)

## Features
- Key feature 1
- Key feature 2

## Quick Start
\`\`\`bash
npm install
npm start
\`\`\`

## Installation
Detailed installation steps

## Usage
Code examples

## Configuration
Environment variables, config files

## API Reference
Link to detailed docs

## Contributing
How to contribute

## License
License type
```

### 3. API Documentation

**REST API (OpenAPI/Swagger):**
```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
```

**Generate from code:**
```bash
# TypeScript/Express
npx tsoa spec-and-routes

# Python/FastAPI (automatic)
# Visit /docs or /redoc
```

### 4. Code Documentation

**JSDoc/TSDoc:**
```typescript
/**
 * Calculates the total price including tax
 * @param items - Array of cart items
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @returns Total price with tax
 * @example
 * calculateTotal([{price: 10}, {price: 20}], 0.08) // 32.40
 */
function calculateTotal(items: CartItem[], taxRate: number): number
```

**Python docstrings:**
```python
def calculate_total(items: list[CartItem], tax_rate: float) -> float:
    """
    Calculate the total price including tax.

    Args:
        items: List of cart items
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price with tax

    Example:
        >>> calculate_total([{'price': 10}, {'price': 20}], 0.08)
        32.40
    """
```

### 5. Architecture Documentation

**C4 Model Diagrams:**
- Context: System and external actors
- Container: High-level tech components
- Component: Internal structure
- Code: Class/function level (optional)

**Decision Records (ADR):**
```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Accepted

## Context
Need a database for production use.

## Decision
PostgreSQL for relational data.

## Consequences
- Strong ACID compliance
- Need PostgreSQL expertise
- More complex than SQLite for dev
```

### 6. Generate & Validate

```bash
# Generate TypeDoc
npx typedoc src/

# Generate Python docs
pdoc --html src/

# Validate links
npx markdown-link-check README.md
```

### 7. Maintain Documentation

Set up:
- Doc generation in CI
- Link checking
- Version-specific docs
- Changelog updates

## Documentation Checklist

- [ ] README is complete and current
- [ ] API endpoints documented
- [ ] Code has appropriate comments
- [ ] Architecture decisions recorded
- [ ] Setup instructions work
- [ ] Examples are runnable
- [ ] Links are valid
