def test_config(commands):
    assert commands is not None
    assert commands.fcc is not None
    assert commands.supabase is not None
    assert commands.translate is not None
    assert commands.thread is not None
    assert commands.bot_username is not None
