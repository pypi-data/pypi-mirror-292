### mrender/docs2md.py
```python
import inspect
import importlib
import os
from pathlib import Path
import re
from typing import Any, Callable, Dict, List, Tuple, Union


def parse_google_docstring(docstring: str) -> Dict[str, Any]:
    """Parse a Google-style docstring into its components."""
    sections = {
        'description': '',
        'args': {},
        'returns': '',
        'examples': []
    }
    current_section = 'description'
    
    lines = docstring.split('\n')
    for line in lines:
        line = line.strip()
        if line.lower().startswith('args:'):
            current_section = 'args'
        elif line.lower().startswith('returns:'):
            current_section = 'returns'
        elif line.lower().startswith('examples:'):
            current_section = 'examples'
        elif ':' in line and current_section == 'args':
            param, desc = line.split(':', 1)
            sections['args'][param.strip()] = desc.strip()
        elif current_section == 'examples' and line.startswith('>>>'):
            sections['examples'].append(line)
        else:
            sections[current_section] += line + '\n'
    
    # Clean up sections
    for key in sections:
        if isinstance(sections[key], str):
            sections[key] = sections[key].strip()
    
    return sections

def get_relative_path(obj: type | Callable | object) -> str:
    """Get the relative path of the file containing the object."""
    try:
        module = inspect.getmodule(obj)
        if module is None:
            return "Unknown location"
        
        return os.path.relpath(inspect.getfile(module))
    except ValueError:
        return "Unknown location"

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

def generate_method_list(methods: List[Tuple[str, Dict[str, Any]]]) -> str:
    """Generate a markdown list of methods with their descriptions."""
    if not methods:
        return ""
    
    markdown = "<p><strong>Methods</strong></p>\n\n<ul>\n"
    for method_name, method_doc in methods:
        args = ', '.join(method_doc['args'].keys())
        first_sentence = method_doc['description'].split('.')[0]
        markdown += f"<li>`{method_name}({args})`: {first_sentence}</li>\n"
    markdown += "</ul>\n"
    return markdown

def generate_docs(obj: type | Callable | object) -> str:
    """Generate markdown documentation for a given object (class, function, or module).
    
    Args:
    obj: The object to document
    
    Returns:
    str: Markdown formatted documentation
    """
    if inspect.isclass(obj):
        return generate_class_docs(obj)
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        return generate_function_docs(obj)
    if inspect.ismodule(obj):
        return generate_module_docs(obj)
    return f"Unsupported object type: {type(obj)}"

def generate_class_docs(cls: type) -> str:
    """Generate markdown documentation for a class."""
    class_name = cls.__name__
    class_doc = cls.__doc__ or "No class description available."
    parsed_class_doc = parse_google_docstring(class_doc)
    
    file_path = get_relative_path(cls)
    
    methods = []
    for name, member in inspect.getmembers(cls):
        if inspect.isfunction(member) or inspect.ismethod(member) and not name.startswith('_'):
                method_doc = inspect.getdoc(member) or "No description available."
                parsed_method_doc = parse_google_docstring(method_doc)
                methods.append((name, parsed_method_doc))
    
    return f"""
## Class: {class_name}

Defined in: `{file_path}`

{parsed_class_doc['description']}

{generate_feature_list(parsed_class_doc['description'])}

{generate_examples(parsed_class_doc['examples'])}

{generate_method_list(methods)}

"""

def generate_function_docs(func: Callable) -> str:
    """Generate markdown documentation for a function or method."""
    func_name = func.__name__
    func_doc = func.__doc__ or "No function description available."
    parsed_func_doc = parse_google_docstring(func_doc)
    
    file_path = get_relative_path(func)
    
    args = ', '.join(parsed_func_doc['args'].keys())
    
    markdown = f"""
### Function: {func_name}({args})

Defined in: `{file_path}`

{parsed_func_doc['description']}

**Arguments:**
"""

    for arg, desc in parsed_func_doc['args'].items():
        markdown += f"- `{arg}`: {desc}\n"

    markdown += f"""

**Returns:**
{parsed_func_doc['returns']}

{generate_examples(parsed_func_doc['examples'])}

"""

    return markdown

def generate_module_docs(module: object) -> str:
    """Generate markdown documentation for a module."""
    module_name = getattr(module, '__name__', 'Unknown')
    module_doc = getattr(module, '__doc__', "No module description available.")
    parsed_module_doc = parse_google_docstring(module_doc)
    
    file_path = get_relative_path(module)
    
    markdown = f"""
# Module: {module_name}

Defined in: `{file_path}`

{parsed_module_doc['description']}

{generate_feature_list(parsed_module_doc['description'])}

{generate_examples(parsed_module_doc['examples'])}

## Contents

"""

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            if not name.startswith('_'):  # Exclude private members
                markdown += f"- [{name}](#{name.lower().replace(' ', '-')})\n"
    
    markdown += "\n"

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            if not name.startswith('_'):  # Exclude private members
                markdown += generate_docs(obj) + "\n"

    return markdown

def cli(path: str, output_file: str) -> None:
    """Generate markdown documentation for all modules in a given path."""
    if not os.path.exists(path):
        print(f"Error: Path does not exist: {path}")
        return
    if os.path.isfile(path):
        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        markdown = generate_module_docs(module)
    elif os.path.isdir(path):
        mds = []
        for file in os.listdir(path):
            if file.endswith('.py'):
                module_name = file[:-3]
                module_path = os.path.join(path, file)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                markdown = generate_module_docs(module)
                mds.append(markdown)
        markdown = "\n".join(mds)
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
# Copy the entire content of your docs2md.py file here
# Make sure to keep the existing imports and add any necessary ones

# ... (rest of the docs2md.py content)

```