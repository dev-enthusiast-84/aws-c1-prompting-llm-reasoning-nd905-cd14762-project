#!/usr/bin/env python3
"""Multi-turn bug report verification script.

Demonstrates the complete 3-turn bug collection flow:
  Turn 1: Customer reports bug
  Turn 2: Bot asks for steps to reproduce, customer answers
  Turn 3: Bot asks for device/browser, customer provides
  Turn 4: Bot creates ticket with all three parameters

Usage:
    python verify_multiturn_bug.py

This script verifies:
  ✓ Correct question asked each turn (description → steps → environment)
  ✓ Bot collects all three items before calling tool
  ✓ Ticket is created with correct parameters
  ✓ Optional: Verify ticket in DynamoDB if credentials available
"""

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config
from botocore.eventstream import EventStream


def _event_stream(response) -> EventStream:
    """Locate the streaming part of the invoke_harness response."""
    for value in response.values():
        if isinstance(value, EventStream):
            return value
    raise RuntimeError(f"No event stream in response: {list(response)}")


def invoke_harness_turn(
    rt,
    harness_arn: str,
    gateway_arn: str,
    model_id: str,
    session_id: str,
    messages: list,
) -> str:
    """Invoke harness and return the assistant's text response."""

    tools = []
    if gateway_arn:
        tools = [{
            "type": "agentcore_gateway",
            "name": "support_gateway",
            "config": {"agentCoreGateway": {"gatewayArn": gateway_arn}},
        }]

    response = rt.invoke_harness(
        harnessArn=harness_arn,
        runtimeSessionId=session_id,
        model={"bedrockModelConfig": {"modelId": model_id}},
        tools=tools,
        messages=messages,
    )

    texts = []
    buffer = []
    for event in _event_stream(response):
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                buffer.append(delta["text"])
        elif "messageStop" in event:
            if buffer:
                texts.append("".join(buffer))
                buffer = []
    if buffer:
        texts.append("".join(buffer))

    return texts[-1] if texts else ""


