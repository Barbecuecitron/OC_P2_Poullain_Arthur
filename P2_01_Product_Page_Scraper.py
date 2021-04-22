import requests
from bs4 import BeautifulSoup as BS


def main():
	url = 'http://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html'
	response = requests.get(url)
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
		# Making the function return the book dict so I can retrieve it later on
		return book


if __name__ == '__main__':
	print(main())
