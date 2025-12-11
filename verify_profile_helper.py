
from utils.profile_helper import get_profile_picture_url

def test_profile_helper():
    print("Testing get_profile_picture_url...")

    # TestCase 1: None -> UI Avatars
    url = get_profile_picture_url(None, "John Doe")
    print(f"1. None -> {url}")
    assert "ui-avatars.com" in url

    # TestCase 2: External URL -> As is
    ext = "https://example.com/pic.jpg"
    url = get_profile_picture_url(ext, "John Doe")
    print(f"2. External -> {url}")
    assert url == ext

    # TestCase 3: Absolute Path -> As is
    abs_path = "/static/uploads/pic.jpg"
    url = get_profile_picture_url(abs_path, "John Doe")
    print(f"3. Absolute -> {url}")
    assert url == abs_path

    # TestCase 4: Static Path -> Prepend /
    static = "static/uploads/pic.jpg"
    url = get_profile_picture_url(static, "John Doe")
    print(f"4. Static -> {url}")
    assert url == "/static/uploads/pic.jpg"

    # TestCase 5: Legacy/Filename -> Prepend upload path
    fname = "mypic.jpg"
    url = get_profile_picture_url(fname, "John Doe")
    print(f"5. Filename -> {url}")
    assert url == "/static/uploads/profile_pics/mypic.jpg"

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    try:
        test_profile_helper()
    except AssertionError as e:
        print("TEST FAILED")
        raise e
    except Exception as e:
        print(f"ERROR: {e}")
