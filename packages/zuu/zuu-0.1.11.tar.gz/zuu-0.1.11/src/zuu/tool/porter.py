import click
import ast
import os
import importlib
import inspect


def is_python_package(directory):
    """Check if a directory is a Python package."""
    return os.path.exists(os.path.join(directory, "__init__.py"))


def find_imports_from_zuu(file_content):
    """Find all imports from zuu in the file content."""
    tree = ast.parse(file_content)
    zuu_imports = {}

    for node in ast.walk(tree):
        # Handle imports like "from zuu.stdpkg.hashlib import hash_file, hash_folder"
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("zuu")
        ):
            for alias in node.names:
                zuu_imports[alias.name] = node.module

        # Handle direct imports like "import zuu.stdpkg.hashlib as hashlib"
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("zuu"):
                    zuu_imports[alias.asname or alias.name] = alias.name

    return zuu_imports


def process_package_files(source_package):
    """Process all Python files in the package to create a map of zuu functions."""
    function_map = {}
    for root, _, files in os.walk(source_package):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    file_content = f.read()

                zuu_imports = find_imports_from_zuu(file_content)

                for function, module_path in zuu_imports.items():
                    if function not in function_map:
                        function_map[function] = (file_path, module_path)

    return function_map


def resolve_function_source(
    module_path, function_name, resolved_functions, resolving_stack
):
    """Resolve the actual source of a function by inspecting its module."""
    if function_name in resolved_functions:
        return ""

    try:
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)
        source = inspect.getsource(func)

        # Parse the source to find additional dependencies
        tree = ast.parse(source)
        for node in ast.walk(tree):
            # Check for import statements within the function
            if isinstance(node, ast.ImportFrom):
                imported_module = node.module
                for alias in node.names:
                    if imported_module.startswith("zuu"):
                        resolve_function_source(
                            imported_module,
                            alias.name,
                            resolved_functions,
                            resolving_stack,
                        )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("zuu"):
                        resolve_function_source(
                            alias.name,
                            alias.name.split(".")[-1],
                            resolved_functions,
                            resolving_stack,
                        )

            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # Check if the called function is in the same module
                called_function = node.func.id
                if (
                    called_function not in resolved_functions
                    and called_function not in resolving_stack
                ):
                    # Prevent circular dependency issues
                    resolve_function_source(
                        module_path,
                        called_function,
                        resolved_functions,
                        resolving_stack,
                    )

        resolved_functions.add(function_name)
        return source
    except Exception as e:
        return f"# Unable to retrieve {function_name} from {module_path}: {e}\n"


def read_existing_utils(destination_file):
    """Read the existing utils.py file to identify already defined functions."""
    existing_functions = set()
    if os.path.exists(destination_file):
        with open(destination_file, "r") as f:
            file_content = f.read()
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    existing_functions.add(node.name)
    return existing_functions


def create_utils_file(function_map, destination_file):
    """Create or update a utils.py file with the necessary functions."""
    existing_functions = read_existing_utils(destination_file)
    resolved_functions = set()

    with open(destination_file, "a") as f:  # Open in append mode
        f.write("# Auto-generated utils.py\n")
        f.write("# This file contains functions imported from the 'zuu' library.\n\n")

        for function, (_, module_path) in function_map.items():
            if (
                function not in existing_functions
                and function not in resolved_functions
            ):
                # Write the identifier line with module path
                f.write(f"#!<zuu>{module_path}\n")
                # Retrieve and write the actual function source code
                source = resolve_function_source(
                    module_path, function, resolved_functions, resolving_stack=set()
                )
                f.write(source + "\n\n")


def get_relative_import_path(from_path, to_path):
    """Calculate the relative import path from one file to another."""
    from_parts = os.path.relpath(from_path, os.path.dirname(to_path)).split(os.path.sep)
    relative_depth = len(from_parts) - 1  # Number of directories up to go
    return "." * relative_depth


def rewrite_imports(source_package, function_map, utils_file):
    """Rewrite imports in the source package to point to utils.py."""
    for root, _, files in os.walk(source_package):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    file_content = f.read()

                tree = ast.parse(file_content)
                modified = False

                # Collect imports to replace
                new_imports = []
                for node in tree.body:
                    if (
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and node.module.startswith("zuu")
                    ):
                        new_imports.extend(
                            alias.name
                            for alias in node.names
                            if alias.name in function_map
                        )
                        modified = True
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if (
                                alias.name.startswith("zuu")
                                and alias.name in function_map
                            ):
                                new_imports.append(alias.name)
                                modified = True

                if modified:
                    # Calculate the relative import path
                    relative_import = get_relative_import_path(file_path, utils_file)
                    # Create a new import statement
                    new_import_statement = f"from {relative_import}.utils import {', '.join(new_imports)}\n"
                    # Rewrite the file content with the new import statement
                    new_content = ast.unparse(tree).replace(
                        file_content, new_import_statement
                    )

                    with open(file_path, "w") as f:
                        f.write(new_content)


@click.group()
def cli():
    """CLI tool for processing Python packages."""
    pass


@cli.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
    help="Source package to process.",
)
@click.option(
    "--destination-file", "-d", type=click.Path(), help="File to copy functions to."
)
def port(source, destination_file):
    """Process a package to trace zuu functions and copy them to a utils file."""
    if not is_python_package(source):
        raise click.UsageError(
            f"{source} is not a valid Python package (missing __init__.py)"
        )

    if destination_file is None:
        destination_file = os.path.join(source, "utils.py")

    click.echo(f"Processing package at {source}...")

    # Scan the entire package to create a map of functions
    function_map = process_package_files(source)

    # Print discovered functions
    click.echo("Discovered zuu functions:")
    for function, (file_path, module_path) in function_map.items():
        click.echo(f"- {function} (found in {file_path}, imported from {module_path})")

    # Create or update the utils.py file
    create_utils_file(function_map, destination_file)

    # Rewrite imports to use utils.py
    rewrite_imports(source, function_map, destination_file)

    click.echo(
        f"Functions have been copied to {destination_file} and imports have been updated."
    )


def run():
    """port zuu functions"""
    isy = input("This is a beta solution, proceed with caution. (press y to continue)")
    if isy != "y":
        return

    cli()


if __name__ == "__main__":
    cli()
