import ast
from ast import AST
import os


def is_test_function(node: AST) -> bool:
    """Check if a node is a test function based on its name."""
    return isinstance(node, ast.FunctionDef) and node.name.startswith('test_')


def is_test_class(node: AST) -> bool:
    """Check if a node is a test class by looking for any test functions in its body."""
    return isinstance(node, ast.ClassDef) and any(
        is_test_function(child) or is_test_class(child) for child in node.body)


def get_code_from_node(node: AST, file_content: str) -> str:
    """Extract the code block for a given AST node."""
    lines = file_content.splitlines()
    start_line = node.lineno - 1
    end_line = node.end_lineno
    return '\n'.join(lines[start_line:end_line])


def find_node_in_hierarchy(tree, node_type, name):
    """Find a node by type and name in a hierarchy."""
    for node in ast.walk(tree):
        if isinstance(node, node_type) and node.name == name:
            return node
    return None


def parse_node_id(node_id):
    """Parse the node_id into file path, class names, and test function name."""
    parts = node_id.split("::")
    file_path = parts[0]
    class_names = parts[1:-1] if len(parts) > 2 else []
    test_name = parts[-1] if len(parts) > 1 else None
    return file_path, class_names, test_name


def collect_and_share_test_data(node_id):
    """Parse a .py file to extract content for specified class and test function."""
    file_path, class_names, test_name = parse_node_id(node_id)
    location = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    if not os.path.exists(file_path):
        print(f"Warning: The specified file does not exist: {file_path}")
        return None

    with open(file_path, 'r') as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    result = {
        "node_id": node_id,
        "location": location,
        "file_name": file_name,
        "file_content": file_content,
        "class_name": None,
        "class_content": None,
        "test_case_name": None,
        "test_case_content": None,
    }

    # Extract nested class content if class_names are specified
    if class_names:
        current_node = tree
        for class_name in class_names:
            current_node = find_node_in_hierarchy(current_node, ast.ClassDef, class_name)
            if current_node is None:
                break
        if current_node:
            result['class_name'] = class_names[-1]
            class_content = get_code_from_node(current_node, file_content)
            result['class_content'] = class_content
            # If a test_name is also specified, search within this class
            if test_name:
                for child in current_node.body:
                    if isinstance(child, ast.FunctionDef) and child.name in test_name:
                        result['test_case_name'] = test_name
                        test_case_content = get_code_from_node(child, file_content)
                        result['test_case_content'] = test_case_content
                        break
    else:
        # If no class_name is specified, look for the test function at the root level
        if test_name:
            for node in ast.walk(tree):
                if is_test_function(node) and node.name in test_name:
                    result['test_case_name'] = test_name
                    test_case_content = get_code_from_node(node, file_content)
                    result['test_case_content'] = test_case_content
                    break

    return result
