import scrapy
import json
import os

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']
    
    def __init__(self):
        # Buat folder data jika belum ada
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def parse(self, response):
        # Ambil semua link buku pada halaman
        books = response.css('article.product_pod')
        
        for book in books:
            book_url = book.css('h3 a::attr(href)').get()
            if book_url:
                book_url = response.urljoin(book_url)
                yield response.follow(book_url, self.parse_book)
        
        # Navigasi ke halaman berikutnya
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_book(self, response):
        # Fungsi untuk mengkonversi rating bintang ke angka
        def get_rating_number(rating_text):
            ratings = {
                'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
            }
            return ratings.get(rating_text, 0)
        
        # Ambil informasi rating
        rating_class = response.css('p.star-rating::attr(class)').get()
        rating_text = rating_class.split()[-1] if rating_class else ''
        rating_number = get_rating_number(rating_text)
        
        # Ambil informasi ketersediaan
        availability_text = response.css('p.availability::text').getall()
        availability = ''.join(availability_text).strip()
        
        # Ambil informasi dari tabel product information
        product_info = {}
        rows = response.css('table.table-striped tr')
        for row in rows:
            key = row.css('td:first-child::text').get()
            value = row.css('td:last-child::text').get()
            if key and value:
                product_info[key.strip()] = value.strip()
        
        yield {
            'title': response.css('h1::text').get(),
            'price': response.css('p.price_color::text').get(),
            'availability': availability,
            'rating': rating_number,
            'rating_text': rating_text,
            'description': response.css('#product_description + p::text').get(),
            'image_url': response.urljoin(response.css('div.image_container img::attr(src)').get()),
            'product_info': product_info,
            'url': response.url
        }
