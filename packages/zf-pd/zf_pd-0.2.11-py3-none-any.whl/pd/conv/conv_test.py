import os

import pytest

from pd.conv.conv import FileSource, generate_file_sources


def test_file_source():
    fs = FileSource(name="test", type="txt", path="/path/to")
    assert str(fs) == "/path/to/test.txt"
    assert fs.name == "test"
    assert fs.type == "txt"
    assert fs.path == "/path/to"


def test_file_source_immutability():
    fs = FileSource(name="test", type="txt", path="/path/to")
    with pytest.raises(AttributeError):
        fs.name = "new_name"


@pytest.mark.parametrize(
    "src_filepath, dst_format, expected",
    [
        (
            "/path/to/file.txt",
            "pdf",
            (
                FileSource(name="file", type=".txt", path="/path/to"),
                FileSource(name="file", type="pdf", path="/path/to"),
            ),
        ),
        (
            "/home/user/doc.docx",
            "txt",
            (
                FileSource(name="doc", type=".docx", path="/home/user"),
                FileSource(name="doc", type="txt", path="/home/user"),
            ),
        ),
        (
            "relative/path/image.jpg",
            "png",
            (
                FileSource(name="image", type=".jpg", path="relative/path"),
                FileSource(name="image", type="png", path="relative/path"),
            ),
        ),
    ],
)
def test_generate_file_sources(src_filepath, dst_format, expected):
    result = generate_file_sources(src_filepath, dst_format)
    assert result == expected
    assert isinstance(result[0], FileSource)
    assert isinstance(result[1], FileSource)


def test_generate_file_sources_with_multiple_dots():
    result = generate_file_sources("/path/to/file.with.dots.txt", "pdf")
    assert result[0].name == "file.with.dots"
    assert result[0].type == ".txt"
    assert result[1].name == "file.with.dots"
    assert result[1].type == "pdf"


def test_generate_file_sources_with_no_extension():
    result = generate_file_sources("/path/to/file_without_extension", "pdf")
    assert result[0].name == "file_without_extension"
    assert result[0].type == ""
    assert result[1].name == "file_without_extension"
    assert result[1].type == "pdf"
