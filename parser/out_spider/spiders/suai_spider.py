import scrapy
from urllib.parse import urljoin, urlparse
import csv
import os
import hashlib
from scrapy.pipelines.files import FilesPipeline
import requests


class LinkParserSpider(scrapy.Spider):
    name = 'link_parser'
    start_urls = []
    output_file = "out_spider/spiders/links.csv"
    html_folder = "saved_html_pages"
    files_folder = "downloaded_files"

    visited = set()
    file_links = set()

    file_extensions = [".pdf", ".docx"]  # Массив для фильтрации файлов по расширениям
    allowed_extensions = [".pdf", ".docx", ".html"]

    def __init__(self, start_urls=None, output_file=None, *args, **kwargs):
        super(LinkParserSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = [start_urls]
        if output_file:
            self.output_file = output_file

        os.makedirs(self.html_folder, exist_ok=True)
        os.makedirs(self.files_folder, exist_ok=True)

    def parse(self, response):
        self.save_html_page(response.url, response.body)

        if response.status == 404:
            self.logger.warning(f"Страница не найдена: {response.url}")
            return

        links = response.css('a::attr(href)').getall()

        for link in links:
            if link:
                try:
                    full_url = response.urljoin(link)

                    # Пропускаем уже посещенные URL
                    if full_url in self.visited:
                        continue

                    self.visited.add(full_url)

                    # Проверяем на PDF или DOCX
                    is_pdf = full_url.lower().endswith('.pdf')
                    is_docx = full_url.lower().endswith('.docx')

                    if is_pdf or is_docx:
                        file_type = "pdf" if is_pdf else "docx"
                        self.file_links.add(full_url)
                        self.save_link(full_url, file_type)

                        # # Пробуем скачать файл
                        # self.download_file(full_url, file_type)

                    elif full_url.lower().endswith('.html') or urlparse(full_url).netloc == urlparse(
                            self.start_urls[0]).netloc:
                        # Внутренние страницы продолжаем обходить
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse,
                            errback=self.handle_error
                        )

                except Exception as e:
                    self.logger.error(f"Ошибка при обработке ссылки {link}: {e}")

    def save_html_page(self, url, html_content):
        try:
            file_name = hashlib.md5(url.encode('utf-8')).hexdigest() + ".html"
            file_path = os.path.join(self.html_folder, file_name)

            with open(file_path, 'wb') as f:
                f.write(html_content)

            self.logger.info(f"Сохранена HTML-страница: {file_path}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения HTML: {e}")

    def save_link(self, url, link_type):
        """Сохраняем ссылку в CSV"""
        try:
            with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([url, link_type])

            self.logger.info(f"Сохранена ссылка ({link_type}): {url}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения ссылки: {e}")

    def handle_error(self, failure):
        """Обработка ошибок запроса"""
        self.logger.error(f"Ошибка запроса: {failure.value}")

    def closed(self, reason):
        self.logger.info(f"Парсинг завершён. Всего найдено {len(self.visited)} ссылок, {len(self.file_links)} файлов.")
