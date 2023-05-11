from bs4 import BeautifulSoup as bs
from urllib import request
import re
from csv import writer

numerical_words = {
  "one": 1,
  "two": 2,
  "three": 3,
  "four": 4,
  "five": 5
}

URL = "https://books.toscrape.com/"

with open('books.csv', 'w') as output_file:
  to_csv = writer(output_file)
  headers = ['image_url', 'star_rating', 'price', 'in_stock?', 'category', 'page_url']
  to_csv.writerow(headers)

  response = request.urlopen(URL)
  document = bs(response, "html.parser")

  categories = document.find(class_="nav nav-list").li.ul
  categories = categories.find_all("li")

  def book_scraper(url, next_page=''):
    print(f"Scraping {url}{next_page}")
    
    response = request.urlopen(url + next_page)
    document = bs(response, "html.parser")

    books = document.select("article.product_pod")
    category = document.find("h1").string
    paginator = document.find("ul", class_="pager")

    next_page_element = paginator and paginator.find("a", string="next")
    next_page = next_page_element['href'] if next_page_element else ''

    for book in books:
      image_element = book.find("img")

      image_url = URL + image_element['src'].replace('../', '')
      rating = book.find("p", class_=re.compile("star-rating.*", flags=re.IGNORECASE))['class'][1].lower()
      rating_number = numerical_words[rating]
      price = book.find("p", class_=re.compile("price.*", flags=re.IGNORECASE)).string
      stock_status = book.find("p", class_=re.compile(".*availability", flags=re.IGNORECASE)).get_text().strip().lower() == "in stock"
      page_url = URL + 'catalogue/' + book.find("h3").a['href'].replace('../', '')

      to_csv.writerow([image_url, rating_number, price, stock_status, category, page_url])

    if next_page:
      return book_scraper(url, next_page)
    else:
      print(f"Done with {category}!")

  for category in categories:
    url = URL + category.a['href'].replace('index.html', '')
    book_scraper(url)

  print("All done!")