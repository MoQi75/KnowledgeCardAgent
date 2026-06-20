"""Document loading helpers for the knowledge card system."""

from pathlib import Path


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}


class DocumentLoadError(ValueError):
    """Raised when a learning document cannot be loaded."""


def load_text(source: str) -> tuple[str, dict[str, str]]:
    """Load plain text or a local document path.

    Plain text remains the default path so the agent can work without files.
    TXT and Markdown files are read directly. PDF is supported through pypdf,
    which is already declared in this project.
    """
    candidate = Path(source).expanduser()
    if not candidate.exists():
        return source, {"source_type": "text", "title": _title_from_text(source)}

    if not candidate.is_file():
        raise DocumentLoadError(f"Document path is not a file: {candidate}")

    suffix = candidate.suffix.lower()
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        return candidate.read_text(encoding="utf-8"), {
            "source_type": suffix.lstrip("."),
            "title": candidate.stem,
            "file_path": str(candidate),
        }

    if suffix == ".pdf":
        return _load_pdf(candidate), {
            "source_type": "pdf",
            "title": candidate.stem,
            "file_path": str(candidate),
        }

    raise DocumentLoadError(
        f"Unsupported document type: {suffix or '<none>'}. Supported: text, txt, md, pdf."
    )


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise DocumentLoadError(
            "PDF loading requires pypdf. The project declares pypdf; install dependencies first."
        ) from e

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as e:
        raise DocumentLoadError(f"Failed to read PDF document: {path}") from e

    text = "\n\n".join(page.strip() for page in pages if page.strip())
    if not text:
        raise DocumentLoadError(f"No extractable text found in PDF document: {path}")
    return text


def _title_from_text(text: str) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line[:80] or "Learning material"

