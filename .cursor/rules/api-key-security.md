# API Key Security Guidelines

**CRITICAL: Never expose API keys in client-side code or documentation.**

## Prohibited Practices

❌ Never hardcode API keys in:
- Markdown files (.md)
- README files
- Configuration files committed to version control
- Client-side JavaScript/TypeScript code
- HTML files
- Any files exposed to the browser

## Required Practices

✅ Always use secure methods:
- Environment variables (.env files)
- Secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
- Server-side environment configuration
- CI/CD pipeline secrets

## Key Principles

1. **Server-Side Only**: API keys must only exist in server-side code, never exposed to the browser or client
2. **Version Control**: Add `.env` to `.gitignore` to prevent accidental commits
3. **Access Control**: Implement proper backend APIs that proxy requests to services requiring API keys
4. **Separation**: Keep API keys completely separate from any publicly accessible code or documentation

## Code Review Checklist

When working with API keys, verify:
- [ ] API keys are only used in server-side code
- [ ] `.env` is in `.gitignore`
- [ ] No API keys in client-side JavaScript/TypeScript
- [ ] No API keys in markdown files or documentation
- [ ] Backend APIs proxy requests instead of exposing keys
- [ ] Environment variables are used instead of hardcoded values

## Examples

**✅ Correct:**
```python
# Backend only
api_key = os.getenv("API_KEY")
```

**❌ Incorrect:**
```javascript
// Client-side - NEVER DO THIS
const apiKey = "sk-1234567890abcdef";
```
