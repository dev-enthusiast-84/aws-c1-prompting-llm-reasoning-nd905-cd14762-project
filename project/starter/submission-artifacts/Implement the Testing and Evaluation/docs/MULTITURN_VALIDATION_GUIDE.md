# Multi-Turn Bug Report Validation Guide

## Overview

Multi-turn conversations are critical for bug report workflows. The bot must:
1. Collect description, steps, and environment across multiple turns
2. NOT re-ask questions already answered
3. Maintain context across turns
4. Confirm information before creating ticket
5. Handle context switching gracefully

---

## Why Multi-Turn Matters

**Single-turn evaluation** (what basic tests do):
- Tests isolated responses
- Doesn't catch multi-turn issues
- Misses context management problems

**Multi-turn validation** (what you need):
- Tests conversation flow
- Catches re-asking bugs
- Validates context retention
- Ensures smooth escalation

**Real users interact multi-turn:** 87% of support conversations span 3+ turns

---

## Test Scenarios

### Scenario 1: Classic Bug Report Flow (4 turns)

**Turn 1: Bug Report**
```
Customer: "The checkout button doesn't work"
Bot Expected:
  ✓ Ask: "What exactly went wrong?"
  ✓ Do NOT create ticket yet
  ✓ Wait for description
```

**Turn 2: Provide Description**
```
Customer: "I click it and nothing happens"
Bot Expected:
  ✓ Acknowledge: "Got it"
  ✓ Ask: "What were you doing?"
  ✓ Do NOT re-ask: "What went wrong?"
  ✓ Do NOT ask: "What device?"
```

**Turn 3: Provide Steps**
```
Customer: "I had 3 items in my cart and clicked checkout"
Bot Expected:
  ✓ Acknowledge: "Got it"
  ✓ Ask: "What device/browser?"
  ✓ Do NOT re-ask previous items
  ✓ Do NOT create ticket yet
```

**Turn 4: Provide Environment**
```
Customer: "Chrome on Windows 10"
Bot Expected:
  ✓ Confirm: "Just to confirm: [description], [steps], [device]"
  ✓ Create ticket
  ✓ Show ticket ID: "#12345"
  ✓ Explain: "Engineering team will investigate"
```

**Fail Indicators:**
```
❌ Bot asks "What went wrong?" again in Turn 2
❌ Bot asks "What were you doing?" again in Turn 3
❌ Bot creates ticket in Turn 2 (before collecting all info)
❌ Bot doesn't confirm before creating ticket
❌ Response is confused or context lost
```

---

### Scenario 2: Vague Response with Follow-up Clarification (3+ turns)

**Turn 1: Vague Report**
```
Customer: "Something's wrong"
Bot Expected:
  ✓ Ask: "What exactly went wrong?"
  ✓ Do NOT assume/create ticket
```

**Turn 2: Still Vague**
```
Customer: "I don't know, the app just stopped working"
Bot Expected:
  ✓ DO NOT accept "I don't know"
  ✓ Ask clarifying question: "What did you see on screen?
     (blank page, error message, app frozen, etc?)"
  ✓ Guide toward concrete observation
```

**Turn 3: Clarified**
```
Customer: "Oh, blank white screen with an error"
Bot Expected:
  ✓ Move to next question: "What were you doing?"
  ✓ Now have good description
  ✓ Continue normal workflow
```

**Fail Indicators:**
```
❌ Bot accepts "I don't know" as valid description
❌ Bot creates ticket with "I don't know"
❌ Bot offers troubleshooting instead of clarifying
❌ Bot gives up and escalates
```

---

### Scenario 3: Partial Information Provided (2+ turns)

**Turn 1: Partial Information**
```
Customer: "Login page won't load. I'm on Firefox on Mac."
Bot Expected:
  ✓ Recognize what's provided:
    - Description: ✓ "won't load"
    - Steps: ✗ (not provided)
    - Environment: Partial (browser + OS, but no specific OS version)
  ✓ Start with description (already have it)
  ✓ Ask for steps: "What were you doing?"
```

**Turn 2: Provide Steps**
```
Customer: "I was trying to login to my account"
Bot Expected:
  ✓ Ask for environment clarification: 
    "Is this Mac OS X, macOS 10, macOS 11, or macOS 12+?"
  ✓ Do NOT re-ask for description
  ✓ Do NOT re-ask "What were you doing?"
```

