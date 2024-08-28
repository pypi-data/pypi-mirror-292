import codecs
import os
import shutil
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

import git

from aider.coders import Coder
from aider.commands import Commands
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput
from aider.models import Model
from aider.utils import ChdirTemporaryDirectory, GitTemporaryDirectory, make_repo


class TestCommands(TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

        self.GPT35 = Model("gpt-3.5-turbo")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    @patch('requests.get')
    @patch('aider.commands.BeautifulSoup')
    @patch('aider.commands.Console')
    @patch('rich.console.Console._detect_color_system')
    @patch('aider.commands.display_webpage_content')
    def test_cmd_websearch(self, mock_display_webpage_content, mock_detect_color, mock_console, mock_bs, mock_get):
        mock_detect_color.return_value = None
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        mock_response = MagicMock()
        mock_response.text = '<html><body><div class="g"><h3>Test Title</h3><a href="http://test.com">Link</a><div class="VwiC3b">Test Snippet</div></div></body></html>'
        mock_get.return_value = mock_response

        mock_title = MagicMock()
        mock_title.text = "Test Title"
        mock_link = MagicMock()
        mock_link.__getitem__.return_value = "http://test.com"
        mock_snippet = MagicMock()
        mock_snippet.text = "Test Snippet"

        mock_result = MagicMock()
        mock_result.select_one.side_effect = [mock_title, mock_link, mock_snippet]

        mock_soup = MagicMock()
        mock_soup.select.return_value = [mock_result]
        mock_bs.return_value = mock_soup

        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        result = commands.cmd_websearch("test query", test_input="1")

        mock_get.assert_called_once()
        mock_bs.assert_called_once()
        mock_console_instance.print.assert_called_once()
        mock_display_webpage_content.assert_called_once()
        self.assertIn("Web Search Results:", result)
        self.assertIn("Title: Test Title", result)
        self.assertIn("URL: http://test.com", result)
        self.assertIn("Snippet: Test Snippet", result)

        # Print debugging information
        print(f"mock_display_webpage_content.call_count: {mock_display_webpage_content.call_count}")
        print(f"mock_display_webpage_content.call_args: {mock_display_webpage_content.call_args}")

    @patch('os.environ.get')
    @patch('github.Github')
    @patch('rich.console.Console._detect_color_system')
    def test_cmd_github_search(self, mock_detect_color, mock_github, mock_environ_get):
        mock_detect_color.return_value = None
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        mock_environ_get.return_value = 'dummy_token'

        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance

        mock_result = MagicMock()
        mock_result.repository.full_name = 'test/repo'
        mock_result.path = 'test.py'
        mock_result.html_url = 'https://github.com/test/repo/blob/main/test.py'
        mock_result.decoded_content = b'print("Hello, World!")'

        mock_search_results = MagicMock()
        mock_search_results.totalCount = 1
        mock_search_results.__iter__.return_value = [mock_result]

        mock_github_instance.search_code.return_value = mock_search_results

        result = commands.cmd_github_search("test query")

        mock_github_instance.search_code.assert_called_once_with(query="test query")
        self.assertIn("Top 1 GitHub Search Results:", result)
        self.assertIn("Repository: test/repo", result)
        self.assertIn("File: test.py", result)
        self.assertIn("URL: https://github.com/test/repo/blob/main/test.py", result)
        self.assertIn('print("Hello, World!")', result)

    @patch('aider.commands.inspecting.inspect_object')
    def test_cmd_inspect(self, mock_inspect_object):
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        mock_inspect_object.return_value = "Inspection result"

        with patch.object(io, 'tool_output') as mock_tool_output:
            commands.cmd_inspect("test_module")

            mock_inspect_object.assert_called_once_with("test_module")
            mock_tool_output.assert_called_once_with("Inspection result")

        # Test error handling
        mock_inspect_object.side_effect = Exception("Test error")
        with patch.object(io, 'tool_error') as mock_tool_error:
            commands.cmd_inspect("test_module")
            mock_tool_error.assert_called_once_with("Error inspecting test_module: Test error")

    def test_mistral_finetune_dataformat(self):
        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Test valid Mistral finetune format
        valid_data = [
            {"messages": [{"role": "human", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]},
            {"messages": [{"role": "human", "content": "How are you?"}, {"role": "assistant", "content": "I'm doing well, thank you for asking!"}]}
        ]
        result = commands.validate_mistral_finetune_format(valid_data)
        self.assertTrue(result)

        # Test invalid format: missing 'messages' key
        invalid_data1 = [
            {"wrong_key": [{"role": "human", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
        ]
        with self.assertRaises(ValueError) as cm:
            commands.validate_mistral_finetune_format(invalid_data1)
        self.assertEqual(str(cm.exception), "Each item must be a dictionary with a 'messages' key")

        # Test invalid format: wrong role
        invalid_data2 = [
            {"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
        ]
        with self.assertRaises(ValueError) as cm:
            commands.validate_mistral_finetune_format(invalid_data2)
        self.assertEqual(str(cm.exception), "Messages must start with 'human' and alternate between 'human' and 'assistant'")

        # Test invalid format: missing content
        invalid_data3 = [
            {"messages": [{"role": "human", "content": "Hello"}, {"role": "assistant"}]}
        ]
        with self.assertRaises(ValueError) as cm:
            commands.validate_mistral_finetune_format(invalid_data3)
        self.assertEqual(str(cm.exception), "Each message must be a dictionary with 'role' and 'content' keys")

        # Test invalid format: empty messages list
        invalid_data4 = [
            {"messages": []}
        ]
        with self.assertRaises(ValueError) as cm:
            commands.validate_mistral_finetune_format(invalid_data4)
        self.assertEqual(str(cm.exception), "'messages' must be a list with at least two messages")

        # Test invalid format: non-string content
        invalid_data5 = [
            {"messages": [{"role": "human", "content": 123}, {"role": "assistant", "content": "Hi there!"}]}
        ]
        with self.assertRaises(ValueError) as cm:
            commands.validate_mistral_finetune_format(invalid_data5)
        self.assertEqual(str(cm.exception), "Message content must be a string")

    def test_cmd_add(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Call the cmd_add method with 'foo.txt' and 'bar.txt' as a single string
        commands.cmd_add("foo.txt bar.txt")

        # Check if both files have been created in the temporary directory
        self.assertTrue(os.path.exists("foo.txt"))
        self.assertTrue(os.path.exists("bar.txt"))

    def test_cmd_add_bad_glob(self):
        # https://github.com/paul-gauthier/aider/issues/293

        io = InputOutput(pretty=False, yes=False)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        commands.cmd_add("**.txt")

    def test_cmd_add_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Create some test files
        with open("test1.py", "w") as f:
            f.write("print('test1')")
        with open("test2.py", "w") as f:
            f.write("print('test2')")
        with open("test.txt", "w") as f:
            f.write("test")

        # Call the cmd_add method with a glob pattern
        commands.cmd_add("*.py")

        # Check if the Python files have been added to the chat session
        self.assertIn(str(Path("test1.py").resolve()), coder.abs_fnames)
        self.assertIn(str(Path("test2.py").resolve()), coder.abs_fnames)

        # Check if the text file has not been added to the chat session
        self.assertNotIn(str(Path("test.txt").resolve()), coder.abs_fnames)

    def test_cmd_add_no_match(self):
        # yes=False means we will *not* create the file when it is not found
        io = InputOutput(pretty=False, yes=False)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Call the cmd_add method with a non-existent file pattern
        commands.cmd_add("*.nonexistent")

        # Check if no files have been added to the chat session
        self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_add_no_match_but_make_it(self):
        # yes=True means we *will* create the file when it is not found
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        fname = Path("[abc].nonexistent")

        # Call the cmd_add method with a non-existent file pattern
        commands.cmd_add(str(fname))

        # Check if no files have been added to the chat session
        self.assertEqual(len(coder.abs_fnames), 1)
        self.assertTrue(fname.exists())

    def test_cmd_add_drop_directory(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=False)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Create a directory and add files to it using pathlib
        Path("test_dir").mkdir()
        Path("test_dir/another_dir").mkdir()
        Path("test_dir/test_file1.txt").write_text("Test file 1")
        Path("test_dir/test_file2.txt").write_text("Test file 2")
        Path("test_dir/another_dir/test_file.txt").write_text("Test file 3")

        # Call the cmd_add method with a directory
        commands.cmd_add("test_dir test_dir/test_file2.txt")

        # Check if the files have been added to the chat session
        self.assertIn(str(Path("test_dir/test_file1.txt").resolve()), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/test_file2.txt").resolve()), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/another_dir/test_file.txt").resolve()), coder.abs_fnames)

        commands.cmd_drop("test_dir/another_dir")
        self.assertIn(str(Path("test_dir/test_file1.txt").resolve()), coder.abs_fnames)
        self.assertIn(str(Path("test_dir/test_file2.txt").resolve()), coder.abs_fnames)
        self.assertNotIn(
            str(Path("test_dir/another_dir/test_file.txt").resolve()), coder.abs_fnames
        )

        # Issue #139 /add problems when cwd != git_root

        # remember the proper abs path to this file
        abs_fname = str(Path("test_dir/another_dir/test_file.txt").resolve())

        # chdir to someplace other than git_root
        Path("side_dir").mkdir()
        os.chdir("side_dir")

        # add it via it's git_root referenced name
        commands.cmd_add("test_dir/another_dir/test_file.txt")

        # it should be there, but was not in v0.10.0
        self.assertIn(abs_fname, coder.abs_fnames)

        # drop it via it's git_root referenced name
        commands.cmd_drop("test_dir/another_dir/test_file.txt")

        # it should be there, but was not in v0.10.0
        self.assertNotIn(abs_fname, coder.abs_fnames)

    def test_cmd_drop_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        subdir = Path("subdir")
        subdir.mkdir()
        (subdir / "subtest1.py").touch()
        (subdir / "subtest2.py").touch()

        Path("test1.py").touch()
        Path("test2.py").touch()

        # Add some files to the chat session
        commands.cmd_add("*.py")

        self.assertEqual(len(coder.abs_fnames), 2)

        # Call the cmd_drop method with a glob pattern
        commands.cmd_drop("*2.py")

        self.assertIn(str(Path("test1.py").resolve()), coder.abs_fnames)
        self.assertNotIn(str(Path("test2.py").resolve()), coder.abs_fnames)

    def test_cmd_add_bad_encoding(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # Create a new file foo.bad which will fail to decode as utf-8
        with codecs.open("foo.bad", "w", encoding="iso-8859-15") as f:
            f.write("ÆØÅ")  # Characters not present in utf-8

        commands.cmd_add("foo.bad")

        self.assertEqual(coder.abs_fnames, set())

    def test_cmd_git(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)

        with GitTemporaryDirectory() as tempdir:
            # Create a file in the temporary directory
            with open(f"{tempdir}/test.txt", "w") as f:
                f.write("test")

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            # Run the cmd_git method with the arguments "commit -a -m msg"
            commands.cmd_git("add test.txt")
            commands.cmd_git("commit -a -m msg")

            # Check if the file has been committed to the repository
            repo = git.Repo(tempdir)
            files_in_repo = repo.git.ls_files()
            self.assertIn("test.txt", files_in_repo)

    def test_cmd_tokens(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        commands.cmd_add("foo.txt bar.txt")

        # Redirect the standard output to an instance of io.StringIO
        stdout = StringIO()
        sys.stdout = stdout

        commands.cmd_tokens("")

        # Reset the standard output
        sys.stdout = sys.__stdout__

        # Get the console output
        console_output = stdout.getvalue()

        self.assertIn("foo.txt", console_output)
        self.assertIn("bar.txt", console_output)

    def test_cmd_add_from_subdir(self):
        repo = git.Repo.init()
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "testuser@example.com").release()

        # Create three empty files and add them to the git repository
        filenames = ["one.py", Path("subdir") / "two.py", Path("anotherdir") / "three.py"]
        for filename in filenames:
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            repo.git.add(str(file_path))
        repo.git.commit("-m", "added")

        filenames = [str(Path(fn).resolve()) for fn in filenames]

        ###

        os.chdir("subdir")

        io = InputOutput(pretty=False, yes=True)
        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        # this should get added
        commands.cmd_add(str(Path("anotherdir") / "three.py"))

        # this should add one.py
        commands.cmd_add("*.py")

        self.assertIn(filenames[0], coder.abs_fnames)
        self.assertNotIn(filenames[1], coder.abs_fnames)
        self.assertIn(filenames[2], coder.abs_fnames)

    def test_cmd_add_from_subdir_again(self):
        with GitTemporaryDirectory():
            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            Path("side_dir").mkdir()
            os.chdir("side_dir")

            # add a file that is in the side_dir
            with open("temp.txt", "w"):
                pass

            # this was blowing up with GitCommandError, per:
            # https://github.com/paul-gauthier/aider/issues/201
            commands.cmd_add("temp.txt")

    def test_cmd_commit(self):
        with GitTemporaryDirectory():
            fname = "test.txt"
            with open(fname, "w") as f:
                f.write("test")
            repo = git.Repo()
            repo.git.add(fname)
            repo.git.commit("-m", "initial")

            io = InputOutput(pretty=False, yes=True)
            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            self.assertFalse(repo.is_dirty())
            with open(fname, "w") as f:
                f.write("new")
            self.assertTrue(repo.is_dirty())

            commit_message = "Test commit message"
            commands.cmd_commit(commit_message)
            self.assertFalse(repo.is_dirty())

    def test_cmd_add_from_outside_root(self):
        with ChdirTemporaryDirectory() as tmp_dname:
            root = Path("root")
            root.mkdir()
            os.chdir(str(root))

            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            outside_file = Path(tmp_dname) / "outside.txt"
            outside_file.touch()

            # This should not be allowed!
            # https://github.com/paul-gauthier/aider/issues/178
            commands.cmd_add("../outside.txt")

            self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_add_from_outside_git(self):
        with ChdirTemporaryDirectory() as tmp_dname:
            root = Path("root")
            root.mkdir()
            os.chdir(str(root))

            make_repo()

            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            outside_file = Path(tmp_dname) / "outside.txt"
            outside_file.touch()

            # This should not be allowed!
            # It was blowing up with GitCommandError, per:
            # https://github.com/paul-gauthier/aider/issues/178
            commands.cmd_add("../outside.txt")

            self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_add_filename_with_special_chars(self):
        with ChdirTemporaryDirectory():
            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            fname = Path("with[brackets].txt")
            fname.touch()

            commands.cmd_add(str(fname))

            self.assertIn(str(fname.resolve()), coder.abs_fnames)

    def test_cmd_tokens_output(self):
        with GitTemporaryDirectory() as repo_dir:
            # Create a small repository with a few files
            (Path(repo_dir) / "file1.txt").write_text("Content of file 1")
            (Path(repo_dir) / "file2.py").write_text("print('Content of file 2')")
            (Path(repo_dir) / "subdir").mkdir()
            (Path(repo_dir) / "subdir" / "file3.md").write_text("# Content of file 3")

            repo = git.Repo.init(repo_dir)
            repo.git.add(A=True)
            repo.git.commit("-m", "Initial commit")

            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(Model("claude-3-5-sonnet-20240620"), None, io)
            print(coder.get_announcements())
            commands = Commands(io, coder)

            commands.cmd_add("*.txt")

            # Capture the output of cmd_tokens
            original_tool_output = io.tool_output
            output_lines = []

            def capture_output(*args, **kwargs):
                output_lines.extend(args)
                original_tool_output(*args, **kwargs)

            io.tool_output = capture_output

            # Run cmd_tokens
            commands.cmd_tokens("")

            # Restore original tool_output
            io.tool_output = original_tool_output

            # Check if the output includes repository map information
            repo_map_line = next((line for line in output_lines if "repository map" in line), None)
            self.assertIsNotNone(
                repo_map_line, "Repository map information not found in the output"
            )

            # Check if the output includes information about all added files
            self.assertTrue(any("file1.txt" in line for line in output_lines))

            # Check if the total tokens and remaining tokens are reported
            self.assertTrue(any("tokens total" in line for line in output_lines))
            self.assertTrue(any("tokens remaining" in line for line in output_lines))

    def test_cmd_add_dirname_with_special_chars(self):
        with ChdirTemporaryDirectory():
            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            dname = Path("with[brackets]")
            dname.mkdir()
            fname = dname / "filename.txt"
            fname.touch()

            commands.cmd_add(str(dname))

            self.assertIn(str(fname.resolve()), coder.abs_fnames)

    def test_cmd_add_abs_filename(self):
        with ChdirTemporaryDirectory():
            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            fname = Path("file.txt")
            fname.touch()

            commands.cmd_add(str(fname.resolve()))

            self.assertIn(str(fname.resolve()), coder.abs_fnames)

    def test_cmd_add_quoted_filename(self):
        with ChdirTemporaryDirectory():
            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            fname = Path("file with spaces.txt")
            fname.touch()

            commands.cmd_add(f'"{fname}"')

            self.assertIn(str(fname.resolve()), coder.abs_fnames)

    def test_cmd_add_existing_with_dirty_repo(self):
        with GitTemporaryDirectory():
            repo = git.Repo()

            files = ["one.txt", "two.txt"]
            for fname in files:
                Path(fname).touch()
                repo.git.add(fname)
            repo.git.commit("-m", "initial")

            commit = repo.head.commit.hexsha

            # leave a dirty `git rm`
            repo.git.rm("one.txt")

            io = InputOutput(pretty=False, yes=True)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            # There's no reason this /add should trigger a commit
            commands.cmd_add("two.txt")

            self.assertEqual(commit, repo.head.commit.hexsha)

            # Windows is throwing:
            # PermissionError: [WinError 32] The process cannot access
            # the file because it is being used by another process

            repo.git.commit("-m", "cleanup")

            del coder
            del commands
            del repo

    def test_cmd_add_unicode_error(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(self.GPT35, None, io)
        commands = Commands(io, coder)

        fname = "file.txt"
        encoding = "utf-16"
        some_content_which_will_error_if_read_with_encoding_utf8 = "ÅÍÎÏ".encode(encoding)
        with open(fname, "wb") as f:
            f.write(some_content_which_will_error_if_read_with_encoding_utf8)

        commands.cmd_add("file.txt")
        self.assertEqual(coder.abs_fnames, set())

    def test_cmd_add_drop_untracked_files(self):
        with GitTemporaryDirectory():
            repo = git.Repo()

            io = InputOutput(pretty=False, yes=False)
            from aider.coders import Coder

            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            fname = Path("test.txt")
            fname.touch()

            self.assertEqual(len(coder.abs_fnames), 0)

            commands.cmd_add(str(fname))

            files_in_repo = repo.git.ls_files()
            self.assertNotIn(str(fname), files_in_repo)

            self.assertEqual(len(coder.abs_fnames), 1)

            commands.cmd_drop(str(fname))

            self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_undo_with_dirty_files_not_in_last_commit(self):
        with GitTemporaryDirectory() as repo_dir:
            repo = git.Repo(repo_dir)
            io = InputOutput(pretty=False, yes=True)
            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            other_path = Path(repo_dir) / "other_file.txt"
            other_path.write_text("other content")
            repo.git.add(str(other_path))

            # Create and commit a file
            filename = "test_file.txt"
            file_path = Path(repo_dir) / filename
            file_path.write_text("first content")
            repo.git.add(filename)
            repo.git.commit("-m", "first commit")

            file_path.write_text("second content")
            repo.git.add(filename)
            repo.git.commit("-m", "second commit")

            # Store the commit hash
            last_commit_hash = repo.head.commit.hexsha[:7]
            coder.aider_commit_hashes.add(last_commit_hash)

            file_path.write_text("dirty content")

            # Attempt to undo the last commit
            commands.cmd_undo("")

            # Check that the last commit is still present
            self.assertEqual(last_commit_hash, repo.head.commit.hexsha[:7])

            # Put back the initial content (so it's not dirty now)
            file_path.write_text("second content")
            other_path.write_text("dirty content")

            commands.cmd_undo("")
            self.assertNotEqual(last_commit_hash, repo.head.commit.hexsha[:7])

            self.assertEqual(file_path.read_text(), "first content")
            self.assertEqual(other_path.read_text(), "dirty content")

            del coder
            del commands
            del repo

    def test_cmd_undo_with_newly_committed_file(self):
        with GitTemporaryDirectory() as repo_dir:
            repo = git.Repo(repo_dir)
            io = InputOutput(pretty=False, yes=True)
            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            # Put in a random first commit
            filename = "first_file.txt"
            file_path = Path(repo_dir) / filename
            file_path.write_text("new file content")
            repo.git.add(filename)
            repo.git.commit("-m", "Add new file")

            # Create and commit a new file
            filename = "new_file.txt"
            file_path = Path(repo_dir) / filename
            file_path.write_text("new file content")
            repo.git.add(filename)
            repo.git.commit("-m", "Add new file")

            # Store the commit hash
            last_commit_hash = repo.head.commit.hexsha[:7]
            coder.aider_commit_hashes.add(last_commit_hash)

            # Attempt to undo the last commit, should refuse
            commands.cmd_undo("")

            # Check that the last commit was not undone
            self.assertEqual(last_commit_hash, repo.head.commit.hexsha[:7])
            self.assertTrue(file_path.exists())

            del coder
            del commands
            del repo

    def test_cmd_undo_on_first_commit(self):
        with GitTemporaryDirectory() as repo_dir:
            repo = git.Repo(repo_dir)
            io = InputOutput(pretty=False, yes=True)
            coder = Coder.create(self.GPT35, None, io)
            commands = Commands(io, coder)

            # Create and commit a new file
            filename = "new_file.txt"
            file_path = Path(repo_dir) / filename
            file_path.write_text("new file content")
            repo.git.add(filename)
            repo.git.commit("-m", "Add new file")

            # Store the commit hash
            last_commit_hash = repo.head.commit.hexsha[:7]
            coder.aider_commit_hashes.add(last_commit_hash)

            # Attempt to undo the last commit
            commands.cmd_undo("")

            # Check that the commit is still present
            self.assertEqual(last_commit_hash, repo.head.commit.hexsha[:7])
            self.assertTrue(file_path.exists())

            del coder
            del commands
            del repo

    def test_cmd_add_aiderignored_file(self):
        with GitTemporaryDirectory():
            repo = git.Repo()

            fname1 = "ignoreme1.txt"
            fname2 = "ignoreme2.txt"
            fname3 = "dir/ignoreme3.txt"

            Path(fname2).touch()
            repo.git.add(str(fname2))
            repo.git.commit("-m", "initial")

            aignore = Path(".aiderignore")
            aignore.write_text(f"{fname1}\n{fname2}\ndir\n")

            io = InputOutput(yes=True)
            coder = Coder.create(
                self.GPT35, None, io, fnames=[fname1, fname2], aider_ignore_file=str(aignore)
            )
            commands = Commands(io, coder)

            commands.cmd_add(f"{fname1} {fname2} {fname3}")

            self.assertNotIn(fname1, str(coder.abs_fnames))
            self.assertNotIn(fname2, str(coder.abs_fnames))
            self.assertNotIn(fname3, str(coder.abs_fnames))
import pytest
from unittest.mock import patch, Mock

@pytest.fixture
def mock_io():
    return MagicMock()

@pytest.fixture
def mock_coder():
    coder = MagicMock()
    coder.root = "/path/to/repo"
    return coder

@pytest.fixture
def commands(mock_io, mock_coder):
    return Commands(io=mock_io, coder=mock_coder)

def test_cmd_github_search_empty_query(commands):
    commands.cmd_github_search("")
    commands.io.tool_error.assert_called_once_with("Please provide a search query.")

@patch('aider.commands.Commands._scrape_url')
@patch('aider.commands.display_webpage_content')
def test_cmd_web(mock_display, mock_scrape_url, commands):
    mock_scrape_url.return_value = "Scraped content"

    result = commands.cmd_web("https://example.com")

    mock_scrape_url.assert_called_once_with("https://example.com")
    mock_display.assert_called_once_with("https://example.com", "Scraped content")
    assert result == "https://example.com:\n\nScraped content"

@patch('aider.commands.Commands._scrape_url')
def test_cmd_web_no_url(mock_scrape_url, commands):
    result = commands.cmd_web("")
    
    assert result is None
    commands.io.tool_error.assert_called_once_with("Please provide a URL to scrape.")
    mock_scrape_url.assert_not_called()

@patch('aider.commands.Commands._scrape_url')
def test_cmd_web_scraper_error(mock_scrape_url, commands):
    mock_scrape_url.side_effect = Exception("Scraping error")
    
    result = commands.cmd_web("https://example.com")
    
    assert result == "https://example.com:\n\n"
    commands.io.tool_error.assert_called_once_with("Unable to scrape the webpage: Scraping error")

@patch('github.Github')
@patch.dict(os.environ, {'GITHUB_ACCESS_TOKEN': 'dummy_token_for_testing'})
def test_cmd_github_search(mock_github, commands):
    class MockPaginatedList:
        def __init__(self, items):
            self.items = items
            self.totalCount = len(items)
    
        def __iter__(self):
            return iter(self.items)
    
    mock_github_instance = Mock()
    mock_github.return_value = mock_github_instance
    mock_search_results = [
        Mock(
            html_url='https://github.com/example/repo1',
            path='file1.py',
            repository=Mock(full_name='example/repo1'),
            decoded_content=b'print("Hello, World!")'
        ),
        Mock(
            html_url='https://github.com/example/repo2',
            path='file2.py',
            repository=Mock(full_name='example/repo2'),
            decoded_content=b'def main():\n    pass'
        )
    ]
    mock_search_results_paginated = MockPaginatedList(mock_search_results)
    mock_github_instance.search_code.return_value = mock_search_results_paginated
    
    result = commands.cmd_github_search("test query")
    
    mock_github_instance.search_code.assert_called_once_with(query="test query")
    assert isinstance(result, str)
    assert "example/repo1" in result
    assert "example/repo2" in result
    assert "file1.py" in result
    assert "file2.py" in result
    assert "https://github.com/example/repo1" in result
    assert "https://github.com/example/repo2" in result
    assert 'print("Hello, World!")' in result
    assert "def main():" in result
