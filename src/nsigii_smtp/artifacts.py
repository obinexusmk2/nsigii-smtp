from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import mimetypes
import zipfile


@dataclass(slots=True)
class Artifact:
    filename: str
    content: bytes
    mime_type: str


class ArtifactEncoder:
    """Builds attachment artifacts without coupling them to SMTP transport."""

    @staticmethod
    def from_text(filename: str, text: str, encoding: str = "utf-8") -> Artifact:
        return Artifact(
            filename=filename,
            content=text.encode(encoding),
            mime_type="text/plain",
        )

    @staticmethod
    def from_file(path: str | Path) -> Artifact:
        file_path = Path(path)
        mime_type, _ = mimetypes.guess_type(file_path.name)
        return Artifact(
            filename=file_path.name,
            content=file_path.read_bytes(),
            mime_type=mime_type or "application/octet-stream",
        )

    @staticmethod
    def zip_artifacts(zip_name: str, artifacts: list[Artifact]) -> Artifact:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for artifact in artifacts:
                zf.writestr(artifact.filename, artifact.content)
        return Artifact(
            filename=zip_name,
            content=buffer.getvalue(),
            mime_type="application/zip",
        )
