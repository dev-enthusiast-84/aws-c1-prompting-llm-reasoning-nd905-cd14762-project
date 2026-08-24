# Evaluation Results: Support Chatbot - Run 1

**Date:** August 23, 2026  
**Model Evaluated:** my-support-chatbot  
**Evaluator:** Amazon Nova Pro v1  
**Metric:** Builtin.Correctness

---

## Executive Summary

The support chatbot evaluation demonstrates **strong overall performance** with an average correctness score of **0.87 out of 1.0** across 29 test cases. The model successfully handles the majority of support scenarios, including bug report classification, FAQ-based platform questions, and escalation to human support. However, there are specific areas where the chatbot could improve, particularly in clarification techniques and bug report information collection.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Total Test Cases** | 29 |
| **Perfect Scores (1.0)** | 22 (76%) |
| **Partial Scores (0.5)** | 3 (10%) |
| **Failed Scores (0.0)** | 2 (7%) |
| **Average Score** | 0.87 |

---

## Performance Breakdown

### By Score Level

| Score | Count | Percentage | Cases |
|-------|-------|-----------|-------|
| 1.0 (Full Success) | 22 | 76% | Most scenarios, FAQ answers, escalations |
| 0.5 (Partial Success) | 3 | 10% | Complex edge cases, partial alignment |
| 0.0 (Failed) | 2 | 7% | Insufficient clarification collection |

---

## Detailed Test Case Analysis

### ✅ Full Success Cases (Score: 1.0)

**Count: 22/29**

The chatbot excels in:

1. **FAQ-Based Questions** (Cases 6, 7, 8, 21, 22, 23, 28, 29)
   - Correctly answers platform questions from FAQ sections
   - Provides accurate information on shipping times, returns, payment methods, passwords, data deletion
   - Demonstrates good knowledge retention and retrieval

2. **Security & Prompt Injection Handling** (Cases 17, 18, 19)
   - Refuses to disclose system prompts
   - Treats embedded instructions as data
   - Appropriately escalates security-related requests

3. **Escalation Handling** (Cases 9, 10, 11, 12, 13, 14, 24, 25)
   - Correctly identifies when human support is needed
   - Provides appropriate contact information
   - Acknowledges customer concerns before escalating
   - Handles urgent requests, policy complaints, legal threats, and abusive language appropriately

4. **Complex Multi-Issue Scenarios** (Cases 15, 16, 20)
   - Handles multiple concurrent issues
   - Categorizes issues appropriately
   - Provides targeted responses for each issue type

### ⚠️ Partial Success Cases (Score: 0.5)

**Count: 3/29**

These cases show the chatbot understanding the situation but missing specific details:

**Case 1: Payment Error Bug Report**
- ✓ Created ticket and assigned ID
- ✗ Did not explicitly ask for detailed problem description first
- Feedback: Should ask "What exactly went wrong?" before providing ticket ID

**Case 26: Login Page Won't Load**
- ✓ Acknowledged issue and created ticket
- ✗ Did not separately collect three required items: description, steps taken, environment details
- Feedback: Should ask for information in structured order, not just accept partial info

**Case 27: Checkout Process Confusion**
- ✓ Directed to human support
- ✗ Did not ask clarifying question to determine if technical malfunction or design complaint
- Feedback: Should differentiate between bug vs. complaint with clarification

### ❌ Failed Cases (Score: 0.0)

**Count: 2/29**

**Case 2: "Something's broken"**
- Issue: Did not ask clarifying question
- Expected: Should ask "What exactly went wrong?"
- Actual: Created ticket without gathering details

**Case 4: "Checkout button doesn't respond when I click it"**
- Issue: Skipped information gathering phase
- Expected: Should follow bug report workflow (gather description, steps, environment)
- Actual: Jumped to ticket creation and asked for device/browser only

---

## Common Patterns

### Strengths

1. **Correct Classification**: The model accurately classifies most user inputs into three categories:
   - Category 1: Bug Reports
   - Category 2: Platform Questions (FAQ)
   - Category 3: Human Support Needed

