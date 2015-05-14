import urllib2
import urllib
import os
import time
import string
from bs4 import BeautifulSoup

latest_margin_file = '/home/rushiraj/workspace/stock/data/latest_margin.csv'
z_margin_url = 'https://zerodha.com/margin-calculator/Equity/'


def get_hist_data(exchange,script,date=''):
	hist_url = 'https://www.google.com/finance/historical?q=' + exchange + ':' + urllib.quote(script)
	hist_file_main = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv'
	hist_page = urllib2.urlopen(hist_url)
	hist_pg = BeautifulSoup(hist_page.read())

	if date == '':
		fd = open(hist_file_main,'w')
		fd.close()
	for data_row in hist_pg.find_all('table'):
		for data in data_row.find_all('tr'):
			row = ""
			foundDate = 'false';
			for i in data.find_all('td'):
				if i.get('class') == ['lm']:
					row = row + i.text.strip() + ","
					if date != '' and i.text.strip() == date : 
						foundDate = 'true';
				if i.get('class') == ['rgt']:
					value = i.text.replace(",","")
					value = value.strip()
					row = row + value + ","
				if i.get('class') == ['rgt rm']:
					value = i.text.replace(",","")
					value = value.strip()
					row = row + value + ","
			if foundDate == 'true':
				return row;
			if row != "":
				fd = open(hist_file_main,'a')
				fd.write(row+"\n")
				fd.close()


def append_data_at_begining(exchange,script,todays_Data):

	hist_file_main = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv'
	hist_file_temp = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv_temp'

	if todays_Data in open(hist_file_main).read():
		print "Data for this date is already there."
		return

	temp_file=open(hist_file_temp,'w')
	temp_file.write(todays_Data+"\n")

	main_file= open(hist_file_main,'r')
	temp_file.write(main_file.read())
	main_file.close()

	temp_file.close()

	os.remove(hist_file_main)
	os.rename(hist_file_temp,hist_file_main)

def append_todays_hist_data(exchange,script):

	hist_file_main = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv'
	todays_date = time.strftime("%b %d, %Y")
#	todays_date = 'May 13, 2015'

	if todays_date in open(hist_file_main).read():
		print "Data for this date is already there."
		return
	else:
		todays_Data = get_hist_data(exchange,script,todays_date)
		append_data_at_begining(exchange,script,todays_Data)


#def get_hist_data_bse(script):
#	hist_url = 'http://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?scripcode='+script+'&flag=sp&Submit=G'
#	hist_file_main = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv'
#	hist_page = urllib2.urlopen(hist_url)
#	hist_pg = BeautifulSoup(hist_page.read())
#
#	
#	fd = open(hist_file_main,'w')
#	fd.close()
#	for data_row in hist_pg.find_all('tr'):
#		if data_row.get('class') == ['TTRow']:
#			data_field =  data_row.find_all('td')
#			date=data_field[0].text.strip()
#			open_v=data_field[1].text.strip()
#			high=data_field[2].text.strip()
#			low=data_field[3].text.strip()
#			close=data_field[4].text.strip()
#			WAP=data_field[5].text.strip()
#			number_of_shares=data_field[6].text.strip()
#			number_of_trades=data_field[7].text.strip()
#			total_turnover=data_field[8].text.strip()
#			dev_qty=data_field[9].text.strip()
#			dev_per=data_field[10].text.strip()
#			high_low_diff=data_field[11].text.strip()
#			open_close_diff=data_field[12].text.strip()
#			fd = open(hist_file_main,'a')
#			fd.write(date+","+open_v+","+high+","+low+","+close+","+WAP+","+number_of_shares+","+number_of_trades+","+total_turnover+","+dev_qty+","+dev_per+","+high_low_diff+","+open_close_diff+"\n")
#			fd.close()
#
#			
#
##			for data_field in data_row.find_all('td'):
##				print data_field.text.strip()
	

def create_g_url(exchange,scrip_code):
	return 'https://www.google.com/finance?q=' + exchange + ':' + scrip_code 

