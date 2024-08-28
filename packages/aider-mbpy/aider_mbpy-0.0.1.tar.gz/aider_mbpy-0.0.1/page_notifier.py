from bs4 import BeautifulSoup, HTMLTreeBuilder
import requests

def notify_and_expand_page(url):
    """
    Notifies the user to open and expand a page, then uses BeautifulSoup to parse the HTML.
    
    Args:
    url (str): The URL of the page to open and expand.
    
    Returns:
    BeautifulSoup object: The parsed HTML of the expanded page.
    """
    print(f"Please open and expand the page at: {url}")
    input("Press Enter when you've expanded the page...")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser', builder=HTMLTreeBuilder())
    
    return soup

# Example usage
if __name__ == "__main__":
    url = "https://example.com"
    expanded_page = notify_and_expand_page(url)
    print(expanded_page.title.string)  # Print the page title as an example
