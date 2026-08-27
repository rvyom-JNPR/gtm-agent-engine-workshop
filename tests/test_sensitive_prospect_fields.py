import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, get_prospect


class SensitiveProspectFieldsTest(unittest.TestCase):
    def setUp(self):
        data_service._PROFILES.clear()

    def test_prospect_tools_omit_billing_qualification(self):
        prospect_id = "LEAD-15229"

        contact_result = get_prospect.invoke({"prospect_id": prospect_id})
        profile_result = build_prospect_profile.invoke({"prospect_id": prospect_id})

        self.assertNotIn("billing_qualification", contact_result["prospect"])
        self.assertNotIn("billing_qualification", profile_result["prospect_profile"])
        self.assertNotIn("billing_qualification", data_service._PROFILES[prospect_id])


if __name__ == "__main__":
    unittest.main()
