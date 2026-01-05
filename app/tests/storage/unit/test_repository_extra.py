from storage.repository import delete_client


def test_delete_nonexistent_returns_false():
    # attempt to delete an id that should not exist
    ok = delete_client(999999999)
    assert ok is False
