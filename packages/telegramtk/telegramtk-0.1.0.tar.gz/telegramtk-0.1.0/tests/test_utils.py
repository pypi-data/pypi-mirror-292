from telegramtk import utils


def test_escape_markdown():
    text = 'Just some *Markdown* _stuff_ [here](https://example.com/)'
    escaped_text = utils.escape_markdown(text)
    assert (
        escaped_text
        == 'Just some \\*Markdown\\* \\_stuff\\_ \\[here\\]\\(https://example\\.com/\\)'
    )
