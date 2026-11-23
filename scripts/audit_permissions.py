#!/usr/bin/env python3
"""Fail when a GitHub Actions workflow leaves GITHUB_TOKEN permissions loose."""

import sys
from pathlib import Path

import yaml

WORKFLOW_GLOBS = ("*.yml", "*.yaml")
WORKFLOW_DIR = Path(".github/workflows")
WRITE_ALL = "write-all"


def write_scopes(permissions):
    """Names of the scopes in a permissions mapping that are set to write."""
    if not isinstance(permissions, dict):
        return []
    return [scope for scope, level in permissions.items() if level == "write"]


def audit_workflow(path):
    """Return one message per permissions problem found in `path`."""
    try:
        doc = yaml.safe_load(path.read_text())
    except OSError as exc:
        return [f"{path}: cannot read: {exc.strerror}"]
    except yaml.YAMLError as exc:
        return [f"{path}: not valid YAML: {exc}"]
    jobs = doc.get("jobs") if isinstance(doc, dict) else None
    if not isinstance(jobs, dict):
        return [f"{path}: no jobs mapping found"]

    findings = []
    top = doc.get("permissions")
    if top == WRITE_ALL:
        findings.append(f"{path}: top-level permissions is {WRITE_ALL}")
    for scope in write_scopes(top):
        findings.append(
            f"{path}: top-level permissions grants {scope}: write to every job"
        )

    for name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        own = job.get("permissions")
        if own == WRITE_ALL:
            findings.append(f"{path}: job '{name}' permissions is {WRITE_ALL}")
        elif own is None and top is None:
            findings.append(f"{path}: job '{name}' has no permissions and the workflow sets none")
    return findings


def collect(paths):
    if paths:
        return [Path(p) for p in paths]
    return sorted(f for pattern in WORKFLOW_GLOBS for f in WORKFLOW_DIR.glob(pattern))


def main(argv=None):
    files = collect(sys.argv[1:] if argv is None else argv)
    if not files:
        print(f"no workflow files found under {WORKFLOW_DIR}", file=sys.stderr)
        return 1
    findings = [m for f in files for m in audit_workflow(f)]
    for message in findings:
        print(message)
    print(f"{len(files)} workflow(s) checked, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
