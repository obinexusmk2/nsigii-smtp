from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import json
import sys

from .artifacts import Artifact, ArtifactEncoder
from .message import HumanNeedPayload, NSIGIIMessage
from .schedule import ScheduleSpec
from .service import NSIGIISMTPService
from .transport import SMTPSettings, SMTPTransport
from .trilateral import TrilateralState


def _parse_state(value: str) -> TrilateralState:
    try:
        return TrilateralState[value]
    except KeyError as exc:
        raise argparse.ArgumentTypeError(f"invalid trilateral state: {value}") from exc


def _parse_send_at(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("send-at must be ISO 8601 format") from exc
    if dt.tzinfo is None:
        raise argparse.ArgumentTypeError("send-at must include timezone information")
    return dt


def _build_artifacts(args: argparse.Namespace) -> list[Artifact]:
    artifacts: list[Artifact] = []
    if args.artifact_text:
        artifacts.append(ArtifactEncoder.from_text(args.artifact_name or "nsigii-message.txt", args.artifact_text))
    for path in args.attach_file or []:
        artifacts.append(ArtifactEncoder.from_file(path))
    if args.zip_artifacts and artifacts:
        return [ArtifactEncoder.zip_artifacts(args.zip_name or "nsigii-artifacts.zip", artifacts)]
    return artifacts


def _build_message(args: argparse.Namespace) -> NSIGIIMessage:
    payload = HumanNeedPayload(
        summary=args.subject,
        needs=args.need,
        details=args.body,
        location=args.location or "",
        contact_name=args.contact_name or "",
    )
    return NSIGIIMessage(
        sender=args.sender,
        recipient=args.recipient,
        subject=args.subject,
        body=args.body,
        payload=payload,
        state=args.state,
        audit_metadata={"mode": args.command},
    )


def _settings_from_args(args: argparse.Namespace) -> SMTPSettings:
    if args.smtp_host:
        return SMTPSettings(
            host=args.smtp_host,
            port=args.smtp_port,
            username=args.smtp_username,
            password=args.smtp_password,
            use_tls=not args.no_tls,
        )
    return SMTPSettings.from_env()


def _add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--from", dest="sender", required=True)
    parser.add_argument("--to", dest="recipient", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--need", action="append", required=True)
    parser.add_argument("--state", type=_parse_state, default=TrilateralState.HERE_AND_NOW)
    parser.add_argument("--location")
    parser.add_argument("--contact-name")
    parser.add_argument("--artifact-text")
    parser.add_argument("--artifact-name")
    parser.add_argument("--attach-file", action="append")
    parser.add_argument("--zip-artifacts", action="store_true")
    parser.add_argument("--zip-name")
    parser.add_argument("--smtp-host")
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--smtp-username")
    parser.add_argument("--smtp-password")
    parser.add_argument("--no-tls", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nsigii-smtp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send")
    _add_shared_arguments(send_parser)

    schedule_parser = subparsers.add_parser("schedule")
    _add_shared_arguments(schedule_parser)
    schedule_parser.add_argument("--send-at", required=True, type=_parse_send_at)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv and "^" in argv:
        parser.error("unexpected '^' argument; in PowerShell use a single line or the backtick (`) line continuation character")
    args = parser.parse_args(argv)

    try:
        artifacts = _build_artifacts(args)
        message = _build_message(args)
        service = NSIGIISMTPService(SMTPTransport(_settings_from_args(args)))

        if args.command == "send":
            result = service.send_now(message, artifacts)
        else:
            schedule = ScheduleSpec(send_at=args.send_at)
            result = service.schedule(message, schedule, artifacts)
    except ValueError as exc:
        parser.error(str(exc))

    json.dump(asdict(result), sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
