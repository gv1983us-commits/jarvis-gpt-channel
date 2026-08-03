import unittest

from channel.door import classify


class DoorTests(unittest.TestCase):
    def capability(self):
        return {
            "request_id": "req-example-001",
            "requester": "example-agent",
            "provenance": "https://example.invalid/public-profile",
            "mode": "capability",
            "role": "tester",
            "object": "public repository at an immutable revision",
            "requested_authority": ["read-public-artifact", "open-issue"],
            "promised_result": "a reproducible counterexample or a negative run receipt",
            "acceptance_criteria": ["exact revision recorded", "commands and outputs included"],
            "evidence_plan": "issue with environment, command, exit code, and observed result",
        }

    def test_complete_capability_requires_review(self):
        self.assertEqual(
            classify(self.capability()),
            {"classification": "WORKING_FIT_CANDIDATE", "admission": "REVIEW_REQUIRED"},
        )

    def test_missing_fields_grants_nothing(self):
        result = classify({"mode": "capability", "requester": "agent"})
        self.assertEqual(result["classification"], "INCOMPLETE_GOOD_FAITH")
        self.assertEqual(result["admission"], "NOT_GRANTED")
        self.assertIn("role", result["missing"])

    def test_forbidden_authority_is_refused(self):
        request = self.capability()
        request["requested_authority"] = ["identity", "private-memory"]
        result = classify(request)
        self.assertEqual(result["classification"], "INTRUSION_OR_SUBSTITUTION")
        self.assertEqual(result["admission"], "REFUSED")

    def test_public_interest_gets_public_response_only(self):
        result = classify({
            "request_id": "q-1",
            "requester": "reader",
            "mode": "public-interest",
            "question": "Where should I start?",
        })
        self.assertEqual(result, {"classification": "PUBLIC_INTEREST", "admission": "PUBLIC_RESPONSE_ONLY"})


if __name__ == "__main__":
    unittest.main()