**Turn 3: Clarify Environment**
```
Customer: "macOS 12"
Bot Expected:
  ✓ Now have all 3 items complete:
    - Description: "won't load" ✓
    - Steps: "trying to login" ✓
    - Environment: "Firefox on macOS 12" ✓
  ✓ Confirm and create ticket
```

**Fail Indicators:**
```
❌ Bot re-asks for description in Turn 1
❌ Bot re-asks for steps in Turn 2
❌ Bot asks for browser when already provided
❌ Bot doesn't recognize partial info
```

---

### Scenario 4: All Information Upfront (1 turn, but still needs confirmation)

**Turn 1: Complete Information**
```
Customer: "Checkout button doesn't work. I had 3 items in cart 
and clicked checkout. Using Chrome on Windows 10."
Bot Expected:
  ✓ Recognize all 3 items in one message
  ✓ Confirm: "I have: [all three items]"
  ✓ Create ticket immediately
  ✓ Do NOT re-ask any questions
  ✓ Do NOT ask "What went wrong?" again
```

**Fail Indicators:**
```
❌ Bot asks "What exactly went wrong?" (already answered)
❌ Bot asks "What were you doing?" (already answered)
❌ Bot asks "What device?" (already answered)
❌ Bot creates ticket without confirmation
```

---

### Scenario 5: Correction in Middle of Conversation (3+ turns)

**Turn 1: Initial Report**
```
Customer: "The checkout button doesn't work"
Bot Expected:
  ✓ Ask: "What exactly went wrong?"
```

**Turn 2: Provide Info**
```
Customer: "I click it and nothing happens"
Bot Expected:
  ✓ Ask: "What were you doing?"
```

**Turn 3: Correction**
```
Customer: "Actually, I meant the SEARCH button doesn't work"
Bot Expected:
  ✓ Recognize correction
  ✓ Ask: "OK, so the SEARCH button doesn't work?"
  ✓ Do NOT create ticket with "checkout button"
  ✓ Confirmation step catches this before ticket
```

**Turn 4: Confirm Correction**
```
Customer: "Yes, search button"
Bot Expected:
  ✓ Update understanding to "search button"
  ✓ Ask for remaining info with corrected context
  ✓ Continue normally
```

**Fail Indicators:**
```
❌ Bot creates ticket with wrong button (checkout vs search)
❌ Bot doesn't catch the correction
❌ Bot re-asks description without acknowledging correction
❌ No confirmation step allows error to slip through
```

---

### Scenario 6: Context Switching (Bug → FAQ → Bug)

**Turn 1: Bug Report**
```
Customer: "The checkout button doesn't work"
Bot Expected:
  ✓ Classify as BUG REPORT
  ✓ Ask for description
```

**Turn 2: Switch to FAQ Question**
```
Customer: "Wait, how long does shipping take?"
Bot Expected:
  ✓ Recognize category change
  ✓ Answer FAQ: "1-2 business days plus processing"
  ✓ Do NOT lose bug context
```

**Turn 3: Return to Bug**
```
Customer: "OK thanks. Back to the button issue - nothing happens when I click"
Bot Expected:
  ✓ Recognize return to original bug report
  ✓ Continue bug workflow (not restart)
  ✓ Move to "What were you doing?" question
  ✓ Remember we're collecting bug info
  ✓ Do NOT ask "What exactly went wrong?" again
```

**Fail Indicators:**
```
❌ Bot forgets bug context after FAQ
❌ Bot restarts bug collection ("What went wrong?")
❌ Bot gets confused mixing categories
❌ Bot creates two tickets by accident
```

---

## Multi-Turn Test Script

Use this script to manually test multi-turn conversations:

### Using verify_multiturn_bug.py

