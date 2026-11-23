import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_permissions  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class AuditWorkflowTest(unittest.TestCase):
    def test_per_job_write_under_read_only_default_is_clean(self):
        self.assertEqual(audit_permissions.audit_workflow(FIXTURES / "good.yml"), [])

    def test_job_without_any_permissions_is_flagged(self):
        findings = audit_permissions.audit_workflow(FIXTURES / "missing.yml")
        self.assertEqual(len(findings), 1)
        self.assertIn("job 'build' has no permissions", findings[0])

    def test_write_all_is_flagged_at_both_levels(self):
        findings = audit_permissions.audit_workflow(FIXTURES / "write-all.yml")
        self.assertEqual(len(findings), 2)
        self.assertIn("top-level", findings[0])
        self.assertIn("job 'build'", findings[1])

    def test_top_level_write_scope_is_flagged(self):
        findings = audit_permissions.audit_workflow(FIXTURES / "top-write.yml")
        self.assertEqual(len(findings), 1)
        self.assertIn("pull-requests: write", findings[0])

    def test_unreadable_path_is_a_finding_not_a_crash(self):
        findings = audit_permissions.audit_workflow(FIXTURES / "nope.yml")
        self.assertIn("nope.yml: cannot read", findings[0])


class MainTest(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual(audit_permissions.main([str(FIXTURES / "good.yml")]), 0)
        self.assertEqual(audit_permissions.main([str(FIXTURES / "missing.yml")]), 1)


if __name__ == "__main__":
    unittest.main()
