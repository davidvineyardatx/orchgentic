from pathlib import Path
from orchgentic.core.exceptions import KnowledgeError

def load_text(path: str) -> str:
    p = Path(path)

    if not p.exists():
        raise KnowledgeError(f"File not found: {path}")

    suffix = p.suffix.lower()

    if suffix in [".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".py"]:
        return p.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise KnowledgeError("PDF support requires: pip install -e '.[docs]'") from exc

        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == ".docx":
        try:
            import docx
        except ImportError as exc:
            raise KnowledgeError("DOCX support requires: pip install -e '.[docs]'") from exc

        document = docx.Document(str(p))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise KnowledgeError(f"Unsupported file type: {suffix}")
