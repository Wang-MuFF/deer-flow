"""Tests for ``deerflow.utils.text_detection``."""

from __future__ import annotations

from pathlib import Path

import pytest

from deerflow.utils.text_detection import (
    ACTIVE_CONTENT_MIME_TYPES,
    _is_active_content_mime_type,
    is_text_file_by_content,
)


def test_text_file_with_plain_content_is_text(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("plain text content\n", encoding="utf-8")

    assert is_text_file_by_content(path) is True


def test_empty_file_is_text(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")

    assert is_text_file_by_content(path) is True


def test_file_with_null_byte_in_sample_is_binary(tmp_path: Path) -> None:
    path = tmp_path / "binary.bin"
    path.write_bytes(b"header\x00payload")

    assert is_text_file_by_content(path) is False


def test_null_byte_after_the_sample_is_not_detected(tmp_path: Path) -> None:
    path = tmp_path / "late-null.bin"
    path.write_bytes(b"a" * 10 + b"\x00")

    assert is_text_file_by_content(path, sample_size=10) is True


def test_nonexistent_file_is_not_text(tmp_path: Path) -> None:
    assert is_text_file_by_content(tmp_path / "missing.txt") is False


def test_directory_is_not_text(tmp_path: Path) -> None:
    assert is_text_file_by_content(tmp_path) is False


def test_utf8_content_with_multibyte_characters_is_text(tmp_path: Path) -> None:
    path = tmp_path / "unicode.txt"
    path.write_text("中文内容 – with an en dash\n", encoding="utf-8")

    assert is_text_file_by_content(path) is True


@pytest.mark.parametrize(
    "mime_type",
    [
        "text/html",
        "application/xhtml+xml",
        "image/svg",
        "image/svg+xml",
        "text/xml",
        "application/xml",
        "text/xsl",
        "application/rss+xml",
        "application/atom+xml",
        "TEXT/HTML",
        "Application/XHTML+XML",
    ],
)
def test_active_content_mime_types_are_detected(mime_type: str) -> None:
    assert _is_active_content_mime_type(mime_type) is True


@pytest.mark.parametrize(
    "mime_type",
    [
        None,
        "",
        "text/plain",
        "application/json",
        "image/png",
        "application/pdf",
        "application/octet-stream",
        "text/xml; charset=utf-8",
    ],
)
def test_non_active_content_mime_types_are_rejected(mime_type: str | None) -> None:
    assert _is_active_content_mime_type(mime_type) is False


def test_active_content_mime_types_are_lowercase() -> None:
    assert all(mime_type == mime_type.lower() for mime_type in ACTIVE_CONTENT_MIME_TYPES)
