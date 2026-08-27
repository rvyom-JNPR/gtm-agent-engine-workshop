import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service
from gtm_agent.gtm_agent import ProspectScore, build_prospect_profile, score_prospect


class ProspectUpdateTest(unittest.TestCase):
    def setUp(self):
        self.prospect_id = "LEAD-39002"
        self.original_tech_stack = list(data_service.PROSPECTS[self.prospect_id]["tech_stack"])
        self.original_profile = data_service._PROFILES.pop(self.prospect_id, None)
        build_prospect_profile.invoke(self.prospect_id)

    def tearDown(self):
        data_service.PROSPECTS[self.prospect_id]["tech_stack"] = self.original_tech_stack
        if self.original_profile is None:
            data_service._PROFILES.pop(self.prospect_id, None)
        else:
            data_service._PROFILES[self.prospect_id] = self.original_profile

    def test_update_then_score_uses_persisted_technology(self):
        update_result = data_service.update_prospect_info(self.prospect_id, "Kafka")

        profile = build_prospect_profile.invoke(self.prospect_id)["prospect_profile"]
        offering = {
            "required_tech_stack": ["Kafka"],
            "min_annual_revenue": 1,
            "description": "Kafka offering",
        }
        score = ProspectScore(
            score=100,
            justification="Kafka is present and no required technologies are missing.",
            rubric_breakdown={
                "revenue_fit": 100,
                "tech_stack_match": 100,
                "segment_fit": 100,
            },
        )
        scoring_llm = unittest.mock.Mock()
        scoring_llm.invoke.return_value = score
        with patch("gtm_agent.gtm_agent._scoring_llm", scoring_llm):
            score_result = score_prospect.invoke({"prospect_profile": profile, "offering": offering})

        self.assertTrue(update_result["updated"])
        self.assertIn("Kafka", update_result["tech_stack"])
        self.assertIn("Kafka", profile["tech_stack"])
        self.assertIn("Kafka", scoring_llm.invoke.call_args.args[0][1]["content"])
        self.assertIn("Kafka is present", score_result["justification"])


if __name__ == "__main__":
    unittest.main()
