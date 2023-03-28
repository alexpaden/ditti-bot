from PIL import ImageFont

from ditti.commands.command_manager import Commands


def test_remove_urls(commands: Commands):
    sample_text = "Visit https://www.example.com for more info."
    expected_text = "Visit  for more info."
    result = commands.text2img.remove_urls(sample_text)
    assert result == expected_text


def test_get_bionic_reading_formatted_text(commands: Commands):
    sample_text = "This is a test string."
    result = commands.text2img.get_bionic_reading_formatted_text(sample_text)
    assert result is not None


def test_extract_html(commands: Commands):
    sample_html = (
        '<div class="bionic-reader-container">' "This is a <b>test</b> string." "</div>"
    )
    expected_text = "This is a <b>test</b> string."
    result = commands.text2img.extract_html(sample_html)
    assert result == expected_text


def test_wrap_text(commands: Commands):
    sample_text = "This is a test string to check the wrap_text function."
    font_name_bold = "./ditti/helpers/fonts/SourceSansPro-Regular.ttf"
    font_bold = ImageFont.truetype(font_name_bold, 25)
    result = commands.text2img.wrap_text(sample_text, font_bold, 200)
    assert "\n" in result


def test_convert(commands: Commands):
    sample_text = "This is a test string."
    result = commands.text2img.convert(sample_text)
    assert result.startswith("https://")
