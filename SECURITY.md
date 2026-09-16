# Security policy

## Reporting a vulnerability

Do not open a public issue for vulnerabilities or exposed credentials. Use the
repository's private vulnerability-reporting feature or contact the maintainers
through their published security channel.

Include the affected version, reproduction steps, impact, and any suggested
mitigation. Do not include real credentials, private endpoints, or production data.

## Supported versions

Security fixes are provided for the latest released version.

## Credential model

This launcher reads one password from macOS Keychain. Use a dedicated read-only
OpenSearch account with the minimum index permissions required. Tool allowlists
and server settings complement, but do not replace, OpenSearch authorization.
