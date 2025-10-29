# spiders/content_spider_html.py
import scrapy
import re
from urllib.parse import urlparse
from out_spider.items import ContentItem
from bs4 import BeautifulSoup

class ContentSpider(scrapy.Spider):
    name = 'content_spider'

    def __init__(self, start_urls=None, *args, **kwargs):
        super(ContentSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = start_urls.split(',')
        else:
            self.start_urls = self.load_links()

    def load_links(self):
        try:
            with open('links.csv', 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f.readlines() if line.strip()]
                print(f"Загружено {len(links)} ссылок из links.csv")
                return links
        except FileNotFoundError:
            print("Файл links.csv не найден")
            return []

    def parse(self, response):
        item = ContentItem()
        item['url'] = response.url
        item['content_type'] = 'html' # Тип файла
        item['filename'] = self.generate_filename(response.url)

        # Очищаем HTML
        item['raw_content'] = response.body.decode('utf-8')  # Преобразуем в строку и сохраняем исходный HTML
        item['cleaned_content'] = self.clean_html(response.body)  # Очищенный HTML
        item['text_content'] = self.extract_text(response)  # Извлекаем текст

        yield item

    def generate_filename(self, url):
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'

        # Заменяем недопустимые символы
        filename = path.replace('/', '_').replace('\\', '_')
        return filename

    def clean_html(self, html):
        # Очистка HTML от ненужных тегов и элементов
        cleaned_html = re.sub(r'<(script|style|noscript).*?>.*?</\1>', '', html.decode('utf-8'),
                              flags=re.DOTALL)  # Удаляем скрипты, стили, noscript
        cleaned_html = re.sub(r'<!--.*?-->', '', cleaned_html, flags=re.DOTALL)  # Удаляем комментарии
        cleaned_html = re.sub(r'<div class="ads">.*?</div>', '', cleaned_html,
                              flags=re.DOTALL)  # Удаляем рекламные блоки (если есть)
        return cleaned_html


    def extract_text(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        # Удаляем ненужные элементы: скрипты, стили, если они есть
        for element in soup(['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'aside', 'form']):
            element.decompose()

        # Таргетируем основной контент:
        # Допустим, основной текст находится в <div class="content"> или <main>
        main_content = soup.find(['div', 'main', 'article'], class_=['content', 'post', 'article', 'main'])

        # Если найден основной блок, извлекаем текст
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            # Если не нашли целевой блок, извлекаем текст с всей страницы
            text = soup.get_text(separator=' ', strip=True)

        cleaned_text = ' '.join(text.split())
        return cleaned_text
