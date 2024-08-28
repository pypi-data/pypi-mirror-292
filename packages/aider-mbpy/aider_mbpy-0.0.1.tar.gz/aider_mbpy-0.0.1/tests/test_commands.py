import unittest
from unittest.mock import Mock, patch
from aider.commands import Commands
from aider.io import InputOutput

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.io = Mock(spec=InputOutput)
        self.coder = Mock()
        self.commands = Commands(self.io, self.coder)

    @patch('aider.commands.requests.get')
    @patch('aider.commands.BeautifulSoup')
    @patch('aider.commands.Console')
    def test_cmd_websearch(self, mock_console, mock_bs, mock_get):
        # Mock the response
        mock_response = Mock()
        mock_response.text = '<html><body><div class="g"><h3>Test Title</h3><a href="http://test.com">Link</a><div class="VwiC3b">Test Snippet</div></div></body></html>'
        mock_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = Mock()
        mock_soup.select.return_value = [mock_response.text]
        mock_bs.return_value = mock_soup

        # Mock Console
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        # Run the command
        result = self.commands.cmd_websearch("test query")

        # Assertions
        mock_get.assert_called_once()
        mock_bs.assert_called_once()
        mock_console_instance.print.assert_called_once()
        self.assertIn("Web Search Results:", result)
        self.assertIn("Title: Test Title", result)
        self.assertIn("URL: http://test.com", result)
        self.assertIn("Snippet: Test Snippet", result)

if __name__ == '__main__':
    unittest.main()
