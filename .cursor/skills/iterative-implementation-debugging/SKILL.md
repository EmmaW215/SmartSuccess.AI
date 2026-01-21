---
name: iterative-implementation-debugging
description: Follows a systematic iterative workflow for implementing features and debugging errors. Includes error collection, root cause analysis, fix implementation, verification loops, and regression prevention. Use when implementing code changes, fixing errors, debugging issues, or when the user requests iterative development with error resolution.
---

# Iterative Implementation and Debugging Workflow

## Overview

This workflow ensures complete error resolution through systematic iteration, with emphasis on backward compatibility and existing functionality preservation.

## Phase 1: Initial Implementation

1. Execute the requested implementation
2. Monitor execution for completion
3. Capture all output, warnings, and error messages

## Phase 2: Error Assessment

**Automatic Error Collection:**
- Collect all error logs, stack traces, and warning messages
- Document affected files and line numbers
- Identify error types (syntax, runtime, dependency, configuration, etc.)

**If Error Information is Incomplete:**
- Explicitly request complete error details from the user:
  - Full error messages
  - Stack traces
  - Console output
  - Browser developer tools logs (if applicable)
  - Build/compilation errors

## Phase 3: Error Resolution

**Root Cause Analysis:**
- Analyze each error systematically
- Determine dependencies between errors
- Prioritize fixes based on error hierarchy

**Fix Implementation:**
- Apply corrections to identified issues
- Ensure fixes target root causes, not symptoms
- Document changes made for each fix

## Phase 4: Verification and Re-execution

**Automated Re-run:**
- Automatically re-execute the implementation after applying fixes
- Monitor for new or recurring errors
- Compare results with previous iteration

**Iteration Loop:**
- Repeat Phases 2-4 until ALL of the following criteria are met:
  - Zero compilation/build errors
  - Zero runtime errors
  - All features function as intended
  - Application runs smoothly without warnings (or acceptable warnings are documented)

## Phase 5: Regression Prevention

**Critical Requirement: Backward Compatibility**

Before finalizing any implementation, verify:

✅ **Existing Functionality Preservation:**
- All pre-existing features continue to work without modification
- No breaking changes to existing APIs or interfaces
- User workflows remain unaffected
- Data structures maintain compatibility

✅ **Non-Impact Verification:**
- Run existing test cases (if available)
- Manually verify core user flows
- Check that unchanged files still function correctly
- Ensure no unintended side effects

✅ **Isolation of Changes:**
- New code is properly encapsulated
- Modifications are scoped to affected components only
- Shared dependencies are handled gracefully
- Configuration changes are additive, not destructive

**If Conflicts Arise:**
- Implement changes in a way that extends rather than replaces
- Use feature flags or conditional logic when necessary
- Provide migration paths for breaking changes
- Document any unavoidable impacts with clear justification

## Termination Conditions

The implementation is considered **COMPLETE** when:

1. ✅ All errors are resolved
2. ✅ Application executes successfully
3. ✅ All new features work as specified
4. ✅ No existing functionality is broken
5. ✅ Performance is acceptable
6. ✅ Code quality standards are met

## Communication Protocol

**During Iteration:**
- Report each error discovered
- Explain the fix being applied
- Confirm successful resolution before moving to next issue

**Upon Completion:**
- Provide summary of all issues encountered and resolved
- List all files created or modified
- Confirm preservation of existing functionality
- Highlight any important notes or considerations

**If Unable to Resolve:**
- Clearly state the blocking issue
- Provide diagnostic information
- Suggest alternative approaches or request additional input
