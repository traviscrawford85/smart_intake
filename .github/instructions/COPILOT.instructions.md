---
applyTo: '**/Dockerfile'
---
Always ensure that all Python code is linted, all requirements are up to date, and that each service (intake_agent, clio_manage, smart_intake_dashboard) has a working Dockerfile.
When patching or adding features, update the Dockerfile and requirements as needed.
Use the GitHub Actions workflow to verify builds and linting on every PR.