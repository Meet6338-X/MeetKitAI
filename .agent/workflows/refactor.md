---
description: Systematic code refactoring workflow. Improves code quality, reduces technical debt.
---

# /refactor - Code Refactoring Workflow

Systematic approach to improving code quality without changing behavior.

// turbo-all

## Steps

### 1. Identify Scope
Ask the user:
- What code do you want to refactor? (file, function, module)
- What's the primary goal? (readability, performance, maintainability)
- Are there tests covering this code?

### 2. Analyze Current State
```bash
# Run static analysis
npx eslint src/ --ext .ts,.tsx
# or for Python
ruff check .
```

Review:
- Code complexity (cyclomatic, cognitive)
- Duplication
- Dependencies
- Test coverage

### 3. Plan Refactoring
Create refactoring plan with:
- Specific changes to make
- Order of operations (smallest to largest)
- Risk assessment for each change

Common refactoring patterns:
- Extract function/method
- Rename for clarity
- Remove duplication (DRY)
- Simplify conditionals
- Introduce patterns (strategy, factory)

### 4. Execute Incrementally
For each change:
1. Make ONE refactoring change
2. Run tests to verify behavior unchanged
3. Commit with descriptive message

```bash
git add .
git commit -m "refactor: extract validation logic to validateUser function"
```

### 5. Verify
```bash
# Run full test suite
npm test

# Check for regressions
npm run lint
npm run type-check
```

### 6. Document
Update comments/docs if function signatures changed.
Note breaking changes in CHANGELOG.

## Refactoring Checklist

- [ ] Tests pass before starting
- [ ] Each change is atomic and committed
- [ ] No behavior changes (unless intended)
- [ ] Code is more readable
- [ ] Reduced complexity
- [ ] Tests still pass after completion
