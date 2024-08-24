import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from gpt_cli.cli import main, print_help  
class TestCLI(unittest.TestCase):

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('gpt_cli.cli.get_api_key')
    @patch('gpt_cli.cli.OpenAI')
    def test_main_success(self, MockOpenAI, MockGetApiKey, mock_stdout):
        MockGetApiKey.return_value = 'fake_api_key'
        
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='Test response'))]
        )
        
        with patch('builtins.input', side_effect=['Test question', 'exit']):
            with patch('sys.argv', ['gpt_cli/cli.py']):
                main()
        
        output = mock_stdout.getvalue()
        self.assertIn('\x1b[92m\x1b[1mAI: \x1b[0m\x1b[93mTest response \x1b[0m', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_help(self, mock_stdout):
        print_help()
        output = mock_stdout.getvalue()
        self.assertIn('Usage: gpt [OPTIONS]', output)
        self.assertIn('-m, --model TEXT', output)
        self.assertIn('-t, --tokens INTEGER', output)
        self.assertIn('-T, --temperature FLOAT', output)

    @patch('sys.exit')
    @patch('gpt_cli.cli.get_api_key')
    def test_no_api_key(self, MockGetApiKey, mock_exit):
        MockGetApiKey.return_value = None
        
        with patch('sys.argv', ['gpt_cli/cli.py']):
            main()
        
        mock_exit.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()