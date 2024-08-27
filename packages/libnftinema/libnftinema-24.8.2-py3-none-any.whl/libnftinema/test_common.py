from libnftinema.common import get_url_path


def test_get_qs():
    input_url = "https://x.com/dir/file.png?z=3&x=1&y=2#fragment"
    expected_output = "/dir/file.png?x=1&y=2&z=3#fragment"
    result = get_url_path(input_url)
    assert result == expected_output, f"Expected {expected_output}, got {result}"
