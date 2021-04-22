import requests
from bs4 import BeautifulSoup as BS
import csv

websiteURL = 'http://books.toscrape.com/'
blacklisted = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
categories = []
numberofbooks = 0
numberofcategories = 0
header = []
rows = []


def bookanalyzer(target_url):
	print("Searching book infos of following page : " + target_url)
	response = requests.get(target_url)
	if response.ok:
		book = {}
		soup = BS(response.text, 'lxml')
		# Getting URL with requests
		book['product_page_url'] = response.url
		# Targeted Infos scraping
		book['title'] = soup.find('div', {'class': 'col-sm-6 product_main'}).find('h1').text
		if soup.find('div', {'id': 'product_description'}) is None:
			book['product_description'] = 'No desc available'
		else:
			book['product_description'] = soup.find('div', {'id': 'product_description'}).findNext('p').text
		book['category'] = soup.find('ul', {'class': 'breadcrumb'}).findAll('li')[2].text.strip()
		book['review_rating'] = soup.find('p', {'class': 'instock availability'}).findNext('p')['class'][1]
		book['image_url'] = soup.findAll('img')[0]['src'].replace('../../', 'http://books.toscrape.com/')

		# Targeted infos in desc. scraping
		desc_specs = soup.find('table', {'class': 'table table-striped'}).findAll('td')
		book['universal_product_code'] = desc_specs[0].text
		# Remove the weird symbol before ''
		book['price_including_tax'] = desc_specs[3].text.replace('Â', '')
		book['price_including_tax'] = desc_specs[2].text.replace('Â', '')
		book['number_available'] = desc_specs[5].text

		if len(header) < 1:
			print('Header est < 1 on le crée')
			for keys in book:
				header.append(keys)
				print(keys)
		file_title = book['category'].lower().replace(' ', '_')

		with open(file_title + '.csv', 'w', encoding='UTF8', newline='') as f:
			rows.append(book)

			writer = csv.DictWriter(f, fieldnames=header)
			writer.writeheader()
			writer.writerows(rows)


	# Retrieve every product links from a defined page
def findallbooksfromcategory(category_url):
	global numberofbooks
	response = requests.get(category_url)
	if response.ok:
		soup = BS(response.text, 'lxml')
		product_page_link_finder = soup.findAll('h3')

		for link in product_page_link_finder:
			# Translating html link to true link
			cleanlink = websiteURL + '/catalogue/' + link.find('a')['href'].replace('../../../', '')
			bookanalyzer(cleanlink)
			print(cleanlink)
			numberofbooks = numberofbooks + 1
	print(str(numberofbooks) + ' books were found accross', numberofcategories, 'categories')


def analyzecategory(url):
	response = requests.get(url)
	if response.ok:
		soup = BS(response.text, 'lxml')
		# Check if there are multiple pages
		if soup.find('li', {'class': 'current'}) is not None:
			find_nbrpages = soup.find('li', {'class': 'current'}).text.strip()
			nbrpages = find_nbrpages[-1]
			for page in range(1, int(nbrpages) + 1):
				newurl = url.replace('index', 'page-' + str(page))
				findallbooksfromcategory(newurl)
		# If not, we don't need a loop and will call our function on the actual URL
		else:
			findallbooksfromcategory(response.url)


# finds every category from the website
def main():
	response = requests.get(websiteURL)
	global numberofcategories
	print('Finding Book categories')
	if response.ok:
		soup = BS(response.text, 'lxml')
		navlist = soup.find('ul', {'class': 'nav nav-list'}).findAll('a')
		for i in range(1, len(navlist)):
			numberofcategories += 1
			analyzecategory(websiteURL + navlist[i]['href'])


main()
