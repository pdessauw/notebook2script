import ast
import json
from os.path import exists, dirname


def cell_parser(cell: dict) -> list[str]:
    """Create python code from a cell source. Working for 'markdown' and 'code' cells."""
    if cell["cell_type"] == "markdown":
        return [f"# {cell_line}" for cell_line in cell["source"]]
    if cell["cell_type"] == "code":
        return cell["source"]

    # Cell type not recognized
    raise RuntimeError(f"Unknown cell type: {cell['cell_type']}")


def line_parser(line: str) -> str:
    """Fix lines of code for writing in document."""
    # Comment Jupyter notebook commands.
    if line.startswith("!") or line.startswith("%"):
        line = f"# {line}"

    if not line.endswith("\n"):  # Add line return if missing.
        line += "\n"
    return line


def main(notebook_path: str, script_path: str, reformat_code: bool = False) -> None:
    """Main function of the script"""
    # Script blocks and parameters
    imports = []
    library = []
    entrypoint = ['if __name__ == "__main__":\n']
    indent = " " * 4

    # Read notebook code and parse it
    with open(notebook_path, "r") as notebook_fp:
        code_blocks = [cell_parser(cell) for cell in json.load(notebook_fp)["cells"]]

    code = [line_parser(line) for block in code_blocks for line in block]
    parsed_code = ast.parse("".join(code))

    # Loop over every AST node to determine which category it belongs to. If
    # '--skip-reorg' is selected, all code goes in the entrypoint.
    if reformat_code:
        for ast_node in parsed_code.body:
            ast_code = ast.unparse(ast_node)
            ast_node_type = type(ast_node)

            # Imports are bundled together
            if ast_node_type in [ast.Import, ast.ImportFrom]:
                imports.append(ast_code)
                continue

            # Functions are stored in the library
            if ast_node_type in [ast.FunctionDef, ast.ClassDef]:
                library.append(ast_code + "\n\n")
                continue

            entrypoint.append(f"{indent}{ast_code.replace(indent, indent * 2)}\n")
    else:
        entrypoint += code

    with open(script_path, "w") as fp:
        fp.writelines(['"""\n', '"""\n'])  # Module level comments
        if len(imports) > 0:  # Write imports
            fp.writelines([line_parser(line) for line in imports] + ["\n\n"])
        if len(library) > 0:  # Write functions
            fp.writelines([line_parser(line) for line in library] + ["\n\n"])

        # Write the rest of the code
        fp.writelines([line_parser(line) for line in entrypoint] + ["\n"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A simple-minded converter to extract Jupyter notebook code into a "
        "Python script."
    )
    parser.add_argument(
        "notebook_path", help="path to the notebook to convert", type=str
    )
    parser.add_argument(
        "--output", "-o", help="path to the output script", type=str, required=True
    )
    parser.add_argument(
        "--reformat",
        "-r",
        help="try to reorganize imports, functions and code in separate blocks",
        action="store_true",
    )

    args = parser.parse_args()

    # Check argument correctness
    if not exists(args.notebook_path):
        raise RuntimeError("Notebook file does not exist")

    if not args.notebook_path.endswith(".ipynb"):
        raise RuntimeError("Notebook should have '.ipynb' extension")

    if not exists(dirname(args.output)):
        raise RuntimeError("Script directory does not exist")

    # Start
    main(args.notebook_path, args.output, args.reformat)
