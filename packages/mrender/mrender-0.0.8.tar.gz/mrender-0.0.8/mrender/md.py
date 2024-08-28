import logging
import time
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown as RichMarkdown

logger = logging.getLogger(__name__)

class Markdown:
    """Stream formatted JSON-like text to the terminal with live updates."""
    
    def __init__(self, data=None, mdargs=None, style="default", save=None):
        logger.debug(f"Initializing Markdown with data: {data}")
        self.data = data or {}

        self.mdargs = mdargs or {}
        self.style = style
        self.console = Console(style=self.style)
        self.live = Live(console=self.console, refresh_per_second=4)
        self.save = save
        self.lines = [data] if isinstance(data, str) else []


    def generate_markdown(self, data=None, depth=1):
        """Generate Markdown from JSON with headers based on depth."""
        data = data if data is not None else self.data
        markdown_lines = []
        indent = "  " * (depth - 1)  # Reduce indent by one level

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and 'type' in value and value['type'] == 'python':
                    markdown_lines.append(f"{indent}{'#' * depth} {key}")
                    markdown_lines.append("```python")
                    markdown_lines.extend(value['content'].split('\n'))
                    markdown_lines.append("```")  # Ensure the code block is closed
                elif isinstance(value, (dict, list)):
                    markdown_lines.append(f"{indent}{'#' * depth} {key}")
                    markdown_lines.extend(self.generate_markdown(value, depth + 1))
                else:
                    markdown_lines.append(f"{indent}- **{key}**: {value}")
        elif isinstance(data, list):
            for item in data:
                markdown_lines.extend(self.generate_markdown(item, depth))
        elif isinstance(data, str):
            for line in data.split("\n"):
                markdown_lines.append(f"{indent}{line}")
        
        return markdown_lines

    def stream(self, depth=0):
        logger.debug(f"Streaming with depth: {depth}")
        if not self.data:
            logger.warning("No data to display.")
            return

        markdown_content = "\n".join(self.generate_markdown(self.data, depth))
        
        with self.live:
            self.live.update(RichMarkdown(markdown_content, **self.mdargs))
            time.sleep(0.1)  # Small delay for visual effect

        if self.save:
            Path(self.save).write_text(markdown_content)
            logger.info(f"Markdown content saved to {self.save}")

def recursive_read(file, include=None):
    include = include or {".json", ".md", ".txt", ".yaml", ".toml", ".py"}
    data = {}
    file_path = Path(file)
    if file_path.is_file() and file_path.suffix in include and "__pycache__" not in str(file_path):
        logger.info(f"Reading file: {file_path}")
        content = file_path.read_text()
        if file_path.suffix == '.py':
            data[str(file_path)] = {'type': 'python', 'content': content}
        else:
            data[str(file_path)] = content
    elif file_path.is_dir():
        for sub_path in file_path.iterdir():
            data.update(recursive_read(sub_path, include))
    return data

def example():
    nested_data = {
        "name": "Example Package",
        "version": "1.0.0",
        "description": "This is a deeply nested structure.",
        "dependencies": [
            {
                "name": "Dependency 1",
                "version": "2.0.0",
                "sub_dependencies": [
                    {
                        "name": "Sub-dependency A",
                        "version": "2.1.1",
                        "details": {
                            "maintainer": "John Doe",
                            "license": "MIT"
                        }
                    },
                    {
                        "name": "Sub-dependency B",
                        "version": "2.1.2",
                        "details": {
                            "maintainer": "Jane Smith",
                            "license": "Apache-2.0"
                        }
                    }
                ]
            },
            {
                "name": "Dependency 2",
                "version": "3.0.0",
                "sub_dependencies": [
                    {
                        "name": "Sub-dependency C",
                        "version": "3.1.0",
                        "details": {
                            "maintainer": "Alice Brown",
                            "license": "GPL-3.0"
                        }
                    }
                ]
            }
        ],
        "urls": {
            "Homepage": "https://example.com",
            "Repository": "https://github.com/example/package"
        }
    }

    md = Markdown(data=nested_data)
    md.stream()

if __name__ == "__main__":
    example()
