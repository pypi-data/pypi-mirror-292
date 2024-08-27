import html2text
from lxml import etree
import html5_parser
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
import re


def html_to_markdown_with_depth(html_content, max_depth):
    # Parse HTML using html5-parser
    document = html5_parser.parse(html_content)

    # Helper function to traverse the tree and convert to a string with limited depth
    def traverse_tree(node, current_depth):
        if current_depth > max_depth or not hasattr(node, 'tag'):
            return ""
        
        result = etree.tostring(node, encoding='unicode', method='html')
        
        # Recursively process child nodes
        for child in node:
            result += traverse_tree(child, current_depth + 1)
        
        return result

    # Start traversal from the root of the document
    limited_html = traverse_tree(document, 0)

    # Convert the limited HTML to Markdown
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False  # Keep links in the markdown
    markdown_text = text_maker.handle(limited_html)

    return markdown_text

def display_markdown_hierarchically(markdown_text, max_depth):
    console = Console()
    md = Markdown(markdown_text)
    console.print(md)

def cli(path, max_depth):
    with open(path, "r") as file:
        html_content = file.read()

    markdown_output = html_to_markdown_with_depth(html_content, max_depth)

    print("Markdown Output:")
    print(markdown_output)

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
