# Information-Only vs Implementation Mode

## Information-Only Mode (No Implementation)

When user requests contain these patterns, respond with **explanations, guidance, or answers ONLY**. Do not execute code, create files, modify files, or push changes.

**Trigger Phrases:**
- "Please let me know..."
- "Please tell me..."
- "Please help me understand..."
- "Please explain..."
- "Please read [files/data] and let me know..."
- "Please guide me on..."
- "Please answer my question..."
- "What is...?"
- "How does...?"
- "Can you explain...?"

**Appropriate Responses:**
- Provide explanations and analysis
- Offer guidance and recommendations
- Answer questions with detailed information
- Review and summarize file contents
- Suggest approaches or solutions

**Prohibited Actions:**
- Creating or modifying files
- Executing code or commands
- Pushing changes to version control
- Installing packages or dependencies
- Any system-level modifications

**Scope:** Applies regardless of operational mode (including "Agent" mode).

---

## Implementation Mode (Active Development)

When user requests contain action-oriented language, proceed with implementation after confirmation if needed.

**Trigger Phrases:**
- "Please create..."
- "Please implement..."
- "Please build..."
- "Please push..."
- "Please add..."
- "Go ahead and..."
- "Start coding..."

**Protocol:**
1. Confirm scope of work if ambiguous
2. Proceed with implementation
3. Provide summary of changes made

---

## Clarification Protocol

When user intent is ambiguous, always ask:
"Would you like me to:
A) Explain/analyze this, or
B) Implement the changes?"

**Default Rule:** If unsure, ask before starting any action.
