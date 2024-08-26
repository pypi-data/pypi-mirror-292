import unittest
from TkEasyGo.core import SimpleWindow

class TestSimpleWindow(unittest.TestCase):
    def setUp(self):
        self.window = SimpleWindow()

    def test_add_button(self):
        def dummy_command():
            pass
        self.window.add_button("Test Button", dummy_command)
        button = self.window.widgets.get('button')
        self.assertIsNotNone(button)
        self.assertEqual(button.cget('text'), "Test Button")

    def test_add_textbox(self):
        textbox = self.window.add_textbox("Test")
        self.assertEqual(textbox.get(), "Test")

if __name__ == '__main__':
    unittest.main()
