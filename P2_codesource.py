import requests
import csv
from bs4 import BeautifulSoup as BS
import os


# Analyze a book's product page
def book_analyzer(target_url):
	response = requests.get(target_url)
	# Validity check
	if response.ok:
		book = {}
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
		# Returns the books dict
		return book


# Sends every book from the defined page to the Analyzer
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
	return booksfromcategory


# Analyze our page and goes to the next one if it features a next button
def send_page_to_scraper_and_try_to_find_next(url):
	response = requests.get(url)
	if response.ok:
		soup = BS(response.text, 'lxml')
		booklist = send_books_from_page_to_analyzer(url)
		# Si il y a un bouton :
		if soup.find('li', {'class': 'next'}) is not None:
			url_split = url.split('/')
			end_of_url = url_split[-1]
			next_page_button = soup.find('li', {'class': 'next'}).find('a')['href']
			next_page_url = url.replace(end_of_url, next_page_button)
			booklist.extend(send_page_to_scraper_and_try_to_find_next(next_page_url))
		return booklist


	# To check / create folders dynamically
def create_folder(directory):
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
	except OSError:
		print('ERROR while trying to create :' + directory)


	# Handles our images downloading
def download_product_image(img_url, book_title, category):
	response = requests.get(img_url)
	file = open('books_images\\' + category + '\\' + book_title + '.jpg', 'wb')
	file.write(response.content)
	file.close()


# Cleans our strings so we can use them as file/folder names without any glitch.
def clean_str(string):
	stripped_string = string.replace(' ', '_')
	pretty_string = ''.join(char for char in stripped_string if char.isalnum() or char == '_')
	return pretty_string


# Used to store our data into csv files.
# Also calls our img downloader on every book.
def write_in_csv(books):
	header = []
	rows = []
	if len(header) < 1:
		# Write header and file title from books[0]
		for keys in books[0]:
			header.append(keys)

	file_title = books[0]['category'].lower().replace(' ', '_')
	# Adding rows from books values
	for book in books:
		rows.append(book)
		download_product_image(book['image_url'], clean_str(book['title']), book['category'])

	with open('books_specs\\' + file_title + '.csv', 'w', encoding='UTF8', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=header)
		writer.writeheader()
		writer.writerows(rows)


	# Analyzes a category, creates an imgs folder for it, calls csv writer function
def analyze_category(category_url):
	category_books = send_page_to_scraper_and_try_to_find_next(category_url)
	# Creating a category folder for our books imgs before we write anything inside using books[0] as a sample
	create_folder('books_images\\' + category_books[0]['category'])
	write_in_csv(category_books)
	return category_books


def main():
	# Initializing our folders
	create_folder('./books_images')
	create_folder('./books_specs')
	website_url = "https://books.toscrape.com/"
	# Our list containing every book from the website
	all_books = []
	response = requests.get(website_url)
	number_of_categories = 0
	if response.ok:
		soup = BS(response.text, 'lxml')
		navlist = soup.find('ul', {'class': 'nav nav-list'}).findAll('a')

		for i in range(1, len(navlist)):
			number_of_categories += 1
			all_books.extend(analyze_category(website_url + navlist[i]['href']))


if __name__ == '__main__':
	main()
