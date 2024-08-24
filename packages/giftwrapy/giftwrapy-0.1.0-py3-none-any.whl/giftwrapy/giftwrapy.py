import argparse
import fnmatch
import os
from pathlib import Path

# Constants for tree structure
tee = "├── "
last = "└── "
branch = "│   "
space = "    "


def tree(dir_path: Path, prefix: str = "", ignore_dirs=None, ignore_files=None):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        if path.is_dir() and should_ignore(path.name, ignore_dirs):
            continue
        if path.is_file() and should_ignore(path.name, ignore_files):
            continue
        yield prefix + pointer + path.name
        if path.is_dir():
            extension = branch if pointer == tee else space
            yield from tree(
                path,
                prefix=prefix + extension,
                ignore_dirs=ignore_dirs,
                ignore_files=ignore_files,
            )


def should_ignore(name, ignore_patterns):
    """Check if a name matches any of the ignore patterns."""
    if ignore_patterns is None:
        return False
    return any(fnmatch.fnmatch(name, pattern) for pattern in ignore_patterns)


def repo_to_markdown(
    directory: str,
    extensions: list,
    ignore_dirs: list = None,
    ignore_files: list = None,
    output_file: str = "project_contents.md",
) -> str:
    """
    Convert a repository to a single markdown file.

    Args:
    directory (str): The path to the directory to convert.
    extensions (list): List of file extensions to include.
    ignore_dirs (list): List of directory names or patterns to ignore in content (optional).
    ignore_files (list): List of file names or patterns to ignore in content (optional).
    output_file (str): Name of the output markdown file.

    Returns:
    str: The path to the generated markdown file.
    """
    markdown = ""

    # Generate directory tree
    markdown += "# Project Structure\n\n```plaintext\n"

    # add directory name to the top of the tree
    markdown += Path(directory).name + "\n"

    for line in tree(
        Path(directory), ignore_dirs=ignore_dirs, ignore_files=ignore_files
    ):
        markdown += line + "\n"
    markdown += "```\n\n"

    # Process files
    markdown += "# File Contents\n\n"
    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(d, ignore_dirs)]

        for file in files:
            if should_ignore(file, ignore_files):
                continue

            file_path = os.path.join(root, file)
            _, file_extension = os.path.splitext(file)

            if file_extension in extensions:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                relative_path = os.path.relpath(file_path, directory)
                markdown += f"## {relative_path}\n\n"
                markdown += f"```{file_extension[1:]}\n{content}\n```\n\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    return os.path.abspath(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a repository to a single markdown file."
    )
    parser.add_argument("directory", help="The path to the directory to convert.")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".html", ".sql", ".css"],
        help="List of file extensions to include.",
    )
    parser.add_argument(
        "--ignore-dirs",
        nargs="+",
        default=["__pycache__", "migrations"],
        help="List of directory names or patterns to ignore.",
    )
    parser.add_argument(
        "--ignore-files",
        nargs="+",
        default=[],
        help="List of file names or patterns to ignore.",
    )
    parser.add_argument(
        "--output",
        default="project_contents.md",
        help="Name of the output markdown file.",
    )

    args = parser.parse_args()

    result = repo_to_markdown(
        args.directory,
        args.extensions,
        args.ignore_dirs,
        args.ignore_files,
        args.output,
    )

    print(f"Markdown file generated successfully: {result}")


if __name__ == "__main__":
    main()
