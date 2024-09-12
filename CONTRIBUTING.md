# Contributing Guidelines

First off, thank you for taking the time to contribute! 🎉 Your help is greatly appreciated. Below are some guidelines for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Reporting Bugs](#reporting-bugs)
4. [Suggesting Enhancements](#suggesting-enhancements)
5. [Pull Requests](#pull-requests)
6. [Development Setup](#development-setup)
7. [Style Guide](#style-guide)
8. [License](#license)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [email@example.com](mailto:email@example.com).

## How to Contribute

### Reporting Bugs

If you find a bug, please report it by [opening an issue](https://github.com/WagnerAG/checkmk_fortigate/issues). Be sure to include:

- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Any relevant logs, screenshots, or code snippets.

### Suggesting Enhancements

If you have an idea to improve the project, we'd love to hear it! Please [open an issue](https://github.com/WagnerAG/checkmk_fortigate/issues) and include:

- A clear and descriptive title.
- The reasoning behind the enhancement.
- How it would benefit the project.
- Any implementation suggestions (if you have them).

### Pull Requests

If you're ready to make changes, follow these steps:

1. **Fork the repository.**
2. **Create a new branch** for your changes (`git checkout -b my-feature-branch`).
3. **Commit your changes** (`git commit -am 'Add a feature'`).
4. **Push to the branch** (`git push origin my-feature-branch`).
5. **Open a Pull Request** with a clear title and description.

Please ensure your pull request:

- Passes all tests and linter checks.
- Is focused on a single feature or issue.
- Includes relevant documentation if applicable.

### Development Setup

This project uses Visual Studio Code with a `devcontainer` for development. Follow these steps to get started:

1. **Clone the repository**:
   ```sh
   https://github.com/WagnerAG/checkmk_fortigate.git
   cd checkmk_fortigate
   ```

2. **Open the project in Visual Studio Code**:
   ```sh
   code .
   ```

3. **Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS)** and select `Remote-Containers: Reopen in Container`. This will build and start the development container.

4. **Install dependencies** (if not already installed in the container):
   ```sh
   pip install -r requirements.txt
   ```

5. **Run the tests**:
   ```sh
   pytest
   ```

Run pytest in verbose mode
   ```sh
    pytest -v
   ```

### Style Guide

This project uses [`ruff`](https://github.com/charliermarsh/ruff) for linting and code style. To ensure consistency, make sure to run `ruff` before committing your code:

```sh
ruff check .
```

To automatically fix issues:

```sh
ruff check . --fix
```

### License

By contributing, you agree that your contributions will be licensed under the same license as the project.