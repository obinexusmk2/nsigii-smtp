from io import BytesIO
import zipfile

from nsigii_smtp import ArtifactEncoder


def test_text_artifact_encoding():
    artifact = ArtifactEncoder.from_text("help.txt", "Need food and water")
    assert artifact.filename == "help.txt"
    assert artifact.mime_type == "text/plain"
    assert artifact.content.decode() == "Need food and water"


def test_zip_artifacts_contains_members():
    first = ArtifactEncoder.from_text("a.txt", "A")
    second = ArtifactEncoder.from_text("b.txt", "B")
    archive = ArtifactEncoder.zip_artifacts("bundle.zip", [first, second])
    with zipfile.ZipFile(BytesIO(archive.content)) as zf:
        assert sorted(zf.namelist()) == ["a.txt", "b.txt"]