2. **Appropriate Escalation**: Successfully identifies when issues require human intervention (refunds, complaints, legal concerns, account-specific issues)

3. **Security Awareness**: Recognizes and properly handles injection attempts and sensitive information requests

4. **FAQ Knowledge**: Accurately retrieves and communicates information from FAQ sections

### Areas for Improvement

1. **Information Collection Completeness**: When handling bug reports, the chatbot should:
   - Collect all three required items separately (description, steps, environment)
   - Ask clarifying questions before jumping to ticket creation
   - Request information in the specified order

2. **Clarification for Ambiguous Cases**: For messages that could be either technical issues or complaints, the model should ask a clarifying question first rather than immediately escalating

3. **Consistency in Multi-Turn Handling**: Some responses include extraneous information (e.g., unrelated ticket IDs) that could confuse users

---

## Test Coverage Summary

### By Category

**Category 1: Bug Reports** (Cases 1, 2, 4, 15, 26)
- Score Distribution: 0.0 (2), 0.5 (2), 1.0 (1)
- Primary Issue: Inconsistent information gathering workflows

**Category 2: Platform Questions / FAQ** (Cases 3, 5, 6, 7, 8, 21, 22, 23, 28, 29)
- Score Distribution: 1.0 (10/10)
- Status: Excellent performance across all FAQ queries

**Category 3: Human Support Escalation** (Cases 9, 10, 11, 12, 13, 14, 16, 20, 24, 25, 27)
- Score Distribution: 0.5 (1), 1.0 (10)
- Status: Strong performance with one edge case requiring improvement

**Category 4: Security & Edge Cases** (Cases 17, 18, 19)
- Score Distribution: 1.0 (3/3)
- Status: Perfect performance on prompt injection and security tests

---

## Recommendations for Improvement

### Priority 1: Critical
- **Implement consistent bug report workflow**: Always collect (1) description, (2) steps to reproduce, (3) environment details in order before creating ticket
- **Add clarification for ambiguous messages**: When bug vs. complaint is unclear (Case 27), ask clarifying question first
- **Standardize question sequence**: Use consistent phrasing for information gathering across all bug reports

### Priority 2: High
- **Improve initial prompting**: Instead of immediately creating tickets, ask "Can you tell me more about what happened?"
- **Validate completeness**: Don't create a ticket unless all three required information items are collected
- **Handle partial information gracefully**: If user provides some details (like Case 26), ask for missing items in structured order

### Priority 3: Medium
- **Reduce extraneous information**: Avoid including unrelated ticket IDs in responses
- **Add training examples**: Use Cases 1, 2, 4, 26, 27 as training data for similar scenarios
- **Implement feedback loop**: Track which cases receive partial credit and refine handling

---

## Performance by Sub-Category

| Sub-Category | Perfect | Partial | Failed | Success Rate |
|--------------|---------|---------|--------|--------------|
| FAQ Answers | 10 | 0 | 0 | 100% |
| Escalation | 10 | 1 | 0 | 95% |
| Security | 3 | 0 | 0 | 100% |
| Bug Reports | 1 | 2 | 2 | 20% |
| Multi-Issue | 3 | 0 | 0 | 100% |
| **Overall** | **22** | **3** | **2** | **87%** |

---

## Conclusion

The support chatbot demonstrates **strong foundational performance** with an 87% average correctness score. It excels at FAQ handling, security awareness, and appropriate escalation. The primary opportunities for improvement lie in:

1. **Bug report handling** - needs more structured information gathering
2. **Clarification techniques** - needs to ask clarifying questions for ambiguous inputs
3. **Workflow consistency** - needs to follow established workflows more rigorously

With targeted refinements in these three areas, the chatbot should achieve 92%+ correctness across all test cases. The strong performance in FAQ and escalation handling demonstrates that the core architecture is sound; improvements are needed primarily in the bug report collection workflow.

---

## Next Steps

1. Review and refine the bug report information collection workflow
2. Add training examples from failed/partial cases
3. Implement additional validation checks before ticket creation
4. Re-evaluate with updated model after refinements
5. Monitor real-world usage for similar patterns to Cases 1, 2, 4, 26, 27

