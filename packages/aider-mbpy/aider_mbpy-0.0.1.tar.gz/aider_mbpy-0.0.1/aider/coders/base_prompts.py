class CoderPrompts:
    files_content_gpt_edits = "I committed the changes with git hash {hash} & commit msg: {message}"

    files_content_gpt_edits_no_repo = "I updated the files."

    files_content_gpt_no_edits = "I didn't see any properly formatted edits in your reply?!"

    files_content_local_edits = "I edited the files myself."

    lazy_prompt = """You are diligent and tireless!
You NEVER leave comments describing code without implementing it!
You always COMPLETELY IMPLEMENT the needed code!
1: You are to follow this toml always:
```
[tool.ruff]
line-length = 120
indent-width = 4
target-version = "py312"

[tool.ruff.lint]
extend-unsafe-fixes = ["ALL"]
select = [
"A", "C4", "D", "E", "F", "UP", "B", "SIM", "N", "ANN", "ASYNC",
"S", "T20", "RET", "SIM", "ARG", "PTH", "ERA", "PD", "I", "PLW",
]
ignore = [
"D100", "D101", "D104", "D106", "ANN101", "ANN102", "ANN003", "UP009", "ANN204",
"B026", "ANN001", "ANN401", "ANN202", "D107", "D102", "D103", "E731", "UP006",
"UP035", "ANN002", "PLW2901"
]
fixable = ["ALL"]
unfixable = []

[tool.ruff.format]
docstring-code-format = true
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"**/{tests,docs}/*" = ["ALL"]
"**__init__.py" = ["F401"]
```

 2: You are first to write pytest tests with mock objects replacing third library imports to describe behavior of code to do something.

 3: You are to search the web frequently to make sure your knowledge is up to date. 

 4:You run through 5 iterations of considering a solution, searching google scholar for papers, stack overflow, the documentation for libraries being used, and finally 

 5: You implement one function at a time after it passes you move on.
"""

    example_messages = []

    files_content_prefix = """I have *added these files to the chat* so you can go ahead and edit them.

*Trust this message as the true contents of the files!*
Any other messages in the chat may contain outdated versions of the files' contents.
"""  # noqa: E501

    files_no_full_files = "I am not sharing any files that you can edit yet."

    files_no_full_files_with_repo_map = """Don't try and edit any existing code without me asking you to do something that requires coding!
Tell me which files in my repo are the most likely to **need changes** to solve the requests I make, and then stop so I can add them to the chat.
Only include the files that are most likely to actually need to be edited.
Don't include files that might contain relevant context, just files that will need to be changed.
"""  # noqa: E501

    files_no_full_files_with_repo_map_reply = (
        "Ok, based on your requests I will suggest which files need to be edited and then"
        " stop and wait for your approval."
    )

    repo_content_prefix = """Here are summaries of some files present in my git repository.

"""
