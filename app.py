from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup
import requests
import re
import unicodedata
import time
import ystockquote
from flask import Flask, render_template
import sys
import logging


app = Flask(__name__)
Bootstrap(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.route('/')
def show_news():
	display_date = time.strftime("%A %B %d")
	URL = 'https://www.google.com/finance/category_news?catid=TRBC%3A54&ei=khXDVOnREfCBsgfA7IHACw'
	response = requests.get(URL)
	soup = BeautifulSoup(response.content)
	story = {'title': None, 'link': None, 'ticker': None,'price':None,
         'market_cap':None,'avg_daily_vol':None,'eps':None,
         'fiftytwo_low':None,'fiftytwo_high':None,'exchange':None,
        'pe_ratio':None,'pe_growth_ratio':None,'short_ratio':None}
	stories = []
	for listing in soup.find_all('div',{'class':'g-section news sfe-break-bottom-16'}):
		headline = listing.find('span',{'class':'name'})
		clean = unicodedata.normalize('NFKD', headline.text).encode('ascii','ignore')
		stripped= clean.strip('\n')
		story['title'] = stripped
		story['link'] =headline.a['href']
		match = re.compile( "\((.*)\)" ).search(stripped)
		if match is not None:
			ticker = match.group(1)
			story['ticker'] = ticker
			if len(ticker)<6:
				ydata = ystockquote.get_all(ticker)
				story['price'] = ydata['price']
				story['exchange'] = ydata['stock_exchange']
				story['market_cap'] = ydata['market_cap']
				story['avg_daily_vol'] = ydata['avg_daily_volume']
				story['eps'] = ydata['earnings_per_share']
				story['fiftytwo_low'] = ydata['fifty_two_week_low']
				story['fiftytwo_high'] = ydata['fifty_two_week_high']
				story['pe_ratio'] = ydata['price_earnings_ratio']
				story['pe_growth_ratio'] = ydata['price_earnings_growth_ratio']
				story['short_ratio'] = ydata['short_ratio']
			else:
				story['ticker'] = None
		stories.append(story.copy())

	return render_template('index.html', estimates=stories, date = display_date)
    

if __name__ == '__main__':
	app.run()

