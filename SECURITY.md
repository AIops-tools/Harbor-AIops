# Security

Report vulnerabilities privately through the repository's GitHub security advisory flow when the repository is available. Do not put credentials, registry URLs with embedded secrets, or private image details into public issues.

Credentials are stored in the encrypted local `secrets.enc` store. The config file contains only target location and username. TLS verification is on by default. All Harbor tools in this first version are read-only; the bundled governance harness records audit metadata and enforces budgets. Use a Harbor account with the least server-side privileges needed for the requested queries.