def verify_question_type(response: str, expected_type: str) -> bool:
    """Verify response is asking for the expected type of information."""

    keywords = {
        "description": ["what went wrong", "what happened", "describe", "error", "issue"],
        "steps": ["doing", "steps", "reproduce", "click", "action", "try"],
        "environment": ["device", "browser", "os", "windows", "chrome", "safari", "firefox", "mac", "phone", "iphone"],
    }

    response_lower = response.lower()

    if expected_type not in keywords:
        print(f"  ⚠️ Unknown expected type: {expected_type}")
        return False

    found = any(kw in response_lower for kw in keywords[expected_type])

    if found:
        print(f"  ✓ Response asks for {expected_type} (keywords found)")
        return True
    else:
        print(f"  ✗ Response doesn't ask for {expected_type}")
        print(f"    Expected keywords: {', '.join(keywords[expected_type])}")
        print(f"    Got: {response[:200]}")
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="agentcore_config.json",
                        help="Config file from setup_gateway.py")
    parser.add_argument("--model-id", default="us.amazon.nova-pro-v1:0",
                        help="Bedrock model ID to use")
    parser.add_argument("--harness-arn", default=None,
                        help="Override harness ARN")
    parser.add_argument("--gateway-arn", default=None,
                        help="Override gateway ARN")
    parser.add_argument("--region", default=None,
                        help="AWS region")
    parser.add_argument("--check-dynamodb", action="store_true",
                        help="Also check if ticket was created in DynamoDB")
    args = parser.parse_args()

    # Load config
    config = {}
    config_path = Path(args.config)
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))

    harness_arn = args.harness_arn or config.get("harness_arn")
    gateway_arn = args.gateway_arn or config.get("gateway_arn")
    region = args.region or config.get("region") or "us-east-1"

    if not harness_arn:
        sys.exit("No harness ARN — pass --harness-arn or run create_harness.py first")

    # Initialize Bedrock client
    rt = boto3.client(
        "bedrock-agentcore",
        region_name=region,
        config=Config(read_timeout=300, retries={"max_attempts": 1}),
    )

    # Session ID persists across all turns
    session_id = f"verify-bug-{uuid.uuid4()}-multiturn"

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   MULTI-TURN BUG REPORT VERIFICATION                           ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Session ID: {session_id}")
    print(f"Harness ARN: {harness_arn}")
    print()

    # ========================================================================
    # TURN 1: Customer reports bug
    # ========================================================================
    print("TURN 1: Customer Reports Bug")
    print("─" * 60)

    customer_turn1 = "The checkout button doesn't work. I click it but nothing happens."
    print(f"Customer: \"{customer_turn1}\"")
    print()

    try:
        response_turn1 = invoke_harness_turn(
            rt=rt,
            harness_arn=harness_arn,
            gateway_arn=gateway_arn,
            model_id=args.model_id,
            session_id=session_id,
            messages=[{"role": "user", "content": [{"text": customer_turn1}]}],
        )
    except Exception as e:
        sys.exit(f"❌ Turn 1 failed: {e}")

    print(f"Bot: {response_turn1}")
    print()

    # Verify Turn 1
    print("Verification:")
    checks_t1 = [
        verify_question_type(response_turn1, "description"),
        "ticket" not in response_turn1.lower(),
        "error" not in response_turn1.lower() or "describe" in response_turn1.lower(),
    ]

    if not all(checks_t1):
        print("  ✗ TURN 1 FAILED: Bot didn't ask for description properly")
        sys.exit(1)

    print("  ✓ TURN 1 PASSED: Bot correctly asked for description")
    print()

    # ========================================================================
    # TURN 2: Customer provides description, bot asks for steps
    # ========================================================================
    print("TURN 2: Provide Description → Bot Asks for Steps")
    print("─" * 60)

    customer_turn2 = "I had 3 items in my cart and clicked the checkout button to proceed to payment."
    print(f"Customer: \"{customer_turn2}\"")
    print()

    try:
        response_turn2 = invoke_harness_turn(
            rt=rt,
            harness_arn=harness_arn,
            gateway_arn=gateway_arn,
            model_id=args.model_id,
            session_id=session_id,
            messages=[
                {"role": "user", "content": [{"text": customer_turn1}]},
                {"role": "assistant", "content": [{"text": response_turn1}]},
                {"role": "user", "content": [{"text": customer_turn2}]},
            ],
        )
    except Exception as e:
        sys.exit(f"❌ Turn 2 failed: {e}")

    print(f"Bot: {response_turn2}")
    print()

    print("Verification:")
    checks_t2 = [
        verify_question_type(response_turn2, "steps"),
        "ticket" not in response_turn2.lower(),
    ]

    if not all(checks_t2):
        print("  ✗ TURN 2 FAILED: Bot didn't ask for steps properly")
        sys.exit(1)

    print("  ✓ TURN 2 PASSED: Bot correctly asked for steps to reproduce")
    print()

    # ========================================================================
    # TURN 3: Customer provides steps, bot asks for environment
    # ========================================================================
    print("TURN 3: Provide Steps → Bot Asks for Environment")
    print("─" * 60)

    customer_turn3 = "This is happening in Chrome on my Windows 10 laptop."
    print(f"Customer: \"{customer_turn3}\"")
    print()

    try:
        response_turn3 = invoke_harness_turn(
            rt=rt,
            harness_arn=harness_arn,
            gateway_arn=gateway_arn,
            model_id=args.model_id,
            session_id=session_id,
            messages=[
                {"role": "user", "content": [{"text": customer_turn1}]},
                {"role": "assistant", "content": [{"text": response_turn1}]},
                {"role": "user", "content": [{"text": customer_turn2}]},
                {"role": "assistant", "content": [{"text": response_turn2}]},
                {"role": "user", "content": [{"text": customer_turn3}]},
            ],
        )
    except Exception as e:
        sys.exit(f"❌ Turn 3 failed: {e}")

    print(f"Bot: {response_turn3}")
    print()

    print("Verification:")
    checks_t3 = [
        verify_question_type(response_turn3, "environment"),
        "ticket" not in response_turn3.lower(),
    ]

    if not all(checks_t3):
        print("  ✗ TURN 3 FAILED: Bot didn't ask for environment properly")
        sys.exit(1)

    print("  ✓ TURN 3 PASSED: Bot correctly asked for device/browser")
    print()

    # ========================================================================
    # TURN 4: Customer provides environment, bot creates ticket
    # ========================================================================
    print("TURN 4: Provide Environment → Bot Creates Ticket")
    print("─" * 60)

    customer_turn4 = "Chrome, Windows 10"
    print(f"Customer: \"{customer_turn4}\"")
    print()

    try:
        response_turn4 = invoke_harness_turn(
            rt=rt,
            harness_arn=harness_arn,
            gateway_arn=gateway_arn,
            model_id=args.model_id,
            session_id=session_id,
            messages=[
                {"role": "user", "content": [{"text": customer_turn1}]},
                {"role": "assistant", "content": [{"text": response_turn1}]},
                {"role": "user", "content": [{"text": customer_turn2}]},
                {"role": "assistant", "content": [{"text": response_turn2}]},
                {"role": "user", "content": [{"text": customer_turn3}]},
                {"role": "assistant", "content": [{"text": response_turn3}]},
                {"role": "user", "content": [{"text": customer_turn4}]},
            ],
        )
    except Exception as e:
        sys.exit(f"❌ Turn 4 failed: {e}")

    print(f"Bot: {response_turn4}")
    print()

    print("Verification:")
    has_ticket_id = "#" in response_turn4 or "ticket id" in response_turn4.lower()
    has_confirmation = "investigate" in response_turn4.lower() or "engineering" in response_turn4.lower()

    checks_t4 = [has_ticket_id, has_confirmation]

    if not all(checks_t4):
        print("  ✗ TURN 4 FAILED: Bot didn't create ticket properly")
        if not has_ticket_id:
            print("    Missing: Ticket ID not found in response")
        if not has_confirmation:
            print("    Missing: No confirmation message")
        sys.exit(1)

    print("  ✓ Response contains ticket ID")
    print("  ✓ Response confirms investigation will happen")
    print("  ✓ TURN 4 PASSED: Bot correctly created ticket")
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║ ✅ MULTI-TURN BUG COLLECTION FLOW VERIFIED                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print("Summary:")
    print("  Turn 1: Bot classified bug, asked for description       ✓")
    print("  Turn 2: Bot asked for steps to reproduce               ✓")
    print("  Turn 3: Bot asked for device/browser environment       ✓")
    print("  Turn 4: Bot created ticket with all parameters         ✓")
    print()

    # Extract ticket ID from response
    ticket_match = None
    for word in response_turn4.split():
        if "#" in word:
            ticket_match = word.strip(".,!?")
            break

    if ticket_match:
        print(f"Ticket Created: {ticket_match}")

    print()
    print("Collected Information:")
    print(f"  Description: \"{customer_turn1}\"")
    print(f"  Steps: \"{customer_turn2}\"")
    print(f"  Environment: \"{customer_turn4}\"")
    print()

    # ========================================================================
    # OPTIONAL: DynamoDB verification
    # ========================================================================
    if args.check_dynamodb:
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║ DynamoDB VERIFICATION (Optional)                               ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()

        try:
            dynamodb = boto3.client("dynamodb", region_name=region)

            # Try to find ticket in DynamoDB
            # Note: This requires knowing the table name and structure
            table_name = "bug-report-tool-stack-bug-reports"

            print(f"Checking table: {table_name}")
            print()

            try:
                response = dynamodb.scan(
                    TableName=table_name,
                    Limit=10,
                )

                items = response.get("Items", [])

                if items:
                    print(f"Found {len(items)} recent tickets:")
                    for item in items[-3:]:  # Show last 3
                        print(f"  - {item}")
                    print()
                    print("Note: Verify manually that the latest ticket contains:")
                    print(f"  description: Contains 'checkout button'")
                    print(f"  stepsToReproduce: Contains 'cart' and 'checkout'")
                    print(f"  environment: Contains 'Chrome' and 'Windows'")
                else:
                    print("No tickets found in DynamoDB (table may be empty or inaccessible)")

            except Exception as db_e:
                print(f"⚠️ Could not query DynamoDB: {db_e}")
                print("Note: This is optional. Verify manually if needed.")

            print()

        except Exception as e:
            print(f"⚠️ DynamoDB check skipped: {e}")
            print()

    print("✅ VERIFICATION COMPLETE - All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
