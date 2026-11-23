# devops-ci-permissions-audit

A small script that checks GitHub Actions workflows for loose `GITHUB_TOKEN`
permissions. By default the token gets broad scopes on many repositories, so
every workflow should say what it needs and nothing more.

It reports:

- a job that ends up with no explicit `permissions` (none on the job, none at the top level)
- `write-all`, at the top level or on a job
- a write scope at the top level, which every job inherits; grant it per job instead

## Usage

```sh
pip install -r requirements.txt
python3 scripts/audit_permissions.py                  # .github/workflows/*.y*ml
python3 scripts/audit_permissions.py path/to/ci.yml   # specific files
```

Exit code is 0 when clean and 1 when there are findings.
