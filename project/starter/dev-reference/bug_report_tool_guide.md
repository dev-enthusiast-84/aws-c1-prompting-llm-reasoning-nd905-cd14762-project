# Bug Report Tool Reference

**Tool Integration Details**

## create_bug_report Tool Parameters

| Parameter | Source | Example |
|-----------|--------|---------|
| description | "What went wrong?" answer | "Button doesn't respond" |
| stepsToReproduce | "What were you doing?" answer | "Had 3 items, clicked checkout" |
| environment | "What device/browser?" answer | "Chrome on Windows 10" |

## Multi-Turn Collection Flow

```
Turn 1: Customer: "Button broken"
        Bot: "What exactly went wrong?"
        
Turn 2: Customer: "Doesn't respond"
        Bot: "What were you doing?"
        
Turn 3: Customer: "Clicked checkout"
        Bot: "What device/browser?"
        
Turn 4: Customer: "Chrome on Windows"
        Bot: "Ticket #123 created. Engineers investigating."
```

## Common Scenarios

**Scenario 1:** Customer provides 2 of 3 upfront
- Acknowledge what you have
- Ask for the missing item
- Then create ticket

**Scenario 2:** Customer vague
- Ask clarifying question first
- Get more specific answer
- Then proceed with other items

**Scenario 3:** Tool fails
- Apologize
- Provide email fallback: bugs@company.com
- Recap the 3 items they provided
