from giftwrapy import dir_to_markdown

dir_to_markdown(
    directory=".",
    extensions=[".py", ".html", ".sql", ".css", ".md"],
    output_file="project_contents.md",
)
