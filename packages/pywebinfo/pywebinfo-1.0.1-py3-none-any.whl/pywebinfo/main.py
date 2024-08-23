import requests
from bs4 import BeautifulSoup

class PyWebInfo:
    url: str = None
    title: str = None
    description: str = None
    image: str = None
    favicon: str = None

    def __init__(self, url: str):
        self.url = url
        self.__run()
    

    def __run(self):
        try:
            r = requests.get(self.url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                self.url = r.url
                self.title = soup.title.string or self.__get_metacontent(soup, 'title')
                self.description = self.__get_metacontent(soup, 'description')
                self.image = self.__get_metacontent(soup, 'image')
                self.favicon = self.__get_favicon(soup)
        except requests.exceptions.RequestException:
            pass
    
    
    def __get_metacontent(self, soup:BeautifulSoup, name:str):
        metatag = soup.find('meta', attrs={'name': name}) or \
            soup.find('meta', attrs={'name': f'og:{name}'}) or \
            soup.find('meta', attrs={'name': f'twitter:{name}'}) or \
            soup.find('meta', attrs={'property': f'og:{name}'}) or \
            soup.find('meta', attrs={'property': f'twitter:{name}'})
        if metatag:
            return metatag['content']
        
    
    def __get_favicon(self, soup:BeautifulSoup):
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