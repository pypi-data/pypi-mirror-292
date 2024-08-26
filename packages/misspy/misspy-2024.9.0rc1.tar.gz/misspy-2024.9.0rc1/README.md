# misspy
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
> [!WARNING]
> It is in the development phase and very many features are missing. Do not use in a production environment.
<!--Streaming is not available because misspy-rewrite has a bug related to [#xxx](https://github.com/misskey-dev/misskey/issues/xxx). issuesは準備中-->

Fast, asynchronous misskey API framework.

misspy (rewrite) is a framework for writing Misskey bots with Discord.py-like syntax.
### Features✨
- asynchronous
- Fast
- Automatic detection of Misskey version (can also be set manually)
- Discord.py-like syntax

### Install
#### Latest Develop Release
```
$ pip install git+https://github.com/misspy-dev/misspy-rewrite.git
```
#### Latest Alpha Release
```
$ pip install misspy==2.0a4
```
#### Difference between Alpha release and Develop release
Develop releases are always installed from the latest source code, whereas Alpha releases are taken from the latest PyPI release.

### Tested Software
- Misskey v13 onward (Unavailable endpoints are designed to send an error, so they are available in v10 or later Misskey versions and forks.)

### example
An example can be found in [example directory](/example).

## Other

### Supported Version
misspy currently supports all versions of Python 3.8 and later.

### Docs
Documentation can be found at: [https://misspy.github.io/docs](#) (Currently under preparation.)
