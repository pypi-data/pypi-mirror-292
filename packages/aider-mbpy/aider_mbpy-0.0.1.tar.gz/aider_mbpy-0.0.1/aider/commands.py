import difflib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import OrderedDict

import git
import pandas as pd
import plotly.express as px
from PyGithub import Github
from PyGithub import GithubException
from rich import print
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from aider import models, prompts, voice
from aider.help import Help, install_help_extra
from aider.inspecting import inspect_library
from aider.io import InputOutput
from aider.llm import litellm
from aider.scrape import Scraper
from aider.utils import is_image_file

from .dump import dump  # noqa: F401
from .test_automation import TestAutomation


class SwitchCoder(Exception):
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class Commands:
    voice = None

    def __init__(self, io, coder, voice_language=None, verify_ssl=True):
        self.io = io
        self.coder = coder

        self.verify_ssl = verify_ssl
        if voice_language == "auto":
            voice_language = None

        self.voice_language = voice_language

        self.help = None
        self.performance_data = []
        self.module_usage = {}
        self.inspect_library = inspect_library

    def cmd_model(self, args):
        "Switch to a new LLM"

        model_name = args.strip()
        model = models.Model(model_name)
        models.sanity_check_models(self.io, model)
        raise SwitchCoder(main_model=model)

    def cmd_chat_mode(self, args):
        "Switch to a new chat mode"

        from aider import coders

        ef = args.strip()
        valid_formats = OrderedDict(
            sorted(
                (
                    coder.edit_format,
                    coder.__doc__.strip().split("\n")[0] if coder.__doc__ else "No description",
                )
                for coder in coders.__all__
                if getattr(coder, "edit_format", None)
            )
        )

        show_formats = OrderedDict(
            [
                ("help", "Get help about using aider (usage, config, troubleshoot)."),
                ("ask", "Ask questions about your code without making any changes."),
                ("code", "Ask for changes to your code (using the best edit format)."),
            ]
        )

        if ef not in valid_formats and ef not in show_formats:
            if ef:
                self.io.tool_error(f'Chat mode "{ef}" should be one of these:\n')
            else:
                self.io.tool_output("Chat mode should be one of these:\n")

            max_format_length = max(len(format) for format in valid_formats.keys())
            for format, description in show_formats.items():
                self.io.tool_output(f"- {format:<{max_format_length}} : {description}")

            self.io.tool_output("\nOr a valid edit format:\n")
            for format, description in valid_formats.items():
                if format not in show_formats:
                    self.io.tool_output(f"- {format:<{max_format_length}} : {description}")

            return

        summarize_from_coder = True
        edit_format = ef

        if ef == "code":
            edit_format = self.coder.main_model.edit_format
            summarize_from_coder = False
        elif ef == "ask":
            summarize_from_coder = False

        raise SwitchCoder(
            edit_format=edit_format,
            summarize_from_coder=summarize_from_coder,
        )

    def completions_model(self):
        models = litellm.model_cost.keys()
        return models

    def cmd_models(self, args):
        "Search the list of available models"

        args = args.strip()

        if args:
            models.print_matching_models(self.io, args)
        else:
            self.io.tool_output("Please provide a partial model name to search for.")

    def cmd_web(self, args):
        "Search the web and display results"
        from msearch.search import search_web  # type: ignore
        return search_web(args)


    def _scrape_url(self, url):
        if not self.scraper:
            self.scraper = Scraper(
                print_error=self.io.tool_error, verify_ssl=self.verify_ssl
            )

    def is_command(self, inp):
        return True

    def get_completions(self, cmd):

        fun = getattr(self, f"completions_{cmd}", None)
        if not fun:
            return
        return sorted(fun())

    def get_commands(self):
        commands = []
        for attr in dir(self):
            if not attr.startswith("cmd_"):
                continue
            cmd = attr[4:]
            cmd = cmd.replace("_", "-")
            commands.append("/" + cmd)

        return commands

    def cmd_show_context(self, args):
        "Run the terminal 'ls' command"
        result = self.cmd_run("ls " + args)
        if result:
            from rich.console import Console
            from rich.table import Table

            console = Console()
            table = Table(show_header=False, box=None)
            for item in result.split():
                table.add_row(item)
            console.print(table)
        return result

    def do_run(self, cmd_name, args):
        cmd_name = cmd_name.replace("-", "_")
        cmd_method_name = f"cmd_{cmd_name}"
        cmd_method = getattr(self, cmd_method_name, None)
        if cmd_method:
            return cmd_method(args)
        else:
            self.io.tool_output(f"Error: Command {cmd_name} not found.")

    def matching_commands(self, inp):
        words = inp.strip().split()
        if not words:
            return

        first_word = words[0]
        rest_inp = inp[len(words[0]) :]

        all_commands = self.get_commands()
        matching_commands = [cmd for cmd in all_commands if cmd.startswith(first_word)]
        return matching_commands, first_word, rest_inp

    def run(self, inp):
        try:
            # Step 1: Check if the input is a command (with or without slash)
            command = inp.lstrip('/!')
            cmd_method_name = f"cmd_{command.split()[0]}"
            cmd_method = getattr(self, cmd_method_name, None)
            
            if cmd_method:
                args = ' '.join(command.split()[1:])
                return cmd_method(args)

            # Step 2: Try to automatch to a command
            res = self.matching_commands(inp)
            if res is not None:
                matching_commands, first_word, rest_inp = res
                if len(matching_commands) == 1:
                    return self.do_run(matching_commands[0][1:], rest_inp)
                elif first_word in matching_commands:
                    return self.do_run(first_word[1:], rest_inp)
                elif len(matching_commands) > 1:
                    self.io.tool_error(f"Ambiguous command: {', '.join(matching_commands)}")
                    return None

            # Step 3: Try running as a shell command
            try:
                result = self.do_run("run", inp)
                if result:
                    return result
            except Exception:
                pass

            # Step 4: Query the LLM
            return inp
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except SyntaxError:
            self.io.tool_error("Invalid syntax. Please check your input.")
            return None
        except FileNotFoundError:
            self.io.tool_error("Command or file not found. Please check your input.")
            return None

    def string_similarity(self, a, b):
        return difflib.SequenceMatcher(None, a, b).ratio()

    # any method called cmd_xxx becomes a command automatically.
    # each one must take an args param.

    def cmd_commit(self, args=None):
        "Commit edits to the repo made outside the chat (commit message optional)"

        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        if not self.coder.repo.is_dirty():
            self.io.tool_error("No more changes to commit.")
            return

        commit_message = args.strip() if args else None
        self.coder.repo.commit(message=commit_message)

    def cmd_lint(self, args="", fnames=None):
        "Lint and fix provided files or in-chat files if none provided"

        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        if not fnames:
            fnames = self.coder.get_inchat_relative_files()

        # If still no files, get all dirty files in the repo
        if not fnames and self.coder.repo:
            fnames = self.coder.repo.get_dirty_files()

        if not fnames:
            self.io.tool_error("No dirty files to lint.")
            return

        fnames = [self.coder.abs_root_path(fname) for fname in fnames]

        lint_coder = None
        for fname in fnames:
            try:
                errors = self.coder.linter.lint(fname)
            except FileNotFoundError as err:
                self.io.tool_error(f"Unable to lint {fname}")
                self.io.tool_error(str(err))
                continue

            if not errors:
                continue

            self.io.tool_error(errors)
            if not self.io.confirm_ask(f"Fix lint errors in {fname}?", default="y"):
                continue

            # Commit everything before we start fixing lint errors
            if self.coder.repo.is_dirty():
                self.cmd_commit("")

            if not lint_coder:
                lint_coder = self.coder.clone(
                    # Clear the chat history, fnames
                    cur_messages=[],
                    done_messages=[],
                    fnames=None,
                )

            lint_coder.add_rel_fname(fname)
            lint_coder.run(errors)
            lint_coder.abs_fnames = set()

        if lint_coder and self.coder.repo.is_dirty():
            self.cmd_commit("")

    def cmd_clear(self, args):
        "Clear the chat history"

        self._clear_chat_history()

    def _drop_all_files(self):
        self.coder.abs_fnames = set()
        self.coder.abs_read_only_fnames = set()

    def _clear_chat_history(self):
        self.coder.done_messages = []
        self.coder.cur_messages = []

    def cmd_tokens(self, args):
        """Report on the number of tokens used by the current chat context."""
        res = []

        self.coder.choose_fence()

        # system messages
        main_sys = self.coder.fmt_system_prompt(self.coder.gpt_prompts.main_system)
        main_sys += "\n" + self.coder.fmt_system_prompt(self.coder.gpt_prompts.system_reminder)
        msgs = [
            dict(role="system", content=main_sys),
            dict(
                role="system",
                content=self.coder.fmt_system_prompt(self.coder.gpt_prompts.system_reminder),
            ),
        ]

        tokens = self.coder.main_model.token_count(msgs)
        res.append((tokens, "system messages", ""))

        # chat history
        msgs = self.coder.done_messages + self.coder.cur_messages
        if msgs:
            tokens = self.coder.main_model.token_count(msgs)
            res.append((tokens, "chat history", "use /clear to clear"))

        # repo map
        other_files = set(self.coder.get_all_abs_files()) - set(self.coder.abs_fnames)
        if self.coder.repo_map:
            repo_content = self.coder.repo_map.get_repo_map(self.coder.abs_fnames, other_files)
            if repo_content:
                tokens = self.coder.main_model.token_count(repo_content)
                res.append((tokens, "repository map", "use --map-tokens to resize"))

        fence = "`" * 3

        # files
        for fname in self.coder.abs_fnames:
            relative_fname = self.coder.get_rel_fname(fname)
            content = self.io.read_text(fname)
            if is_image_file(relative_fname):
                tokens = self.coder.main_model.token_count_for_image(fname)
            else:
                # approximate
                content = f"{relative_fname}\n{fence}\n" + content + "{fence}\n"
                tokens = self.coder.main_model.token_count(content)
            res.append((tokens, f"{relative_fname}", "/drop to remove"))

        # read-only files
        for fname in self.coder.abs_read_only_fnames:
            relative_fname = self.coder.get_rel_fname(fname)
            content = self.io.read_text(fname)
            if content is not None and not is_image_file(relative_fname):
                # approximate
                content = f"{relative_fname}\n{fence}\n" + content + "{fence}\n"
                tokens = self.coder.main_model.token_count(content)
                res.append((tokens, f"{relative_fname} (read-only)", "/drop to remove"))

        self.io.tool_output("Approximate context window usage, in tokens:")
        self.io.tool_output()

        width = 8
        cost_width = 9

        def fmt(v):
            return format(int(v), ",").rjust(width)

        col_width = max(len(row[1]) for row in res)

        cost_pad = " " * cost_width
        total = 0
        total_cost = 0.0
        for tk, msg, tip in res:
            total += tk
            cost = tk * self.coder.main_model.info.get("input_cost_per_token", 0)
            total_cost += cost
            msg = msg.ljust(col_width)
            self.io.tool_output(f"${cost:7.4f} {fmt(tk)} {msg} {tip}")  # noqa: E231

        self.io.tool_output("=" * (width + cost_width + 1))
        self.io.tool_output(f"${total_cost:7.4f} {fmt(total)} tokens total")  # noqa: E231

        limit = self.coder.main_model.info.get("max_input_tokens", 0)
        if not limit:
            return

        remaining = limit - total
        if remaining > 1024:
            self.io.tool_output(f"{cost_pad}{fmt(remaining)} tokens remaining in context window")
        elif remaining > 0:
            self.io.tool_error(
                f"{cost_pad}{fmt(remaining)} tokens remaining in context window (use /drop or"
                " /clear to make space)"
            )
        else:
            self.io.tool_error(
                f"{cost_pad}{fmt(remaining)} tokens remaining, window exhausted (use /drop or"
                " /clear to make space)"
            )
        self.io.tool_output(f"{cost_pad}{fmt(limit)} tokens max context window size")

    def cmd_undo(self, args):  # noqa: ANN201
        "Undo the last git commit if it was done by aider"
        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        last_commit = self.coder.repo.repo.head.commit
        if not last_commit.parents:
            self.io.tool_error("This is the first commit in the repository. Cannot undo.")
            return

        prev_commit = last_commit.parents[0]
        changed_files_last_commit = [item.a_path for item in last_commit.diff(prev_commit)]

        for fname in changed_files_last_commit:
            if self.coder.repo.repo.is_dirty(path=fname):
                self.io.tool_error(
                    f"The file {fname} has uncommitted changes. Please stash them before undoing."
                )
                return

            # Check if the file was in the repo in the previous commit
            try:
                prev_commit.tree[fname]
            except KeyError:
                self.io.tool_error(
                    f"The file {fname} was not in the repository in the previous commit. Cannot"
                    " undo safely."
                )
                return

        local_head = self.coder.repo.repo.git.rev_parse("HEAD")
        current_branch = self.coder.repo.repo.active_branch.name
        try:
            remote_head = self.coder.repo.repo.git.rev_parse(f"origin/{current_branch}")
            has_origin = True
        except git.exc.GitCommandError:
            has_origin = False

        if has_origin:
            if local_head == remote_head:
                self.io.tool_error(
                    "The last commit has already been pushed to the origin. Undoing is not"
                    " possible."
                )
                return

        last_commit_hash = self.coder.repo.repo.head.commit.hexsha[:7]
        last_commit_message = self.coder.repo.repo.head.commit.message.strip()
        if last_commit_hash not in self.coder.aider_commit_hashes:
            self.io.tool_error("The last commit was not made by aider in this chat session.")
            self.io.tool_error(
                "You could try `/git reset --hard HEAD^` but be aware that this is a destructive"
                " command!"
            )
            return

        # Reset only the files which are part of `last_commit`
        for file_path in changed_files_last_commit:
            self.coder.repo.repo.git.checkout("HEAD~1", file_path)

        # Move the HEAD back before the latest commit
        self.coder.repo.repo.git.reset("--soft", "HEAD~1")

        self.io.tool_output(f"Removed: {last_commit_hash} {last_commit_message}")

        # Get the current HEAD after undo
        current_head_hash = self.coder.repo.repo.head.commit.hexsha[:7]
        current_head_message = self.coder.repo.repo.head.commit.message.strip()
        self.io.tool_output(f"Now at:  {current_head_hash} {current_head_message}")

        if self.coder.main_model.send_undo_reply:
            return prompts.undo_command_reply

    def cmd_diff(self, args=""):
        "Display the diff of changes since the last message"
        if not self.coder.repo:
            self.io.tool_error("No git repository found.")
            return

        current_head = self.coder.repo.get_head()
        if current_head is None:
            self.io.tool_error("Unable to get current commit. The repository might be empty.")
            return

        if len(self.coder.commit_before_message) < 2:
            commit_before_message = current_head + "^"
        else:
            commit_before_message = self.coder.commit_before_message[-2]

        if not commit_before_message or commit_before_message == current_head:
            self.io.tool_error("No changes to display since the last message.")
            return

        self.io.tool_output(f"Diff since {commit_before_message[:7]}...")

        diff = self.coder.repo.diff_commits(
            self.coder.pretty,
            commit_before_message,
            "HEAD",
        )

        # don't use io.tool_output() because we don't want to log or further colorize
        print(diff)

    def quote_fname(self, fname):
        if " " in fname and '"' not in fname:
            fname = f'"{fname}"'
        return fname

    def completions_read(self):
        return self.completions_add()

    def completions_add(self):
        files = set(self.coder.get_all_relative_files())
        files = files - set(self.coder.get_inchat_relative_files())
        files = [self.quote_fname(fn) for fn in files]
        return files

    def glob_filtered_to_repo(self, pattern):
        try:
            if os.path.isabs(pattern):
                # Handle absolute paths
                raw_matched_files = [Path(pattern)]
            else:
                raw_matched_files = list(Path(self.coder.root).glob(pattern))
        except ValueError as err:
            self.io.tool_error(f"Error matching {pattern}: {err}")
            raw_matched_files = []

        matched_files = []
        for fn in raw_matched_files:
            matched_files += expand_subdir(fn)

        matched_files = [
            str(Path(fn).relative_to(self.coder.root))
            for fn in matched_files
            if Path(fn).is_relative_to(self.coder.root)
        ]

        # if repo, filter against it
        if self.coder.repo:
            git_files = self.coder.repo.get_tracked_files()
            matched_files = [fn for fn in matched_files if str(fn) in git_files]

        res = list(map(str, matched_files))
        return res

    def cmd_add(self, args):
        "Add files to the chat so GPT can edit them or review them in detail"

        added_fnames = []

        all_matched_files = set()

        filenames = parse_quoted_filenames(args)
        for word in filenames:
            fname = Path(word) if Path(word).is_absolute() else Path(self.coder.root) / word

            if self.coder.repo and self.coder.repo.ignored_file(fname):
                self.io.tool_error(f"Skipping {fname} that matches aiderignore spec.")
                continue

            if fname.exists():
                if fname.is_file():
                    all_matched_files.add(str(fname))
                    continue
                # an existing dir, escape any special chars so they won't be globs
                word = re.sub(r"([\*\?\[\]])", r"[\1]", word)

            matched_files = self.glob_filtered_to_repo(word)
            if matched_files:
                all_matched_files.update(matched_files)
                continue

            if self.io.confirm_ask(f"No files matched '{word}'. Do you want to create {fname}?"):
                if fname.is_dir():
                    for f in fname.glob("*.py"):
                        if f.is_file():
                            all_matched_files.add(str(f))
                    for f in fname.glob("*.md"):
                        if f.is_file():
                            all_matched_files.add(str(f))
                # if "*" in str(fname) or "?" in str(fname):
                #     self.io.tool_error(f"Cannot create file with wildcard characters: {fname}")
                else:
                    try:
                        fname.touch()
                        all_matched_files.add(str(fname))
                    except OSError as e:
                        self.io.tool_error(f"Error creating file {fname}: {e}")

        for matched_file in all_matched_files:
            abs_file_path = self.coder.abs_root_path(matched_file)

            if not abs_file_path.startswith(self.coder.root) and not is_image_file(matched_file):
                self.io.tool_error(
                    f"Can not add {abs_file_path}, which is not within {self.coder.root}"
                )
                continue

            if abs_file_path in self.coder.abs_fnames:
                self.io.tool_error(f"{matched_file} is already in the chat")
            else:
                if is_image_file(matched_file) and not self.coder.main_model.accepts_images:
                    self.io.tool_error(
                        f"Cannot add image file {matched_file} as the"
                        f" {self.coder.main_model.name} does not support image.\nYou can run `aider"
                        " --4-turbo-vision` to use GPT-4 Turbo with Vision."
                    )
                    continue
                content = self.io.read_text(abs_file_path)
                if content is None:
                    self.io.tool_error(f"Unable to read {matched_file}")
                else:
                    self.coder.abs_fnames.add(abs_file_path)
                    self.io.tool_output(f"Added {matched_file} to the chat")
                    self.coder.check_added_files()
                    added_fnames.append(matched_file)

    def completions_drop(self):
        files = self.coder.get_inchat_relative_files()
        read_only_files = [self.coder.get_rel_fname(fn) for fn in self.coder.abs_read_only_fnames]
        all_files = files + read_only_files
        all_files = [self.quote_fname(fn) for fn in all_files]
        return all_files

    def cmd_drop(self, args=""):
        "Remove files from the chat session to free up context space"

        if not args.strip():
            self.io.tool_output("Dropping all files from the chat session.")
            self._drop_all_files()
            return

        filenames = parse_quoted_filenames(args)
        for word in filenames:
            # Expand tilde in the path
            expanded_word = os.path.expanduser(word)

            # Handle read-only files separately, without glob_filtered_to_repo
            read_only_matched = [f for f in self.coder.abs_read_only_fnames if expanded_word in f]

            if read_only_matched:
                for matched_file in read_only_matched:
                    self.coder.abs_read_only_fnames.remove(matched_file)
                    self.io.tool_output(f"Removed read-only file {matched_file} from the chat")

            matched_files = self.glob_filtered_to_repo(expanded_word)

            if not matched_files:
                matched_files.append(expanded_word)

            for matched_file in matched_files:
                abs_fname = self.coder.abs_root_path(matched_file)
                if abs_fname in self.coder.abs_fnames:
                    self.coder.abs_fnames.remove(abs_fname)
                    self.io.tool_output(f"Removed {matched_file} from the chat")

    def cmd_git(self, args):
        "Run a git command"
        combined_output = None
        try:
            args = "git " + args
            env = dict(subprocess.os.environ)
            env["GIT_EDITOR"] = "true"
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                shell=True,
                encoding=self.io.encoding,
                errors="replace",
            )
            combined_output = result.stdout
        except Exception as e:
            self.io.tool_error(f"Error running /git command: {e}")

        if combined_output is None:
            return

        self.io.tool_output(combined_output)

    def cmd_test(self, args):
        "Run a shell command and add the output to the chat on non-zero exit code"
        if not args and self.coder.test_cmd:
            args = self.coder.test_cmd

        if not callable(args):
            return self.cmd_run(args, True)

        errors = args()
        if not errors:
            return

        self.io.tool_error(errors, strip=False)
        return errors

    def cmd_run(self, args, add_on_nonzero_exit=False):
        "Run a shell command and optionally add the output to the chat (alias: !)"
        combined_output = None
        instructions = None
        print(f"running command: {args}")
        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                encoding=self.io.encoding,
                errors="replace",
            )
            combined_output = result.stdout
        except Exception as e:
            self.io.tool_error(f"Error running command: {e}")

        if combined_output is None:
            return

        self.io.tool_output(combined_output)

        if add_on_nonzero_exit:
            add = result.returncode != 0
        else:
            response = self.io.prompt_ask(
                "Add the output to the chat?\n[Y/n/instructions]",
            ).strip()

            if response.lower() in ["yes", "y"]:
                add = True
            elif response.lower() in ["no", "n"]:
                add = False
            else:
                add = True
                instructions = response

        if add:
            for line in combined_output.splitlines():
                self.io.tool_output(line, log_only=True)

            msg = prompts.run_output.format(
                command=args,
                output=combined_output,
            )

            if instructions:
                msg = instructions + "\n\n" + msg

            return msg
        return None

    def cmd_exit(self, args):
        "Exit the application"
        sys.exit()

    def cmd_quit(self, args):
        "Exit the application"
        sys.exit()

    def cmd_show_context(self, args):
        "List all known files and indicate which are included in the chat session"

        files = self.coder.get_all_relative_files()

        other_files = []
        chat_files = []
        for file in files:
            abs_file_path = self.coder.abs_root_path(file)
            if abs_file_path in self.coder.abs_fnames:
                chat_files.append(file)
            else:
                other_files.append(file)

        if not chat_files and not other_files:
            self.io.tool_output("\nNo files in chat or git repo.")
            return

        if other_files:
            self.io.tool_output("Repo files not in the chat:\n")
        for file in other_files:
            self.io.tool_output(f"  {file}")
        read_only_files = []
        if read_only_files:
            self.io.tool_output("\nRead-only files:\n")
        for file in read_only_files:
            self.io.tool_output(f"  {file}")

        if chat_files:
            self.io.tool_output("\nFiles in chat:\n")
        for file in chat_files:
            self.io.tool_output(f"  {file}")

    def basic_help(self):
        commands = sorted(self.get_commands())
        pad = max(len(cmd) for cmd in commands)
        pad = "{cmd:" + str(pad) + "}"
        for cmd in commands:
            cmd_method_name = f"cmd_{cmd[1:]}".replace("-", "_")
            cmd_method = getattr(self, cmd_method_name, None)
            cmd = pad.format(cmd=cmd)
            if cmd_method:
                description = cmd_method.__doc__
                self.io.tool_output(f"{cmd} {description}\n```\n{cmd} {description}\n```")
            else:
                self.io.tool_output(f"{cmd} No description available.\n```\n{cmd} No description available.\n```")
        self.io.tool_output()
        self.io.tool_output("Use `/help <question>` to ask questions about how to use aider.")

    def cmd_help(self, args):
        """Ask questions about aider."""
        if not args.strip():
            self.basic_help()
            return

        from aider.coders import Coder

        if not self.help:
            res = install_help_extra(self.io)
            if not res:
                self.io.tool_error("Unable to initialize interactive help.")
                return

            self.help = Help()

        coder = Coder.create(
            io=self.io,
            from_coder=self.coder,
            edit_format="help",
            summarize_from_coder=False,
            map_tokens=512,
            map_mul_no_files=1,
        )
        user_msg = self.help.ask(args)
        user_msg += """
# Announcement lines from when this session of aider was launched:

"""
        user_msg += "\n".join(self.coder.get_announcements()) + "\n"

        coder.run(user_msg, preproc=False)

        if self.coder.repo_map:
            map_tokens = self.coder.repo_map.max_map_tokens
            map_mul_no_files = self.coder.repo_map.map_mul_no_files
        else:
            map_tokens = 0
            map_mul_no_files = 1

        raise SwitchCoder(
            edit_format=self.coder.edit_format,
            summarize_from_coder=False,
            from_coder=coder,
            map_tokens=map_tokens,
            map_mul_no_files=map_mul_no_files,
            show_announcements=False,
        )

    def clone(self):
        return Commands(
            self.io,
            None,
            voice_language=self.voice_language,
            verify_ssl=self.verify_ssl,
        )

    def cmd_ask(self, args):
        "Ask questions about the code base without editing any files"
        return self._generic_chat_command(args, "ask")

    def cmd_code(self, args):
        "Ask for changes to your code"
        return self._generic_chat_command(args, self.coder.main_model.edit_format)

    def _generic_chat_command(self, args, edit_format):
        if not args.strip():
            self.io.tool_error(f"Please provide a question or topic for the {edit_format} chat.")
            return

        from aider.coders import Coder

        coder = Coder.create(
            io=self.io,
            from_coder=self.coder,
            edit_format=edit_format,
            summarize_from_coder=False,
        )

        user_msg = args
        coder.run(user_msg)

        raise SwitchCoder(
            edit_format=self.coder.edit_format,
            summarize_from_coder=False,
            from_coder=coder,
            show_announcements=False,
        )

    def get_help_md(self):
        "Show help about all commands in markdown"

        res = """
|Command|Description|
|:------|:----------|
"""
        commands = sorted(self.get_commands())
        for cmd in commands:
            cmd_method_name = f"cmd_{cmd[1:]}"
            cmd_method = getattr(self, cmd_method_name, None)
            if cmd_method:
                description = cmd_method.__doc__
                res += f"| **{cmd}** | {description} |\n"
            else:
                res += f"| **{cmd}** | |\n"

        res += "\n"
        return res

    def cmd_voice(self, args):
        "Record and transcribe voice input"

        if not self.voice:
            if "OPENAI_API_KEY" not in os.environ:
                self.io.tool_error("To use /voice you must provide an OpenAI API key.")
                return
            try:
                self.voice = voice.Voice()
            except voice.SoundDeviceError:
                self.io.tool_error(
                    "Unable to import `sounddevice` and/or `soundfile`, is portaudio installed?"
                )
                return

        history_iter = self.io.get_input_history()

        history = []
        size = 0
        for line in history_iter:
            if line.startswith("/"):
                continue
            if line in history:
                continue
            if size + len(line) > 1024:
                break
            size += len(line)
            history.append(line)

        history.reverse()
        history = "\n".join(history)

        try:
            text = self.voice.record_and_transcribe(history, language=self.voice_language)
        except litellm.OpenAIError as err:
            self.io.tool_error(f"Unable to use OpenAI whisper model: {err}")
            return

        if text:
            self.io.add_to_input_history(text)
            print()
            self.io.user_input(text, log_only=False)
            print()

        return text

    def cmd_performance(self, args):
        """Display performance data and visualizations."""
        df = pd.DataFrame(self.performance_data)
        
        # Create histogram
        fig = px.histogram(df, x="execution_time", nbins=20, title="Execution Time Distribution")
        fig.show()
        
        # Display summary statistics
        print("[bold]Performance Data Summary:[/bold]")
        
        # Display module usage
        module_df = pd.DataFrame.from_dict(self.module_usage, orient='index', columns=['count'])
        module_df = module_df.sort_values('count', ascending=False)
        print("\n[bold]Module Usage:[/bold]")

    def cmd_inspect(self, args):
        "Inspect a function or module using the inspect_library and optionally add the output to the chat"
        if not args:
            self.io.tool_error("Please provide a function or module name to inspect.")
            return

        name = args.strip()
        depth = 0 # Default depth
        signatures = True
        docs = False
        code = False
        imports = False
        all = False
        # Parse additional arguments
        parts = name.split()
        if len(parts) > 1:
            name = parts[0]
            for part in parts[1:]:
                if part.startswith('depth='):
                    try:
                        depth = int(part.split('=')[1])
                    except ValueError:
                        self.io.tool_error(f"Invalid depth value: {part}")
                elif part == 'sigs':
                    signatures = True
                elif part == 'docs':
                    docs = True
                elif part == 'code':
                    code = True
                elif part == 'imports':
                    imports = True
        if "all" in name:
            name = name.replace("all", "")
            signatures = True
            docs = True
            code = True
            imports = True
            all = True

        output = self.inspect_library(name, depth, signatures, docs, code, all=all)

        # Display the output
        for line in output:
            self.io.tool_output(line)

        # Ask if the user wants to add the output to the chat
        if self.io.confirm_ask("Add the inspection output to the chat?", default="y"):
            msg = prompts.run_output.format(
                command=f"/inspect {args}",
                output="\n".join(output),
            )
            return msg
        return None


    def cmd_automate_testing(self, args):
        """Automate testing for a given function."""
        if not args:
            self.io.tool_error("Please provide a function name.")
            return

        function_name = args.strip()
        automation = TestAutomation(self.coder)
        result = automation.automate_testing(function_name)
        self.io.tool_output(f"Test automation result: {'Success' if result else 'Failure'}")

        # Add the test result to the chat
        if result:
            return f"Automated testing for '{function_name}' was successful."
        else:
            return f"Automated testing for '{function_name}' failed. Please review the generated tests and refactor the code if necessary."

    # def cmd_run_vllm_tests(self, args):
    #     """Run vLLM server tests."""
    #     self.io.tool_output("Running vLLM server tests...")
    #     automation = TestAutomation(self.coder)
    #     result = automation.run_vllm_tests()
    #     if result:
    #         return "All vLLM server tests passed successfully!"
    #     else:
    #         return "vLLM server tests failed. Please check the output for more details."

    def cmd_github_search(self, args):
        """
        Search GitHub and browse results in the terminal.
        Usage: /github_search [repo:owner/name] [user:username] [language:lang] [filename:name] search_term
        """
        if Github is None:
            self.io.tool_error("The 'github' module is not installed. Please install it using: pip install PyGithub")
            return

        try:
            # Get the GitHub token from git config
            try:
                repo = git.Repo(self.coder.root)
                token = repo.git.config('--get', 'github.token')
            except (git.exc.InvalidGitRepositoryError, git.exc.GitCommandError):
                self.io.tool_error("Failed to retrieve GitHub token from git config.")
                self.io.tool_error("Please set your GitHub token using: git config --global github.token YOUR_TOKEN")
                self.io.tool_error("If you don't have a token, create one at https://github.com/settings/tokens")
                return

            if not token:
                self.io.tool_error("GitHub token not found in git config.")
                self.io.tool_error("Please set your GitHub token using: git config --global github.token YOUR_TOKEN")
                self.io.tool_error("If you don't have a token, create one at https://github.com/settings/tokens")
                return

            # Create a Github instance
            g = Github(token)

            query = args.strip()
            if not query:
                self.io.tool_error("Please provide a search term.")
                return

            # Perform the search
            try:
                results = g.search_code(query)

                from rich.console import Console
                from rich.table import Table
                from rich.panel import Panel
                from rich.syntax import Syntax

                console = Console()

                page_size = 5
                page = 1
                total_results = results.totalCount

                while True:
                    start_idx = (page - 1) * page_size
                    end_idx = start_idx + page_size

                    table = Table(title=f"Search Results for: {query} (Page {page}/{(total_results + page_size - 1) // page_size})")
                    table.add_column("File", style="cyan")
                    table.add_column("Repository", style="magenta")
                    table.add_column("URL", style="blue")

                    for item in list(results)[start_idx:end_idx]:
                        table.add_row(item.name, item.repository.full_name, item.html_url)

                    console.print(table)

                    choice = self.io.prompt("Enter file number to view, 'n' for next page, 'p' for previous page, or 'q' to quit: ")

                    if choice.lower() == 'q':
                        break
                    elif choice.lower() == 'n':
                        if end_idx < total_results:
                            page += 1
                        else:
                            self.io.tool_output("No more results.")
                    elif choice.lower() == 'p':
                        if page > 1:
                            page -= 1
                        else:
                            self.io.tool_output("Already on the first page.")
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < min(page_size, end_idx - start_idx):
                            item = list(results)[start_idx + idx]
                            try:
                                content = item.decoded_content.decode('utf-8')
                                syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
                                console.print(Panel(syntax, title=f"Content of {item.path}", expand=False))
                            except Exception as content_error:
                                self.io.tool_error(f"Error fetching content: {str(content_error)}")
                        else:
                            self.io.tool_error("Invalid file number.")
                return f"GitHub search completed for query: {query}"

            except GithubException as github_error:
                self.io.tool_error(f"GitHub API error: {github_error}")
            except Exception as e:
                self.io.tool_error(f"An error occurred while searching GitHub: {str(e)}")

        except Exception as e:
            self.io.tool_error(f"An error occurred: {str(e)}")

        return None

    def cmd_browse_github(self, args):
        """
        Browse a GitHub repository in the terminal.
        Usage: /browse_github owner/repo [path]
        """
        if Github is None:
            self.io.tool_error("The 'github' module is not installed. Please install it using: pip install PyGithub")
            return

        parts = args.split()
        if len(parts) < 1:
            self.io.tool_error("Please provide a repository name (owner/repo).")
            return

        repo_name = parts[0]
        path = parts[1] if len(parts) > 1 else ""

        try:
            g = Github()  # This will use the GITHUB_TOKEN environment variable
            github_repo = g.get_repo(repo_name)

            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.syntax import Syntax
            from rich.prompt import Prompt

            console = Console()

            def display_contents(path):
                contents = github_repo.get_contents(path)
                table = Table(title=f"Contents of {repo_name}/{path}")
                table.add_column("Index", style="cyan")
                table.add_column("Type", style="magenta")
                table.add_column("Name", style="green")
                table.add_column("Size", style="yellow")

                if isinstance(contents, list):
                    for idx, item in enumerate(contents, start=1):
                        table.add_row(
                            str(idx),
                            "DIR" if item.type == 'dir' else "FILE",
                            item.name,
                            str(item.size) if item.type != 'dir' else ""
                        )
                else:
                    table.add_row("1", "FILE", contents.name, str(contents.size))

                console.print(table)

                return contents

            browsing_results = []

            while True:
                contents = display_contents(path)
                browsing_results.append(f"Contents of {repo_name}/{path}")

                if isinstance(contents, list):
                    choice = Prompt.ask(
                        "Enter item number to view/expand, '..' to go up, or 'q' to quit",
                        default="q"
                    )
                    if choice.lower() == 'q':
                        break
                    elif choice == '..':
                        path = '/'.join(path.split('/')[:-1])
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(contents):
                            item = contents[idx]
                            if item.type == 'dir':
                                path = item.path
                            else:
                                content = item.decoded_content.decode('utf-8')
                                syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
                                console.print(Panel(syntax, title=f"Content of {item.path}", expand=False))
                                browsing_results.append(f"Content of {item.path}:\n{content}")
                                input("Press Enter to continue...")
                        else:
                            self.io.tool_error("Invalid item number.")
                else:
                    content = contents.decoded_content.decode('utf-8')
                    syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
                    console.print(Panel(syntax, title=f"Content of {contents.path}", expand=False))
                    browsing_results.append(f"Content of {contents.path}:\n{content}")
                    input("Press Enter to continue...")
                    path = '/'.join(path.split('/')[:-1])  # Go back to parent directory

            # Ask if the user wants to save the results
            if self.io.confirm_ask("Do you want to save the browsing results?", default="n"):
                # Save to chat history
                browsing_summary = "\n\n".join(browsing_results)
                self.io.append_chat_history(f"GitHub browsing results for {repo_name}:\n\n{browsing_summary}")
                self.io.tool_output("Browsing results saved to chat history.")

                # Save to file
                filename = f"github_browse_{repo_name.replace('/', '_')}.txt"
                with open(filename, 'w') as f:
                    f.write("\n\n".join(browsing_results))
                self.io.tool_output(f"Results saved to {filename}")

                return f"Finished browsing GitHub repository {repo_name}. Results saved to chat and file {filename}."
            else:
                return f"Finished browsing GitHub repository {repo_name}. Results were not saved."

        except GithubException as github_error:
            self.io.tool_error(f"GitHub API error: {github_error}")
        except Exception as e:
            self.io.tool_error(f"An error occurred while browsing GitHub: {str(e)}")

        return None

    def cmd_list_remote(self, args):
        """
        List the contents of a remote repository.
        Usage: /list_remote <repository-url>
        """
        if not args:
            self.io.tool_error("Please provide a repository URL.")
            return

        repo_url = args.strip()
        try:
            result = subprocess.run(['git', 'ls-remote', '--heads', repo_url], 
                                    capture_output=True, text=True, check=True)
            self.io.tool_output("Remote repository contents:")
            self.io.tool_output(result.stdout)
            return f"Listed contents of remote repository: {repo_url}"
        except subprocess.CalledProcessError as e:
            self.io.tool_error(f"Error listing remote repository: {e}")
            self.io.tool_error(f"Git output: {e.stderr}")
        except Exception as e:
            self.io.tool_error(f"An unexpected error occurred: {str(e)}")
        
        return None

    def cmd_show_prompts(self, args):
        """
        Show all the prompts used in Aider.
        Usage: /show_prompts
        """
        from aider import prompts

        self.io.tool_output("Prompts used in Aider:")
        for attr_name in dir(prompts):
            if not attr_name.startswith('__'):
                prompt_value = getattr(prompts, attr_name)
                if isinstance(prompt_value, str):
                    self.io.tool_output(f"\n{attr_name}:")
                    self.io.tool_output(prompt_value)

        return "Displayed all prompts used in Aider."

    def cmd_show_prompts_formatted(self, args):
        """Show all the prompts used in Aider with improved formatting.
        Usage: /show_prompts_formatted.
        """  # noqa: D205
        from aider import prompts
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text

        console = Console()
        console.print("[bold]Prompts used in Aider:[/bold]\n")

        for attr_name in dir(prompts):
            if not attr_name.startswith('__'):
                prompt_value = getattr(prompts, attr_name)
                if isinstance(prompt_value, str):
                    title = Text(attr_name, style="cyan")
                    content = Text(prompt_value, style="green")
                    panel = Panel(content, title=title, expand=False, border_style="blue")
                    console.print(panel)
                    console.print()  # Add a blank line between prompts

        return "Displayed all prompts used in Aider with improved formatting."

def expand_subdir(file_path):
    file_path = Path(file_path)
    if file_path.is_file():
        yield file_path
        return

    if file_path.is_dir():
        for file in file_path.rglob("*"):
            if file.is_file():
                yield str(file)


def parse_quoted_filenames(args):
    filenames = re.findall(r"\"(.+?)\"|(\S+)", args)
    filenames = [name for sublist in filenames for name in sublist if name]
    return filenames


def get_help_md():
    from aider.coders import Coder
    from aider.models import Model

    coder = Coder(Model("gpt-3.5-turbo"), None)
    md = coder.commands.get_help_md()
    return md


def main():
    md = get_help_md()
    print(md)


if __name__ == "__main__":
    status = main()
    sys.exit(status)