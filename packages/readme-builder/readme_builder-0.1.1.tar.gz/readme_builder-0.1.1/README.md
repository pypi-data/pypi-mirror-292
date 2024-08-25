## Readme Builder

This project provides a command-line tool for generating README files automatically independent of programming language. It generates a comprehensive and informative README (requires minimal editing) file based on the project structure and files present.

### Features

* **Automatic README Generation:** Analyzes project files and structure to automatically generate a well-formatted README.md file.
* **Project Overview:**  Provides a concise overview of the project's purpose and functionality.
* **Feature Listing:**  Identifies and lists key features based on the project's directory structure and file names.
* **Installation Instructions:**  Generates installation instructions tailored to the project's dependencies and environment management tools.
* **Usage Examples:**  Provides code examples and command-line instructions for running and using the project.

### Installation

Ensure you have `python3` and `pip` on your system.

```bash
pip install readme-builder
```

### Usage

**Run the CLI:**
```bash
readme-builder <path-to-directory>
```

This will analyze the project structure and generate a `README.md` file in the specified directory.


### Contact Information

For any inquiries or feedback, please contact:

* **Email:** akshitadixit[dot]int[at]gmail[dot]com

## Privacy concerns

Uses Gemini to generate the README. No actual file content (except for readme, contributing, license, etc.) is shared with it though. Only file names. No actual code is shared.

## Doesn't work that well?

If your project is a very vague directory with random file names, not even a human would have context about it, this is still AI.
Also this package is written with the purpose of generating a README that <b>requires minimal editing</b>. Take waht is generates, add a couple of fixes and you're good to go.<br>
If however, something super unusual comes up, please raise it to me. Thanks.
