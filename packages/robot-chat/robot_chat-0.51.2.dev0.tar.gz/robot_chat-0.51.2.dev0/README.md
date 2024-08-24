
<!-- Edit README.md, not index.md -->

# RobotChat is AI pair programming in your terminal for robots running Intel RealSense cameras and ROS2.

RobotChat (based on Aider) lets you pair program with LLMs,
to write and edit code in your local git repository.
Start a new project or work with an existing git repo.
RobotChat works best with GPT-4o & Claude 3.5 Sonnet and can
[connect to almost any LLM](https://aider.chat/docs/llms.html).

## Getting started

You can get started quickly like this:

```
$ pip install robot-chat

# Change directory into a git repo
cd /to/your/git/repo

# Work with Claude 3.5 Sonnet on your repo
$ export ANTHROPIC_API_KEY=your-key-goes-here
$ robotchat my-robot.py

# Work with GPT-4o on your repo
$ export OPENAI_API_KEY=your-key-goes-here
$ robotchat my-robot.py
```

See the
[installation instructions](https://aider.chat/docs/install.html)
and other
[documentation](https://aider.chat/docs/usage.html)
for more details.

## Features

- Run robotchat with the files you want to edit: `robotchat <file1> <file2> ...`
- `robotchat my-robot.py`
- Ask for changes:
  - Detect a person and their distance. Move the robot to the person. Stop when it reaches their feet.
  - `/run python3 my-robot.py`
  - If the resulting code, outputs a bug, simply add it to the chat by pressing "y" and RobotChat will attempt to fix the bug so you can re /run your app.
  - Add new features or test cases.
- RobotChat will edit your files to complete your request.
- RobotChat [automatically git commits](https://aider.chat/docs/git.html) changes with a sensible commit message.
- RobotChat works with [most popular languages](https://aider.chat/docs/languages.html): python, javascript, typescript, php, html, css, and more...
- RobotChat works best with GPT-4o & Claude 3.5 Sonnet and can [connect to almost any LLM](https://aider.chat/docs/llms.html).
- RobotChat can edit multiple files at once for complex requests.
- RobotChat uses a [map of your entire git repo](https://aider.chat/docs/repomap.html), which helps it work well in larger codebases.
- Edit files in your editor while chatting with aider, and it will always use the latest version.