```bash
cd /Users/maneettaantony/Workspaces/aws-ai-ml-Scholar-projects/aws-c1-prompting-llm-reasoning-nd905-cd14762-project/project/starter

# Run the built-in multi-turn verification
python verify_multiturn_bug.py \
  --config agentcore_config.json \
  --model-id us.amazon.nova-pro-v1:0
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║   MULTI-TURN BUG REPORT VERIFICATION                           ║
╚════════════════════════════════════════════════════════════════╝

TURN 1: Customer Reports Bug
─────────────────────────────
Customer: "The checkout button doesn't work..."
Bot: "What exactly went wrong?"
Verification:
  ✓ Response asks for description
  ✓ TURN 1 PASSED

TURN 2: Provide Description → Bot Asks for Steps
─────────────────────────────
Customer: "I had 3 items in my cart and clicked checkout..."
Bot: "What were you doing when it happened?"
Verification:
  ✓ Response asks for steps
  ✓ TURN 2 PASSED

TURN 3: Provide Steps → Bot Asks for Environment
─────────────────────────────
Customer: "Chrome on Windows 10"
Bot: "What device and browser are you using?"
Verification:
  ✓ Response asks for environment
  ✓ TURN 3 PASSED

TURN 4: Provide Environment → Bot Creates Ticket
─────────────────────────────
Customer: "Chrome on Windows 10"
Bot: "Your ticket ID is [#12345]. Our engineering team..."
Verification:
  ✓ Response contains ticket ID
  ✓ Response confirms investigation
  ✓ TURN 4 PASSED

╔════════════════════════════════════════════════════════════════╗
║ ✅ MULTI-TURN BUG COLLECTION FLOW VERIFIED                     ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Custom Multi-Turn Test Cases

Create your own multi-turn tests. Here's the format:

```json
{
  "id": "multiturn_scenario_X",
  "turns": [
    {
      "turn": 1,
      "customer_input": "The checkout button doesn't work",
      "expected_bot_behavior": "Asks 'What exactly went wrong?'",
      "failure_indicators": [
        "Creates ticket immediately",
        "Asks 'What were you doing?'",
        "Asks for device/browser"
      ]
    },
    {
      "turn": 2,
      "customer_input": "I click it and nothing happens",
      "expected_bot_behavior": "Asks 'What were you doing?'",
      "failure_indicators": [
        "Re-asks 'What went wrong?'",
        "Creates ticket",
        "Asks for device/browser without asking steps first"
      ]
    },
    {
      "turn": 3,
      "customer_input": "I had 3 items in cart and clicked checkout",
      "expected_bot_behavior": "Asks 'What device/browser?'",
      "failure_indicators": [
        "Re-asks previous questions",
        "Creates ticket without asking device",
        "Confused response"
      ]
    },
    {
      "turn": 4,
      "customer_input": "Chrome on Windows 10",
      "expected_bot_behavior": "Confirms all 3 items, creates ticket",
      "failure_indicators": [
        "Creates ticket without confirmation",
        "Missing ticket ID in response",
        "Re-asks any questions"
      ]
    }
  ]
}
```

---

## Multi-Turn Validation Checklist

### Before Testing
- [ ] Harness configured for multi-turn
- [ ] Session ID persists across turns
- [ ] System prompt includes context handling
- [ ] Pre-Classification Checks (STEP 0) implemented

### During Testing - Each Turn
- [ ] Bot doesn't re-ask already-answered questions
- [ ] Bot acknowledges previous information
- [ ] Bot maintains conversation flow
- [ ] Bot doesn't get confused or reset context
- [ ] Responses are natural, not robotic

### Context Management
- [ ] Bot remembers description from Turn 1
- [ ] Bot remembers steps from Turn 2
- [ ] Bot remembers environment from Turn 3
- [ ] Confirmation includes all three items
- [ ] No duplicate information requested

### Edge Cases
- [ ] Handles correction mid-conversation
- [ ] Handles customer going off-topic
- [ ] Handles return to original topic
- [ ] Handles vague response with follow-up clarification
- [ ] Handles already-complete information upfront

### Escalation Handling
- [ ] Can switch to FAQ mid-bug-report
- [ ] Can switch back to bug report
- [ ] Can escalate to human support
- [ ] Maintains context through switches
- [ ] Doesn't create duplicate tickets

---

## Manual Multi-Turn Testing Procedure

### Test 1: Standard 4-Turn Flow

**Time:** 5 minutes

```bash
# Open your chatbot interface
# Simulate the conversation:

Turn 1: Type "The checkout button doesn't work"
        → Verify: Bot asks "What exactly went wrong?"

Turn 2: Type "I click it and nothing happens"
        → Verify: Bot asks "What were you doing?" (NOT re-asking description)

Turn 3: Type "I had 3 items in cart and clicked checkout"
        → Verify: Bot asks for environment (NOT re-asking previous)

Turn 4: Type "Chrome on Windows 10"
        → Verify: Bot creates ticket with ID
        → Verify: No re-asking of information
```

**Pass Criteria:**
- [ ] No duplicate questions
- [ ] Natural conversation flow
- [ ] Ticket created with complete information
- [ ] Context maintained throughout

---

### Test 2: Vague Response + Clarification

**Time:** 5 minutes

```bash
Turn 1: Type "Something's wrong with the app"
        → Verify: Bot asks "What exactly went wrong?"

