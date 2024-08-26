class TestTeardownError:
    @classmethod
    def setup_class(cls):
        pass
    
    def test_teardown(self):
        assert True
        
    @classmethod
    def teardown_class(cls):
        assert False, "Assertion Message"
