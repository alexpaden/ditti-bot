from ditti.commands.command_manager import Commands

cast_hash = "0x97e621cef46e6acb1f7b32e4b2e4138b50d61d3e28c9e9624d66123c07e0419c"
cast_text = "这是与 foo bar 相当的示例文本"
lang_result = "zh-CN"
translated_text = "Here is the sample text equivalent to foo bar"


def test_get_lang(commands: Commands):
    response = commands.translate.get_lang(text="这是与 foo bar 相当的示例文本")
    assert lang_result == response


def test_translate_text(commands: Commands):
    response = commands.translate.translate(text=cast_text, src_lang=lang_result)
    assert response == translated_text
