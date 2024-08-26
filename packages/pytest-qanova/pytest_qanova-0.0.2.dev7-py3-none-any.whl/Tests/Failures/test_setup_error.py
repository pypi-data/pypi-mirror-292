class TestSetupError:
    a = ''
    
    @classmethod
    def setup_class(cls):
        b = cls.a + 8
    
    def test_setup(self):
        assert True
        