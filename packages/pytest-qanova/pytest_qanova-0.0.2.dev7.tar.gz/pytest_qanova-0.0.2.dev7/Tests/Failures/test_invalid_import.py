# Collection failure

def test_invalid_import():
    import non_existent_module  # This will cause an ImportError
    print(non_existent_module)
    assert non_existent_module
    