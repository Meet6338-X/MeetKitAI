---
name: ai-prompt-engineering
description: AI prompt engineering patterns. System prompts, few-shot learning, chain-of-thought, structured outputs, agent design.
---

# AI Prompt Engineering Skill

Patterns for effective AI prompting and agent design.

## When to Use
- Designing system prompts
- Implementing RAG systems
- Building AI agents
- Optimizing model outputs
- Creating structured responses

## Core Patterns

### 1. System Prompt Structure

```markdown
# Role Definition
You are [specific role] with expertise in [domains].

# Core Capabilities
- [Capability 1]
- [Capability 2]

# Constraints
- [Constraint 1]
- [Constraint 2]

# Output Format
[Specify exact output format]

# Examples (if needed)
[Provide 1-3 examples]
```

### 2. Chain-of-Thought Prompting

```markdown
Solve this problem step by step:

1. First, identify the key components
2. Then, analyze each component
3. Next, determine relationships
4. Finally, synthesize the solution

Show your reasoning at each step.
```

### 3. Few-Shot Learning

```markdown
Here are examples of the task:

Input: "The movie was fantastic!"
Output: {"sentiment": "positive", "confidence": 0.95}

Input: "Terrible experience, waste of time"
Output: {"sentiment": "negative", "confidence": 0.92}

Input: "It was okay, nothing special"
Output: {"sentiment": "neutral", "confidence": 0.78}

Now analyze this:
Input: "[user input]"
Output:
```

### 4. Structured Output

```markdown
Respond ONLY with valid JSON in this exact format:
{
  "summary": "string (max 100 chars)",
  "key_points": ["string", "string", "string"],
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": number (0-1)
}

Do not include any text outside the JSON object.
```

### 5. Role-Based Personas

```markdown
You are a senior software architect with 15 years of experience.
Your communication style is:
- Direct and concise
- Uses technical terminology appropriately
- Provides actionable recommendations
- Cites best practices and patterns

When reviewing code:
- Focus on architecture first
- Identify security concerns
- Suggest performance optimizations
- Recommend maintainability improvements
```

### 6. Task Decomposition

```markdown
Break down this complex task into subtasks:

Main Task: [description]

For each subtask:
1. Define clear inputs and outputs
2. Identify dependencies on other subtasks
3. Estimate complexity (1-5)
4. List required resources

Present as a numbered list with clear dependencies.
```

### 7. Guardrails & Safety

```markdown
Important constraints:
- Never generate harmful content
- Decline requests for personal information
- Acknowledge uncertainty with "I'm not sure"
- Cite sources when making factual claims
- Redirect off-topic requests politely

If a request violates these constraints, respond with:
"I can't help with that, but I can [alternative]."
```

### 8. Context Window Optimization

**Prioritization:**
1. System instructions (always first)
2. Most recent conversation (recency)
3. Relevant retrieved context (RAG)
4. Examples (few-shot)
5. Historical context (oldest first to trim)

**Compression Techniques:**
- Summarize older messages
- Remove redundant information
- Use concise formatting
- Prioritize actionable content

### 9. RAG Prompt Pattern

```markdown
Use the following context to answer the question.
If the context doesn't contain the answer, say "I don't have information about that."

Context:
---
{retrieved_documents}
---

Question: {user_question}

Answer based only on the provided context:
```

### 10. Agent ReAct Pattern

```markdown
You have access to these tools:
- search(query): Search the web
- calculate(expression): Evaluate math
- read_file(path): Read file contents

For each step:
1. Thought: What do I need to do?
2. Action: tool_name(arguments)
3. Observation: [tool output]
4. Repeat until complete

When you have the final answer:
Thought: I have gathered enough information
Final Answer: [your response]
```

### 11. Error Recovery

```markdown
If you encounter an error or invalid input:
1. Explain what went wrong clearly
2. Suggest how to fix the input
3. Provide an example of correct usage
4. Offer to help with a modified request

Never leave the user without a path forward.
```

### 12. Multi-Turn Context

```markdown
Conversation history:
- User asked about X
- You explained Y
- User clarified they meant Z

Current context: The user wants Z specifically.
Continue the conversation naturally, referencing prior context.
```

## Best Practices

| Practice | Why |
|----------|-----|
| Be specific | Reduces ambiguity |
| Use examples | Shows exact format |
| Set constraints | Prevents unwanted outputs |
| Define persona | Consistent voice |
| Structure output | Easier parsing |
| Handle errors | Better UX |

## Anti-Patterns

❌ Vague instructions ("be helpful")
❌ Too many constraints (overwhelms model)
❌ No output format (unpredictable)
❌ Contradictory rules
❌ Assuming context (be explicit)
