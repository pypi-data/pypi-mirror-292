import re
import urllib.parse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

import lxml.html
from html5_parser import parse
import html2text
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def expand_and_view_webpage(url):
    if not is_valid_url(url):
        return "Invalid URL. Please enter a valid URL including the protocol (e.g., http:// or https://)."
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        plain_text = soup.get_text(separator='\n', strip=True)
        
        # Extract and append links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith(('http://', 'https://')):
                href = urllib.parse.urljoin(url, href)
            links.append(f"[{a.text.strip()}]({href})")
        if links:
            plain_text += "\n\n## Links found on the page:\n\n" + "\n".join(links)
        
        return plain_text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"Error parsing the webpage: {str(e)}"

def display_webpage_content(url, content):
    console = Console()
    title = Text(f"Webpage: {url}", style="bold magenta")
    
    # Clean up the content
    cleaned_content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
    cleaned_content = re.sub(r'\s+', ' ', cleaned_content)  # Replace multiple spaces with single space
    
    # Try to parse content as Markdown
    try:
        md_content = Markdown(cleaned_content)
        panel = Panel(md_content, title=title, expand=False, border_style="cyan")
    except:
        # If parsing as Markdown fails, use plain text
        text_content = Text(cleaned_content)
        panel = Panel(text_content, title=title, expand=False, border_style="cyan")
    
    console.print(panel)

def prompt_for_webpage():
    predefined_urls = [
        "https://www.example.com",
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.wikipedia.org"
    ]
    
    while True:
        print("Choose a webpage to view:")
        for i, url in enumerate(predefined_urls, 1):
            print(f"{i}. {url}")
        print("0. Quit")
        
        choice = input("Enter your choice (0-5): ")
        if choice == '0':
            break
        
        try:
            url = predefined_urls[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")
            continue
        
        content = expand_and_view_webpage(url)
        display_webpage_content(url, content)
        
        continue_viewing = input("Would you like to view another webpage? (y/n): ") 
        if continue_viewing.lower() != 'y':
            break

if __name__ == "__main__":
    prompt_for_webpage()
