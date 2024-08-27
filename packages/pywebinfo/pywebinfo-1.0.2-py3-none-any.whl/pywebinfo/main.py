import requests
from bs4 import BeautifulSoup

class PyWebInfo:
    """
    A class to extract basic information from a webpage.

    This class sends a GET request to the provided URL and parse HTML content
    to extract title, description, image, favicon of the webpage.

    Attributes:
        url (str): URL of the webpage.
        title (str | None): Title of the webpage (default is None).
        description (str | None): Description of the webpage (default is None).
        image (str | None): URL of the image associated with the webpage (default is None).
        favicon (str | None): URL of the favicon for the webpage (default is None).
    
    Args:
        url (str): URL of the webpage to extract information from.
    
    Example:
        >>> info = PyWebInfo('https://example.com')
        >>> print(info.title)
        >>> print(info.description)
    """
    url: str | None = None
    '''Full URL of the webpage.'''
    title: str | None = None
    '''Title of the webpage (default is None).'''
    description: str | None = None
    '''Description of the webpage (default is None).'''
    image: str | None = None
    '''URL of the image associated with the webpage (default is None).'''
    favicon: str | None = None
    '''Favicon for the webpage (default is None).'''


    def __init__(self, url: str) -> None:
        """
        Initialize the PyWebInfo object with given URL and extract webpage metadata.

        Args:
            url (str): URL of the webpage to extract information from.
        """
        self.url = url
        self.__run()
    

    def __run(self):
        try:
            r = requests.get(self.url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                self.url = r.url
                self.title = str(soup.title.string) or self.__get_metacontent(soup, 'title')
                self.description = self.__get_metacontent(soup, 'description')
                self.image = self.__get_metacontent(soup, 'image')
                self.favicon = self.__get_favicon(soup)
        except requests.exceptions.RequestException:
            pass
    
    
    def __get_metacontent(self, soup: BeautifulSoup, name: str):
        metatag = soup.find('meta', attrs={'name': name}) or \
            soup.find('meta', attrs={'name': f'og:{name}'}) or \
            soup.find('meta', attrs={'name': f'twitter:{name}'}) or \
            soup.find('meta', attrs={'property': f'og:{name}'}) or \
            soup.find('meta', attrs={'property': f'twitter:{name}'})
        if metatag:
            return metatag['content']
        
    
    def __get_favicon(self, soup: BeautifulSoup):
        icon = soup.find('link', attrs={'rel': 'shortcut icon'}) or \
            soup.find('link', attrs={'rel': 'icon'}) or \
            soup.find('link', attrs={'rel': 'apple-touch-icon'}) or \
            soup.find('link', attrs={'rel': 'mask-icon'})
        if icon:
            icon_url = icon['href']
            if icon_url[:4] == 'http':
                return icon_url
            icon_url = self.url + icon_url[1:]
            return icon_url
            
        
if __name__ == '__main__':
    test = PyWebInfo('https://www.python.org/')
    print('URL:', test.url)
    print('Title:', test.title)
    print('Description:', test.description)
    print('Image:', test.image)
    print('Icon:', test.favicon)