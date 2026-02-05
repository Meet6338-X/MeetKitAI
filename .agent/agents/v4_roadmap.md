# KARYA AGENT v4.0 Roadmap: "Autonomous Evolution"

> Taking the system from "Project Generator" to "Autonomous Software Engineer".

## 🚀 Proposed Improvements

### 1. 🐙 GitOps & Version Control Integration
**Goal**: Treat the generated project like a real software repository from second zero.
- [ ] Auto-initialize git repository (`git init`).
- [ ] Generate comprehensive `.gitignore` based on tech stack.
- [ ] **Atomic Commits**: Automatically commit after each phase:
  - "feat: Initial Project Structure"
  - "docs: Requirements and Proposal"
  - "arch: System Architecture Design"
  - "feat: Backend Implementation"
- [ ] Branch management (optional `develop` / `main` setup).

### 2. 🏥 Self-Healing & Auto-Repair (The "Fixer" Loop)
**Goal**: Ensure generated code is syntactically correct before the user sees it.
- [ ] **Syntax Validation**: Run python `compile()` or node `check` on generated files.
- [ ] **Auto-Fix Loop**: If syntax check fails, feed error back to LLM to regenerate the specific file.
- [ ] **Linter Integration**: Run `ruff` or `eslint` to fix formatting automatically.

### 3. 🎨 Real Asset Generation (Beyond Markdown)
**Goal**: Create professional assets that can be used directly in executive presentations.
- [ ] **Diagram Rendering**: Convert Mermaid text diagrams into actual `.png/.svg` files using `playwright` or `graphviz`.
- [ ] **Slide Generation**: Generate editable `.pptx` files using `python-pptx` instead of just markdown slides.
- [ ] **PDF Reports**: Compile the project report into a professional PDF.

### 4. 🧠 Persistent Context & Memory (RAG)
**Goal**: Handle larger projects by dynamically retrieving relevant context.
- [ ] **Vector Store**: Use a light local vector store (Chromadb/FAISS) to index requirements and architecture.
- [ ] **Context Retrieval**: When generating backend code, retrieve *only* relevant architecture modules, not the whole doc.

### 5. 🐳 Runtime Verification (The "Sandbox")
**Goal**: Verify the app actually *runs*.
- [ ] **Docker Test**: Attempt to build and run the generated `docker-compose.yml`.
- [ ] **Health Check**: Ping the API endpoints to verify they are up.
- [ ] **Report**: "Build Successful" or "Build Failed" in the final report.

---

## Recommended Next Steps (Phase 1 of v4)

I recommend we start with **GitOps** and **Self-Healing**, as these provide the highest immediate value for production reliability.
