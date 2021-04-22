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
		# Does it have a description ?
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
		specs_to_keep = {'UPC': 'universal_product_code', 'Product Type': False,
						 'Price (incl. tax)': 'price_including_tax', 'Price (excl. tax)': 'price_excluding_tax',
						 'Tax': False, 'Availability': 'number_available', 'Number of Reviews': False}

		desc_specs = soup.find('table', {'class': 'table table-striped'}).findAll('td')
		index = 0
		for spec in specs_to_keep:
			if specs_to_keep[spec] is not False:
				# print(specs_to_keep[spec] + ' = ' + desc_specs[index].text)
				book[specs_to_keep[spec]] = desc_specs[index].text
			index += 1
		# Translation of weird symbol before '£'
		book['price_including_tax'] = book['price_including_tax'].replace('Â', '')
		book['price_excluding_tax'] = book['price_excluding_tax'].replace('Â', '')
		# Returns the book dict with every scraped info -- WORKING
		return book
#def csv_magic(category_books):
#	print(category_books)

def find_all_books_from_category(pages_to_analyze):
	booksfromcategory = []
	print('We will analyze' , pages_to_analyze)
	linkBegin = 'http://books.toscrape.com/catalogue/'
	for link in pages_to_analyze:
		print(' Currently Analyzing : ' + link)
		response = requests.get(link)
		if response.ok:
			soup = BS(response.text, 'lxml')
			product_pages_finder= soup.findAll('h3')
			for product_page in product_pages_finder:
				product_page_link = linkBegin + product_page.find('a')['href'].replace('../../../', '')
				booksfromcategory.append(book_analyzer(product_page_link))
	print('This return is working properly')
	# Returns a dictionnary of the category containing every needed book as subdictionnaries -- WORKING
	return booksfromcategory


# Counts pages and call find_all_books_from_category when done
def count_pages(url,pagesurl):
	response = requests.get(url)
	pagesurl.append(url)
	if response.ok:
		soup = BS(response.text, 'lxml')
		# Checks if a next button exists & re-calls itself if so
		if soup.find('li', {'class': 'next'}) is not None:
			nextpagebutton = soup.find('li', {'class': 'next'}).find('a')['href']
			newurl = url.replace('index.html', nextpagebutton)
			count_pages(newurl,pagesurl)
		else:
			print(str(len(pagesurl)) + ' page(s) successfully found.')
			books_dictionnary = find_all_books_from_category(pagesurl)
			# If we print book_dictionnary here, we can see it is perfect, but I can't return it for some reason,
			# Whenever I try to get the value returned by this function, I do get a None Type.
			# But printing it here works fine and delivers it the way it should.
			return books_dictionnary


def main():
	pagesurl = []
	all_books = count_pages('http://books.toscrape.com/catalogue/category/books/romance_8/index.html', pagesurl)
	print(all_books)


if __name__ == '__main__':
	main()