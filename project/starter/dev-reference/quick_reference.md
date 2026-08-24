# Quick Reference Guide

**Quick lookup during testing and development**

## Routing Decision Tree

```
Customer message received
├─ Is it a technical malfunction? → BUG REPORT
├─ Is it a policy/order question? → PLATFORM QUESTION  
└─ Otherwise? → HUMAN SUPPORT
```

## Hallucination Prevention Responses

```
FAQ gap:
  "I don't have that specific information. Let me connect you with 
   our support team: 1-800-555-0199"

Account lookup:
  "I can't see your account directly. Our support team will look 
   that up for you at 1-800-555-0199"

Technical speculation:
  "I'll collect the details so our engineering team can investigate."
  [NO troubleshooting, just collect info]
```

## Bug Report Checklist (Ask in Order)

- [ ] Turn 1: "What exactly went wrong?"
- [ ] Turn 2: "What were you doing when it happened?"
- [ ] Turn 3: "What device/browser are you using?"
- [ ] THEN call tool (not before!)

## Escalation Triggers

Immediately escalate if:
- Fraud, security breach mentioned
- Payment/refund dispute
- Legal threats
- GDPR/data deletion requests
- Abusive language
- Policy exceptions needed

## Testing Checklist

- [ ] Bug reports collect 3 items in order
- [ ] Platform questions answer from FAQ only
- [ ] Human support redirects with phone number
- [ ] No troubleshooting offered
- [ ] No promises made
- [ ] No sensitive data requested
