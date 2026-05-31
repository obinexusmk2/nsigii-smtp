# nsigii-smtp

`nsigii-smtp` is a Python SDK and CLI for NSIGII humanitarian message dispatch.
It is designed for structured SMTP delivery of requests involving food, water,
shelter, medical supplies, and related urgent needs.

The package follows the NSIGII trilateral model:

- `HERE_AND_NOW` maps to internal `alpha` transport behavior
- `THERE_AND_THEN` maps to internal `beta` transport behavior
- `WHEN_AND_WHERE` maps to internal `gamma` transport behavior

## Features

- Structured NSIGII message envelope
- Humanitarian payload validation
- SMTP transport with environment-variable configuration support
- Artifact packaging for text and zip attachments
- CLI for immediate send and future scheduling

## Quick Start

```bash
python -m pip install -e .[dev]
```

Immediate send:

```bash
nsigii-smtp send --from sender@example.org --to aid@example.org --subject "Need food and water" --body "Urgent request for food, water, and shelter." --need food --need water --need shelter --state HERE_AND_NOW
```

Scheduled send:

```bash
nsigii-smtp schedule --from sender@example.org --to aid@example.org --subject "Follow-up request" --body "Please check availability tomorrow." --need food --state WHEN_AND_WHERE --send-at 2026-06-01T09:30:00+01:00
```

PowerShell note:

- Prefer a single-line command, or use the PowerShell continuation character `` ` `` instead of `^`.
- If you do not pass `--smtp-host`, set `NSIGII_SMTP_HOST` first.

Example:

```powershell
$env:NSIGII_SMTP_HOST = "smtp.gmail.com"
nsigii-smtp send --from sender@example.org --to aid@example.org --subject "Need food and water" --body "Urgent request for food, water, and shelter." --need food --state HERE_AND_NOW
```

Important:

- `smtp.example.org` is only a documentation placeholder, not a real mail server.
- For Gmail, use `smtp.gmail.com` with port `587` and an app password if account security requires it.

## Pizza API Note

`pizzaapi` is not used by the runtime package. It is treated only as a teaching
example of API abstraction in Python: just as a pizza-ordering wrapper models an
order before sending it to a transport boundary, `nsigii-smtp` models a
humanitarian aid request before sending it through SMTP.

See [docs/examples/pizzaapi_example.md](docs/examples/pizzaapi_example.md).
![https://github.com/RIAEvangelist/node-dominos-pizza-api]