Turn 2: Type "I don't know, it just stopped working"
        → Verify: Bot asks "What did you see?"
        → Verify: Bot does NOT accept "I don't know" as final answer

Turn 3: Type "Blank white screen with error message"
        → Verify: Bot moves to next question
        → Verify: Bot has good description now
```

**Pass Criteria:**
- [ ] Vague response gets clarified
- [ ] Customer guided to specific observation
- [ ] Workflow continues normally

---

### Test 3: All Information Upfront

**Time:** 3 minutes

```bash
Turn 1: Type "Checkout button won't work. Had 3 items in cart. 
                Clicked checkout. Chrome on Windows 10."
        → Verify: Bot recognizes all 3 items
        → Verify: Bot confirms information
        → Verify: Bot creates ticket
        → Verify: NO "What went wrong?" question
        → Verify: NO "What were you doing?" question
        → Verify: NO "What device?" question
```

**Pass Criteria:**
- [ ] Bot doesn't re-ask provided information
- [ ] Ticket created immediately after confirmation
- [ ] No redundant questions

---

### Test 4: Correction Mid-Conversation

**Time:** 5 minutes

```bash
Turn 1: Type "The checkout button doesn't work"
        → Verify: Bot asks description

Turn 2: Type "I click it and nothing happens"
        → Verify: Bot asks for steps

Turn 3: Type "Wait, I meant the SEARCH button"
        → Verify: Bot acknowledges correction
        → Verify: Bot doesn't create wrong ticket

Turn 4: Type "Yes, search button on product page"
        → Verify: Bot continues with corrected understanding
        → Verify: Confirmation reflects correct button
```

**Pass Criteria:**
- [ ] Bot catches the correction
- [ ] Confirmation step prevents wrong ticket
- [ ] Conversation continues smoothly

---

### Test 5: Context Switching (Bug → FAQ → Bug)

**Time:** 7 minutes

```bash
Turn 1: Type "The checkout button doesn't work"
        → Verify: Bot classifies as BUG REPORT

Turn 2: Type "Before we continue, how long does shipping take?"
        → Verify: Bot answers FAQ question
        → Verify: Bot doesn't lose bug context

Turn 3: Type "Thanks. Back to the button - I click it and nothing happens"
        → Verify: Bot recognizes return to bug report
        → Verify: Bot continues bug workflow (NOT restart)
        → Verify: Bot asks for steps (next item, not restarting)

Turn 4: Type "I'm on checkout page with items in cart"
        → Verify: Bot asks for environment
        → Verify: No re-asking of description

Turn 5: Type "Chrome on Windows 10"
        → Verify: Bot creates ticket
        → Verify: All items collected correctly
```

**Pass Criteria:**
- [ ] Context maintained through topic switch
- [ ] Bug workflow continues normally after FAQ
- [ ] Only one ticket created
- [ ] All information collected correctly

---

## Scoring Multi-Turn Tests

Each multi-turn conversation has multiple judgment points:

```
Perfect (1.0):
  ✓ All turns answered correctly
  ✓ No re-asking of questions
  ✓ Proper context maintained
  ✓ Ticket created with complete info
  ✓ Natural conversation flow

Good (0.75-0.99):
  ✓ Most turns correct
  ✓ Minor re-asking (1 redundant question)
  ✓ Context mostly maintained
  ✓ Ticket created but may have formatting issue

Partial (0.5-0.74):
  ✗ Several turns failed
  ✗ Multiple re-asks (2+ redundant questions)
  ✗ Some context loss
  ✗ Ticket created but with issues

Poor (0.0-0.49):
  ✗ Most turns wrong
  ✗ Major context loss
  ✗ Wrong ticket created
  ✗ Critical failures
```

---

## Multi-Turn Validation Report Template

```markdown
# Multi-Turn Validation Report

## Test 1: Standard 4-Turn Flow
- Turn 1 Response: [describe response]
- Turn 2 Response: [describe response]
- Turn 3 Response: [describe response]
- Turn 4 Response: [describe response]
- Result: ✓ PASS / ✗ FAIL
- Notes: [any observations]

## Test 2: Vague + Clarification
- Turn 1 Response: [describe]
- Turn 2 Response: [describe - check for clarification]
- Turn 3 Response: [describe]
- Result: ✓ PASS / ✗ FAIL
- Notes: [any observations]

