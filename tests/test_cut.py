from ditti.commands.command_manager import Commands


def test_parse_cut_command(commands: Commands):
    cut = commands.cut
    call_text = "@ditti cut this is my title string —tag evrything"
    expected_output = {"title": "this is my title string", "tag": "evrything"}
    result = cut.parse_cut_command(call_text)
    assert result == expected_output


def test_extract_img_links(commands: Commands):
    cut = commands.cut
    parent_text = "https://i.imgur.com/yIB3Lci.jpg"
    expected_output = ["https://i.imgur.com/yIB3Lci.jpg"]
    result = cut.extract_img_urls(parent_text)
    assert result == expected_output
