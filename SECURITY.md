# Security

Report vulnerabilities privately through the repository's GitHub security advisory flow when the repository is available. Do not put credentials, registry URLs with embedded secrets, or private image details into public issues.

Credentials are stored in the encrypted local `secrets.enc` store. The config file contains only target location and username. TLS verification is on by default, and environment proxy settings are not inherited for registry requests. The bundled governance harness records audit metadata and enforces budgets. Use a Harbor account with the least server-side privileges needed for the requested queries and optional scan/tag writes. Scan and tag creation use dry-run; a lost response is marked unknown. Job logs and vulnerability details may contain sensitive data, so share their output only with intended operators.
