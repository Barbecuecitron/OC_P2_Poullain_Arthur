import requests
from bs4 import BeautifulSoup as BS


# Analyze a book's product page
def book_analyzer(target_url):
	response = requests.get(target_url)
	book = {}
	# Validity check
	if response.ok:
		soup = BS(response.text, 'lxml')
		book['product_page_url'] = response.url
		book['title'] = soup.find('h1').text
		if soup.find('div', {'id': 'product_description'}) is None:
			book['product_description'] = 'No desc available'
		else:
			book['product_description'] = soup.find('div', {'id': 'product_description'}).findNext('p').text

		book['category'] = soup.find('ul', {'class': 'breadcrumb'}).findAll('li')[2].text.strip()
		book['review_rating'] = 0
		product_main_cols = soup.find('div', {'class': 'col-sm-6 product_main'}).findAll('p')

		# Retrieving product rating by class to avoid updates errors
		for infos in product_main_cols:
			if infos['class'][0] != 'star-rating':
				pass
			else:
				book['review_rating'] = infos['class'][1]

		book['image_url'] = soup.findAll('img')[0]['src'].replace('../../', 'http://books.toscrape.com/')

		# Dictionnary to loop, compare & translate the website indexes we need
		specs_to_keep = {
			'UPC': 'universal_product_code',
			'Price (incl. tax)': 'price_including_tax', 'Price (excl. tax)': 'price_excluding_tax',
			'Availability': 'number_available'
			}
		desc_specs = soup.find('table', {'class': 'table table-striped'}).findAll('th')
		desc_values = soup.find('table', {'class': 'table table-striped'}).findAll('td')
		for i in range(0, len(desc_specs)):
			if desc_specs[i].text in specs_to_keep:
				book[specs_to_keep[desc_specs[i].text]] = desc_values[i].text

		book['price_including_tax'] = book['price_including_tax'].replace('Â', '')
		book['price_excluding_tax'] = book['price_excluding_tax'].replace('Â', '')
		# Making the function return the book dict so I can retrieve it later on
		return book

# Sends every book from the defined page to the
def send_books_from_page_to_analyzer(link):
	booksfromcategory = []
	base_link = 'http://books.toscrape.com/catalogue/'
	print(' Currently Analyzing : ' + link)
	response = requests.get(link)
	if response.ok:
		soup = BS(response.text, 'lxml')
		product_pages_finder = soup.findAll('h3')
		for product_page in product_pages_finder:
			product_page_link = base_link + product_page.find('a')['href'].replace('../../../', '')
			booksfromcategory.append(book_analyzer(product_page_link))
	# Returns a dictionnary of the category containing every needed book as subdictionnaries -- WORKING
	return booksfromcategory


# Analyze our page and goes to the next one if it features a next button
def send_page_to_scraper_and_try_to_find_next(url):
	response = requests.get(url)
	category_link ="https://books.toscrape.com/catalogue/category/books/"
	if response.ok:
		soup = BS(response.text, 'lxml')
		booklist = send_books_from_page_to_analyzer(url)
		# Si il y a un bouton :
		if soup.find('li', {'class': 'next'}) is not None:
			url_split = url.split('/')
			end_of_url = url_split[-1]
			next_page_button = soup.find('li', {'class': 'next'}).find('a')['href']
			next_page_url = url.replace(end_of_url, next_page_button)
			#newurl = url.replace('index.html', nextpagebutton)
			#print("Mon url = ", url)
			booklist.extend(send_page_to_scraper_and_try_to_find_next(next_page_url))
		return booklist


def main():
	# Initializing a book list to use as parameter for recursivity
	recursive_booklist = []
	all_books = send_page_to_scraper_and_try_to_find_next('https://books.toscrape.com/catalogue/category/books/default_15/index.html')
	print(all_books)


if __name__ == '__main__':
	main()