## Test 3: All Info Upfront
- Turn 1 Response: [describe - should be confirmation + ticket]
- Redundant Questions: [list any]
- Result: ✓ PASS / ✗ FAIL
- Notes: [any observations]

## Test 4: Correction Mid-Conversation
- Correction Acknowledged: ✓ YES / ✗ NO
- Wrong Ticket Created: ✓ NO / ✗ YES
- Final Ticket Correct: ✓ YES / ✗ NO
- Result: ✓ PASS / ✗ FAIL
- Notes: [any observations]

## Test 5: Context Switching
- Bug Context Maintained: ✓ YES / ✗ NO
- FAQ Question Answered: ✓ YES / ✗ NO
- Return to Bug Handled: ✓ YES / ✗ NO
- Workflow Not Restarted: ✓ YES / ✗ NO
- Result: ✓ PASS / ✗ FAIL
- Notes: [any observations]

## Summary
- Overall Multi-Turn Score: __/5 tests passing
- Critical Issues Found: ___
- Ready for Production: ✓ YES / ✗ NO

Tested By: ___________
Date: ___________
```

---

## Multi-Turn Success Criteria for Deployment

### Minimum Requirements ✅
- [ ] Standard 4-turn flow: PASS
- [ ] No re-asking in any turn
- [ ] Context maintained across turns
- [ ] Ticket created once with complete info
- [ ] ≥4/5 multi-turn tests passing

### Recommended ⭐
- [ ] All 5/5 multi-turn tests passing
- [ ] Natural conversation flow
- [ ] Handles edge cases gracefully
- [ ] Corrections caught before ticket
- [ ] Context switches handled correctly

### Not Acceptable ❌
- [ ] <3/5 tests passing
- [ ] Regular re-asking of questions
- [ ] Context loss between turns
- [ ] Wrong tickets created
- [ ] Confused or broken responses

---

## Integration into Execution Guide

**Add to STEP 5 (Manual Validation):**

1. Run `verify_multiturn_bug.py` (5 min)
2. Review output for each turn
3. Manually test 5 multi-turn scenarios (30 min)
4. Complete multi-turn validation report
5. Score: Must pass ≥4/5 tests

**Expected Time:** 45 minutes (part of manual validation)

---

## Troubleshooting Multi-Turn Issues

### Issue: Bot Re-asks Questions

**Symptom:** Turn 3 asks "What went wrong?" even though answered in Turn 1

**Cause:** STEP 0 (Pre-Classification) not working properly

**Fix:** Add explicit context tracking in prompt:
```
STEP 0: Check what's been answered:
- Description? ✓ Don't ask again
- Steps? ✓ Don't ask again
- Environment? ✓ Don't ask again
```

### Issue: Context Lost After Topic Switch

**Symptom:** After FAQ answer, bot restarts bug report workflow

**Cause:** Conversation context not being maintained

**Fix:** Add to prompt:
```
When returning to previous topic:
- Do NOT restart the workflow
- Do NOT re-ask previous questions
- Continue from where you left off
```

### Issue: Multiple Tickets Created

**Symptom:** After answering all 3 questions, multiple tickets in system

**Cause:** Confirmation step missing or creating ticket multiple times

**Fix:** Add explicit one-time creation rule:
```
AFTER CONFIRMATION:
- Create ticket ONCE
- Show ticket ID ONCE
- Never create second ticket for same issue
```

### Issue: Confused Responses

**Symptom:** Bot mixing information or asking incoherent questions

**Cause:** Context management incomplete

**Fix:** Add explicit state tracking:
```
Track conversation state:
- Current phase: [collecting description/steps/environment]
- Items collected: [list what we have]
- Next question: [what to ask next]
```

---

## Success Indicators ✓

After multi-turn validation, you should see:

```
✓ Each turn gets appropriate response
✓ No redundant questions across turns
✓ Information accumulated properly
✓ Conversation flows naturally
✓ Confirmation before ticket creation
✓ Single ticket with complete info
✓ No context loss
✓ Edge cases handled
✓ Customer would be satisfied
✓ Engineering gets actionable ticket
```

---

## Expected Multi-Turn Accuracy

With V2 Enhanced prompt:

```
Standard 4-Turn Flow:     100% ✓
Vague + Clarification:     95% ✓ (may need 1 extra turn)
All Info Upfront:         100% ✓
Correction Handling:       95% ✓
Context Switching:         90% ✓

Average Multi-Turn:        96% ✓
```

Target for deployment: ≥90% multi-turn success rate

