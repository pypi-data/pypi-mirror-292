import argparse
import os

import requests

_WEBSERVER_URL = "https://readme-builder.onrender.com/generate_readme"


def read_file(file_path):
    """Utility function to read the content of a file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def extract_contact_from_readme(readme_path):
    """Extract contact information from README.md or fallback configuration files."""
    readme_content = read_file(readme_path)
    if readme_content:
        # Simple extraction logic based on common patterns
        lines = readme_content.split("\n")
        flag = -1
        for i, line in enumerate(lines):
            if (
                "contact" in line.lower()
                or "maintainer" in line.lower()
                or "author" in line.lower()
            ):
                flag = i
                break
        if flag != -1:
            return "\t".join(lines[flag:])

    return extract_contact_from_config_files(os.path.dirname(readme_path))


def extract_contact_from_config_files(directory):
    possible_extensions = [
        ".toml",
        ".xml",
        "Pipfile",
        "Makefile",
        "config.js",
        "Gemfile",
        ".gradle",
        ".json",
        ".md",
        ".env",
    ]

    for ext in possible_extensions:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            if ext in (file_ext, filename):
                file_content = read_file(file_path)
                if (
                    "email" in file_content
                    or "contact" in file_content
                    or "author" in file_content
                    or "maintainer" in file_content
                    or "support" in file_content
                ):
                    return file_content

            if filename == "setup.py":
                file_content = read_file(file_path)
                if (
                    "email" in file_content
                    or "contact" in file_content
                    or "author" in file_content
                    or "maintainer" in file_content
                    or "support" in file_content
                ):
                    return file_content

    return ""


def get_context_from_files(directory):
    """Extracts content from files to provide context for the model."""
    context, _contributing, _license, _contact = "", "", "", ""
    ignored_files = ["Dockerfile", "LICENSE", "CHANGELOG.md", "VERSION"]
    for dirpath, dirnames, filenames in os.walk(directory):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        level = dirpath.replace(directory, "").count(os.sep)
        indent = " " * 4 * level
        context += f"{indent}{os.path.basename(dirpath)}/\n"
        sub_indent = " " * 4 * (level + 1)
        for filename in filenames:
            if filename.lower() == "contributing.md":
                _contributing = read_file(os.path.join(dirpath, filename))
            if filename.lower() == "license" or filename.lower() == "license.md":
                _license = read_file(os.path.join(dirpath, filename))
            if filename.lower() == "readme.md":
                _contact = extract_contact_from_readme(os.path.join(dirpath, filename))

            if not (
                filename in ignored_files
                or filename.startswith(".")
                or filename.endswith(".yml")
                or filename.endswith(".lock")
                or filename.endswith(".env")
                or filename.endswith(".rdb")
                or filename.endswith(".csv")
            ):
                context += f"{sub_indent}{filename}\n"

    if not _contact:
        _contact = extract_contact_from_config_files(directory)

    return context, _contributing, _license, _contact


def get_generated_readme(
    _context, _contributing=None, _license=None, _contact=None
) -> str:
    url = _WEBSERVER_URL
    payload = {
        "context": _context,
        "contributing": _contributing,
        "license": _license,
        "contact": _contact,
    }
    print(url, payload)
    response = requests.post(url, json=payload)
    if response.status_code == 200:  # noqa: PLR2004
        return response.json().get("readme")
    else:
        raise ValueError(f"Error generating README: {response.json().get('error')}")


def generate_readme(directory):
    context, _contributing, _license, _contact = get_context_from_files(directory)
    readme_content = get_generated_readme(context, _contributing, _license, _contact)
    return readme_content


def main():
    parser = argparse.ArgumentParser(
        description="Automatically generate a README.md file."
    )
    parser.add_argument("directory", type=str, help="The project directory to analyze.")
    args = parser.parse_args()
    readme_content = generate_readme(args.directory)
    print(readme_content)
    readme_path = os.path.join(args.directory, "README.md")
    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_content)

    print(f"README.md generated successfully in {args.directory}")


if __name__ == "__main__":
    main()
