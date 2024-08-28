import re

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from rich.console import Console
from rich.markdown import Markdown as RichMarkdown
from rich.panel import Panel
from rich.text import Text

from mrender.md import Markdown


def html_to_markdown_with_depth(html_content, max_depth):
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    def traverse_tree(node, current_depth):
        if current_depth > max_depth:
            return ""
        
        if isinstance(node, str):
            return node.strip()
        
        result = []
        for child in node.children:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                header_level = min(int(child.name[1]), max_depth)
                result.append('#' * header_level + ' ' + child.get_text().strip())
            elif child.name == 'p':
                result.append(child.get_text().strip())
            else:
                result.append(traverse_tree(child, current_depth + 1))
        
        return '\n\n'.join(filter(None, result))

    # Start traversal from the body tag
    body = soup.body or soup
    markdown_text = traverse_tree(body, 1)  # Start from body with depth 1

    return markdown_text

def display_markdown_hierarchically(markdown_text, max_depth):

    md = Markdown(markdown_text)
    md.stream(max_depth)



def cli(path, max_depth):
    with open(path, "r") as file:
        html_content = file.read()

    markdown_output = html_to_markdown_with_depth(html_content, max_depth)



    display_markdown_hierarchically(markdown_output, max_depth)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python web2md.py <path> <max_depth>")
        sys.exit(1)
    
    cli(sys.argv[1], int(sys.argv[2]))
    # # Sample HTML content
    # html_content = """
    # <html>
    #     <head><title>Sample Page</title></head>
    #     <body>
    #         <h1>Heading 1</h1>
    #         <p>This is a <strong>sample</strong> paragraph with <a href="https://example.com">a link</a>.</p>
    #         <div>
    #             <h2>Subheading</h2>
    #             <ul>
    #                 <li>First item</li>
    #                 <li>Second item</li>
    #             </ul>
    #         </div>
    #         <footer>
    #             <p>Footer content</p>
    #         </footer>
    #     </body>
    # </html>
    # """

    # max_depth = 3
    # markdown_output = html_to_markdown_with_depth(html_content, max_depth)

    # print("Markdown Output:")
    # print(markdown_output)

    # display_markdown_hierarchically(markdown_output, max_depth)import re

def extract_links(markdown_content):
    """Extract links from markdown content."""
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, markdown_content)
    return [{"text": text, "url": url} for text, url in links]
