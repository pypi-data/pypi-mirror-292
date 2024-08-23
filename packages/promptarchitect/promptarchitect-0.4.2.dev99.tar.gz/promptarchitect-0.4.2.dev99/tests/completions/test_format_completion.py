from promptarchitect.completions.format import Format, FormatCheckCompletion


def test_format_check_used():
    completion = FormatCheckCompletion()
    comment = "FORMAT == json"
    assert completion.format_check_used(comment) is True


def test_format_check_not_used():
    completion = FormatCheckCompletion()
    comment = "This is a comment without any format check."
    assert completion.format_check_used(comment) is False


def test_check_format_html_valid():
    completion = FormatCheckCompletion(format=Format.HTML)
    data = "<html><body><h1>Hello World</h1></body></html>"
    assert completion.check_format(data) is True


def test_check_format_json_valid():
    completion = FormatCheckCompletion(format=Format.JSON)
    data = '{"name": "John", "age": 30}'
    assert completion.check_format(data) is True


def test_check_format_json_invalid():
    completion = FormatCheckCompletion(format=Format.JSON)
    data = '{"name": "John", "age": 30,}'
    assert completion.check_format(data) is False


def test_check_format_text_valid():
    completion = FormatCheckCompletion(format=Format.TEXT)
    data = "This is a valid text."
    assert completion.check_format(data) is True


def test_check_format_text_invalid():
    completion = FormatCheckCompletion(format=Format.TEXT)
    data = "This is an invalid text with special characters: äöü"
    assert completion.check_format(data) is False


def test_check_format_markdown_valid():
    completion = FormatCheckCompletion(format=Format.MARKDOWN)
    data = "# Heading\n\nThis is some **bold** text."
    assert completion.check_format(data) is True
