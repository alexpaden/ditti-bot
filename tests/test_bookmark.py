import pytest
from farcaster.client import Warpcast
from farcaster.models import Parent

from ditti.commands.command_manager import Commands

# Remove the MockWarpcast class as it's no longer needed


# Test cases for parse_bookmark_command function
@pytest.mark.parametrize(
    "call_text, expected_output",
    [
        ("@ditti bookmark", {"title": None, "tag": None}),
        ("@ditti bookmark title", {"title": "title", "tag": None}),
        (
            "@ditti bookmark this is my title string --tag evrything",
            {"title": "this is my title string", "tag": "evrything"},
        ),
        (
            "@ditti bookmark this is my title string —tag evrything",
            {"title": "this is my title string", "tag": "evrything"},
        ),
        (
            "@ditti bookmark this is my title string —tag evrything extra text",
            {"title": "this is my title string", "tag": "evrything"},
        ),
        (
            "@ditti bookmark this is my title string --tag",
            {"title": "this is my title string", "tag": None},
        ),
        ("@ditti bookmark —tag tag_only", {"title": None, "tag": "tag_only"}),
    ],
)
def test_parse_bookmark_command(
    fcc: Warpcast, commands: Commands, call_text, expected_output
):
    bookmark = commands.bookmark
    result = bookmark.parse_bookmark_command(call_text)
    assert result == expected_output


# Test cases for start_bookmark function
@pytest.mark.parametrize(
    "hash_value, expected_output",
    [
        (
            "0xdf7c3b1def8805067ca17e78ec27d35d6dd4400c",
            (
                "Please provide a title for your bookmark. "
                "`@ditti bookmark <title text> --tag <category>`",
                Parent(fid=533, hash="0xdf7c3b1def8805067ca17e78ec27d35d6dd4400c"),
            ),
        ),
        (
            "0x9aa0555f7ca3ed35e32103248d4e941f863340b8",
            (
                "'this is my title string' was saved to your bookmarks! 🔖",
                Parent(fid=533, hash="0x9aa0555f7ca3ed35e32103248d4e941f863340b8"),
            ),
        ),
    ],
)
def test_start_bookmark(fcc: Warpcast, commands: Commands, hash_value, expected_output):
    bookmark = commands.bookmark
    call_cast = fcc.get_cast(hash=hash_value).cast
    result = bookmark.start_bookmark(call_cast)
    assert result[0] == expected_output[0]
    assert result[1].fid == expected_output[1].fid
    assert result[1].hash == expected_output[1].hash
