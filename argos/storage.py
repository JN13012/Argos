"""Bounded JSON input and atomic output, with no dependency or network access."""

import hashlib
import json
import os
from pathlib import Path
import tempfile


MAX_DOCUMENT_BYTES = 1024 * 1024


class ValidationError(ValueError):
    """An input violates the offline assessment contract."""


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("JSON contains duplicate object keys")
        result[key] = value
    return result


def _invalid_number(value):
    raise ValidationError("JSON contains a non-standard number")


def load_document(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_DOCUMENT_BYTES + 1)
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValidationError("Assessment exceeds the 1 MiB input limit")
    try:
        return json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_keys,
            parse_constant=_invalid_number,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValidationError("Assessment must be a valid UTF-8 JSON document") from exc


def json_text(document, *, bounded=False):
    text = json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if bounded and len(text.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise ValidationError("Assessment output exceeds the 1 MiB input limit")
    return text


def document_digest(document):
    return hashlib.sha256(json_text(document).encode("utf-8")).hexdigest()


def write_output(path, text, *, force=False, protected=()):
    """Publish a completed file atomically; never overwrite an input or proof."""
    path = Path(path)
    if path.is_symlink():
        raise ValidationError("Output must not be a symbolic link")
    target = path.resolve()
    for item in protected:
        source = Path(item)
        if target == source.resolve() or (
            path.exists() and source.exists() and path.samefile(source)
        ):
            raise ValidationError("Output must not overwrite an input or evidence file")
    if path.exists() and not force:
        raise ValidationError("Output already exists; choose another path or use --force")
    if path.exists() and not path.is_file():
        raise ValidationError("Output must be a regular file")
    raw = text.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        if force:
            os.replace(temporary, path)
        else:
            try:
                os.link(temporary, path)
            except FileExistsError as exc:
                raise ValidationError("Output already exists; choose another path") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