def get_current_stock_price(g_url):
	g_page = urllib2.urlopen(g_url)
	pg = BeautifulSoup(g_page.read())
	
	for data_field in pg.find_all('span'):
		if data_field.get('class') == ['pr']:
			return data_field.text.strip()

def get_lt_price_from_margin_file():
	margin_fp = open(latest_margin_file)
	for line in margin_fp:
		data = line.split(',')
		script_code = data[0].strip()
		margin = data[1].strip()
	#if margin == '9x':
		print script_code + " : " + get_current_stock_price(create_g_url('NSE',urllib.quote(script_code)))
	margin_fp.close()



def create_new_margin_file():
#print "Here we will create file"
	if os.path.exists(latest_margin_file):
		# change the name to old file
		os.rename(latest_margin_file, latest_margin_file + "_old" )
	# create new file
	fd = open(latest_margin_file,'w')
	fd.close()
	# Add in the log that file updated


def latest_z_margin():
	margin_page = urllib2.urlopen(z_margin_url)
	soup = BeautifulSoup(margin_page.read())

	create_new_margin_file()
	fd = open(latest_margin_file,'w')

	for row in soup.find_all('tr'):
		if row.get('data-scrip') != None:
			script_name = row.get('data-scrip')
			for subrow in row.find_all('td'):
				if subrow.get('class') == ['mis']:
					margin = subrow.text.strip()
					fd.write(script_name + "," + margin + "\n")
	fd.close()
	   
def apply_cam_formula(high_day,low_day,close_day):
	
	high = float(high_day)
	low = float(low_day)
	close = float(close_day)

	H4 = close+(0.55*(high-low))
	H3 = close+(0.275*(high-low))
	H2 = close+(0.183*(high-low))
	H1 = close+(0.0916*(high-low))

	L1 = close-(0.0916*(high-low))
	L2 = close-(0.183*(high-low))
	L3 = close-(0.275*(high-low))
	L4 = close-(0.55*(high-low))

	H3L3_diff = H3-L3
	H4L4_diff = H4-L4

	H3L3_percentage = H3L3_diff * 100 / close
	H4L4_percentage = H4L4_diff * 100 / close

	data = "%s,%s,%s,%s,%s,%s,%s,%s" % (H4, H3, L3, L4, H3L3_diff, H4L4_diff, H3L3_percentage, H4L4_percentage)
	return data

def apply_cammerila(exchange, script,date=''):
	
	hist_file_main = '/home/rushiraj/workspace/stock/data/main_HIST_'+script+'.csv'
	cam_dir =  '/home/rushiraj/workspace/stock/data/'

	hist_fp = open(hist_file_main,'r')
	if date == '':
		first_line = hist_fp.readline();
		data_line= first_line
	else:
		for line in hist_fp:
			if date in line:
				data_line = line
	hist_fp.close()

	if data_line != '':
		data = data_line.split(',')
		date = "%s_%s" % (data[0], data[1].strip())
		cam_data = apply_cam_formula(data[3],data[4],data[5])
		cam_file = "%scam_%s.csv" % (cam_dir,date.replace(' ','_'))
		fd = open(cam_file,'a')
		fd.write("%s,%s,%s\n" % (script, date, cam_data))
		fd.close()




###########################################################
margin_fp = open(latest_margin_file,'r')

exchange = 'NSE'

for line in margin_fp:
	data = line.split(',')
	script = data[0].strip()
	margin = data[1].strip()
#	get_hist_data(exchange, script)
#	append_todays_hist_data(exchange, script)
	apply_cammerila(exchange, script,'May 13, 2015')

margin_fp.close()
##########################################################


#latest_z_margin()							


#url = create_g_url('BOM','523204')	   
#url = create_g_url('NSE',urllib.quote('ALSTOMT&D'))
#url = urllib.quote(url,':/?=') # this will not quote specified character in the url
#lt_price = get_current_stock_price(url)
