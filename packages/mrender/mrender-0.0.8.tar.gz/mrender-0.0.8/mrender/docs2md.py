import re
from pathlib import Path
from typing import Dict, List, Union

def parse_google_docstring(docstring: str) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
    """Parse a Google-style docstring into its components using regex."""
    sections = {
        'description': '',
        'args': {},
        'returns': '',
        'examples': []
    }
    
    # Extract description
    description_match = re.match(r'(.*?)(?:Args:|Returns:|Examples:|\Z)', docstring, re.DOTALL)
    if description_match:
        sections['description'] = description_match.group(1).strip()
    
    # Extract args
    args_match = re.search(r'Args:(.*?)(?:Returns:|Examples:|\Z)', docstring, re.DOTALL)
    if args_match:
        args_section = args_match.group(1)
        arg_matches = re.finditer(r'(\w+)\s*:\s*(.+?)(?=\w+\s*:|\Z)', args_section, re.DOTALL)
        for match in arg_matches:
            sections['args'][match.group(1)] = match.group(2).strip()
    
    # Extract returns
    returns_match = re.search(r'Returns:(.*?)(?:Examples:|\Z)', docstring, re.DOTALL)
    if returns_match:
        sections['returns'] = returns_match.group(1).strip()
    
    # Extract examples
    examples_match = re.search(r'Examples:(.*)', docstring, re.DOTALL)
    if examples_match:
        sections['examples'] = [line.strip() for line in examples_match.group(1).strip().split('\n') if line.strip()]
    
    return sections

def generate_feature_list(description: str) -> str:
    """Generate a markdown list of features from the description."""
    features = re.findall(r'- (.*)', description)
    if not features:
        return ""
    
    markdown = "<p><strong>Key features</strong></p>\n\n<ul>\n"
    for feature in features:
        markdown += f"<li>{feature}</li>\n"
    markdown += "</ul>\n"
    return markdown

def generate_examples(examples: List[str]) -> str:
    """Generate a markdown code block with examples."""
    if not examples:
        return ""
    
    markdown = "<p><strong>Usage example</strong></p>\n\n<pre><code>\n"
    for example in examples:
        markdown += f"{example}\n"
    markdown += "</code></pre>\n"
    return markdown

def generate_docs(file_path: str) -> str:
    """Generate markdown documentation for a given Python file."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    module_name = Path(file_path).stem
    markdown = f"# Module: {module_name}\n\n"
    
    # Extract module docstring
    module_doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if module_doc_match:
        module_doc = module_doc_match.group(1).strip()
        parsed_module_doc = parse_google_docstring(module_doc)
        markdown += f"{parsed_module_doc['description']}\n\n"
        markdown += generate_feature_list(parsed_module_doc['description'])
        markdown += generate_examples(parsed_module_doc['examples'])
    else:
        markdown += "No module description available.\n\n"
    
    # Extract classes and functions
    class_matches = re.finditer(r'class\s+(\w+).*?:\s*(""".*?""")?', content, re.DOTALL)
    func_matches = re.finditer(r'def\s+(\w+).*?:\s*(""".*?""")?', content, re.DOTALL)
    
    for match in class_matches:
        class_name = match.group(1)
        class_doc = match.group(2)
        if class_doc:
            parsed_class_doc = parse_google_docstring(class_doc.strip('"""'))
            markdown += f"## Class: {class_name}\n\n"
            markdown += f"{parsed_class_doc['description']}\n\n"
            markdown += generate_feature_list(parsed_class_doc['description'])
            markdown += generate_examples(parsed_class_doc['examples'])
    
    for match in func_matches:
        func_name = match.group(1)
        func_doc = match.group(2)
        if func_doc:
            parsed_func_doc = parse_google_docstring(func_doc.strip('"""'))
            markdown += f"### Function: {func_name}\n\n"
            markdown += f"{parsed_func_doc['description']}\n\n"
            if parsed_func_doc['args']:
                markdown += "**Arguments:**\n\n"
                for arg, desc in parsed_func_doc['args'].items():
                    markdown += f"- `{arg}`: {desc}\n"
                markdown += "\n"
            if parsed_func_doc['returns']:
                markdown += f"**Returns:** {parsed_func_doc['returns']}\n\n"
            markdown += generate_examples(parsed_func_doc['examples'])
    
    return markdown

def cli(path: str, output_file: str) -> None:
    """Generate markdown documentation for all Python files in a given path."""
    if Path(path).is_file():
        markdown = generate_docs(path)
    elif Path(path).is_dir():
        markdown = ""
        for file in Path(path).glob('**/*.py'):
            markdown += generate_docs(str(file)) + "\n\n"
    else:
        print(f"Error: Path is neither a file nor a directory: {path}")
        return
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(markdown)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python docs2md.py <path> <output_file>")
        sys.exit(1)
    cli(sys.argv[1], sys.argv[2])
