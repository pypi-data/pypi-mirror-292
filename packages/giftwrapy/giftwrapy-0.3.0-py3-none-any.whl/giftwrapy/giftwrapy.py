import argparse
import fnmatch
import os
from pathlib import Path

__ALL__ = ["dir_to_markdown", "tree"]

DEFAULT_TREE_IGNORE_PATS = [
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "dist",
    ".DS_Store",
    "*.pyc",
    ".ruff_cache",
    "staticfiles",
]


DEFAULT_CONTENTS_IGNORE_PATS = DEFAULT_TREE_IGNORE_PATS + [
    "migrations",
]


# Constants for tree structure
TEE = "├── "
LAST = "└── "
BRANCH = "│   "
SPACE = "    "


def tree(
    dir_path: Path,
    prefix: str = "",
    ignore_dirs=None,
    ignore_files=None,
    use_default_ignore_pats=True,
):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters

    Parameters
    ----------
    dir_path : Path
        The directory to generate the tree for.

    prefix : str, optional
        The prefix to add to each line of the tree.
        Default is an empty string.

    ignore_dirs : list, optional
        List of directory names or patterns to ignore in content.
        Default is None.

    ignore_files : list, optional
        List of file names or patterns to ignore in content.
        Default is None.

    use_default_ignore_pats : bool, optional
        Whether to use the default ignore patterns for directories.
        Default is True.
    """
    ignore_dirs = ignore_dirs or []
    ignore_files = ignore_files or []

    if use_default_ignore_pats:
        ignore_dirs.extend(DEFAULT_TREE_IGNORE_PATS)
        ignore_files.extend(DEFAULT_TREE_IGNORE_PATS)

    contents = list(dir_path.iterdir())
    pointers = [TEE] * (len(contents) - 1) + [LAST]
    for pointer, path in zip(pointers, contents):
        if path.is_dir() and should_ignore(path.name, ignore_dirs):
            continue
        if path.is_file() and should_ignore(path.name, ignore_files):
            continue
        yield prefix + pointer + path.name
        if path.is_dir():
            extension = BRANCH if pointer == TEE else SPACE
            yield from tree(
                path,
                prefix=prefix + extension,
                ignore_dirs=ignore_dirs,
                ignore_files=ignore_files,
                use_default_ignore_pats=False,
            )


def should_ignore(name, ignore_patterns):
    """Check if a name matches any of the ignore patterns."""
    if ignore_patterns is None:
        return False
    return any(fnmatch.fnmatch(name, pattern) for pattern in ignore_patterns)


def dir_to_markdown(
    directory: str,
    extensions: list,
    ignore_dirs: list = None,
    ignore_files: list = None,
    use_default_ignore_pats: bool = True,
    output_file: str = "project_contents.md",
) -> str:
    """
    Convert a repository to a single markdown file.

    Parameters
    ----------
    directory : str
        The path to the directory to convert.
    extensions : list
        List of file extensions to include.
    ignore_dirs : list, optional
        List of directory names or patterns to ignore in content.
    ignore_files : list, optional
        List of file names or patterns to ignore in content.
    use_default_ignore_pats : bool, optional
        Whether to use the default ignore patterns for directories.
        These also affect the tree structure representation.
        e.g, '__pycache__', 'migrations', '.git', '.idea', '.vscode', '.venv'.
        (see DEFAULT_CONTENTS_IGNORE_PATS)
        Default is True.
    output_file : str, optional
        Name of the output markdown file.

    Returns
    -------
    str
        The path to the generated markdown file.
    """

    ignore_dirs = ignore_dirs or []
    ignore_files = ignore_files or []

    if use_default_ignore_pats:
        ignore_dirs.extend(DEFAULT_CONTENTS_IGNORE_PATS)
        ignore_files.extend(DEFAULT_CONTENTS_IGNORE_PATS)

    markdown = ""

    # Generate directory tree
    markdown += "# Project Structure\n\n```plaintext\n"

    # add directory name to the top of the tree
    markdown += Path(directory).name + "\n"

    for line in tree(
        Path(directory),
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files,
        use_default_ignore_pats=use_default_ignore_pats,
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

                if content.strip():  # Check if content is not empty
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
        default=[".py", ".html", ".sql", ".css", ".md"],
        help="List of file extensions to include.",
    )
    parser.add_argument(
        "--ignore-dirs",
        nargs="+",
        default=[],
        help="List of directory names or patterns to ignore.",
    )
    parser.add_argument(
        "--ignore-files",
        nargs="+",
        default=[],
        help="List of file names or patterns to ignore.",
    )
    parser.add_argument(
        "--use-default-ignore-pats",
        default=True,
        action="store_true",
        help="Whether to use the default ignore patterns.",
    )
    parser.add_argument(
        "--output",
        default="project_contents.md",
        help="Name of the output markdown file.",
    )

    args = parser.parse_args()

    result = dir_to_markdown(
        args.directory,
        args.extensions,
        args.ignore_dirs,
        args.ignore_files,
        args.use_default_ignore_pats,
        args.output,
    )

    print(f"Markdown file generated successfully: {result}")


if __name__ == "__main__":
    main()
