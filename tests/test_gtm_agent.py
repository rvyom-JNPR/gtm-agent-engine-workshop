import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import get_prospect, send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    def test_blocks_disqualified_prospects_with_explicit_override(self):
        runtime = SimpleNamespace(config={"metadata": {"user_id": "rep_amills"}})
        disqualified = get_prospect.invoke({"prospect_id": "LEAD-50001"})["prospect"]
        qualified = get_prospect.invoke({"prospect_id": "LEAD-12853"})["prospect"]

        blocked = send_prospect_email.func(
            disqualified,
            "Pricing Deck",
            "Please review the attached deck.",
            runtime,
        )
        overridden = send_prospect_email.func(
            disqualified,
            "Pricing Deck",
            "Please review the attached deck.",
            runtime,
            allow_disqualified=True,
        )
        sent = send_prospect_email.func(
            qualified,
            "Welcome",
            "Thanks for your interest.",
            runtime,
        )

        self.assertEqual(
            blocked,
            {
                "status": "blocked",
                "error": "Prospect is disqualified; re-run with allow_disqualified=True to override.",
            },
        )
        self.assertEqual(overridden["status"], "sent")
        self.assertEqual(sent["status"], "sent")
