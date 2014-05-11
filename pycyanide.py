import urllib
from bs4 import BeautifulSoup as Soup
import lxml
import os
import sys
import time
import sqlite3

archive_url = ""

def get_soup(url):
	try:
		page = urllib.urlopen(url).read()
	except Exception:
		sys.exit('\tThere seems to a problem with your internet connection or the Universe hates you. Basically you suck! :P')
	soup = Soup(page)
	return soup

def insert_db(links):
	db = sqlite3.connect('links.sqlite')
	cursor = db.cursor()
	comics = list()
	for link in links:
		num = link[len("http://explosm.net/comics/"):-len("/")]
		num = int(num)
		#comics.append((num,link))
		try:
			cursor.execute('INSERT INTO cyanide(comic_num,comic_link) VALUES(?,?)',(num,link,))
			db.commit()
			print str((num,link)) + " insert -- SUCCESS!"
		except Exception:
			db.rollback()
			#print str((num,link)) + " insert -- FAILURE!"
	db.close()
	print "Database succesfully updated!"
	

def update_db():
	url = "http://explosm.net/comics/archive/"
	links = get_links(get_soup(url))
	db2 = sqlite3.connect('links.sqlite')
	cursor2 = db2.cursor()
	cursor2.execute("SELECT MAX(comic_num) FROM cyanide WHERE DOne='True'")
	comic = cursor2.fetchone()
	db2.close()
	comic_num = comic[0]
	new_links = list()
	for link in links:
		num=link[len('http://explosm.net/comics/'):-1]
		num=int(num)
		if num>comic_num:
			new_links.append(link)
			print link
	insert_db(new_links)

def get_links(soup):
	links = list()
	for link in soup.find_all('a')[21:(len(soup.find_all('a'))-8)]:#archive-2014
		links.append("http://explosm.net"+link.get('href'))
	return links

def get_links_from_db():
	db = sqlite3.connect('links.sqlite')
	cursor = db.cursor()
	done_links = list()
	cursor.execute('''SELECT comic_num,comic_link FROM cyanide WHERE Done='True' ''')
	done_links = cursor.fetchall()
	cursor.execute('SELECT comic_num,comic_link,Done FROM cyanide')
	links = list()
	links = cursor.fetchall()
	undone_links = list()
	cursor.execute('''SELECT comic_num,comic_link FROM cyanide WHERE Done='False' ''')
	undone_links = cursor.fetchall()
	db.close()
	links.reverse()
	elif len(done_links)>len(undone_links):
		for link in links:
			comic_num = link[0]
			comic_link = link[1]
			bool_done = link[2]
			if bool_done == 'False':
				#if comic_num == 3544:
					#cursor.execute('DELETE FROM cyanide WHERE comic_num=?',(comic_num,))
				#	continue
				#elif comic_num == 3548 or comic_num == 3547 or comic_num == 3546 or comic_num == 3545:
				#	continue   
				check_link(comic_num,comic_link)
				time.sleep(30)

	else:	
		for link in links[len(done_links)-1:]:
			comic_num = link[0]
			comic_link = link[1]
			bool_done = link[2]
			if bool_done == 'False':
				#if comic_num == 3544:
					#cursor.execute('DELETE FROM cyanide WHERE comic_num=?',(comic_num,))
				#	continue
				#elif comic_num == 3548 or comic_num == 3547 or comic_num == 3546 or comic_num == 3545:
				#	continue   
				check_link(comic_num,comic_link)
				time.sleep(30)

def download_comic(comic_num,comic_link):
	if not 'Comics' in os.getcwd():
		dirr = os.getcwd()
		os.chdir(dirr+'/Comics/')
	print str(comic_num) + "--" + comic_link
	soup = get_soup(comic_link)
	if "author" in soup.find_all('a')[9].get('href'):
		author = soup.find_all('a')[9].text.split()[0]
	elif not "author" in soup.find_all('a')[9].get('href'):
		#author = "Kris"
		#author = "Chaseweek"
		author = "guest4"
	save = "http://www.explosm.net/db/files/Comics/"+author+"/"
	comic_image = soup.find_all('img')[-8].get('src')
	file_name = str(comic_num) + "_" + author + "_" + soup.find_all('img')[-8].get('src')[len(save):]
	file_name = file_name.replace("/","_")
	try:
		comic = urllib.urlopen(comic_image).read()
		#comic = requests.get(comic_image)
	except Exception, e:
		raise e
		#sys.exit("Failure to open the comic image. Your internet sucks!")
	if not os.path.exists(file_name):
		f = open(file_name,"w")
		f.write(comic)
		f.close()
		print "\t" + file_name + " saved! -- SUCCESSFULLY!"
	else:
		print "\t" + file_name + " skipped! -- FILE ALREADY EXISTS!"
	
	if 'Comics' in os.getcwd():
		dirr = os.getcwd()
		os.chdir(dirr[:-len('Comics/')])
	db = sqlite3.connect('links.sqlite')
	cursor = db.cursor()
	cursor.execute('UPDATE cyanide SET Done = ? WHERE comic_num = ?',('True',comic_num,))
	print "\tUpdated "+ str(comic_num) +" succesfully!"
	db.commit()
	db.close()

def check_link(comic_num,comic_link):
	try:
		comic = urllib.urlopen(comic_link).read()
	except Exception:
		sys.exit('\tThere seems to a problem with your internet connection or the Universe hates you. Basically you suck! :P')
	comic_soup = Soup(comic)
	error = 'OH NOES!!! WAHT YOU DOEN!!?Comic could not be found.'
	soup = get_soup(comic_link)
	imgs = soup.find_all('img')
	db = sqlite3.connect('links.sqlite')
	cursor = db.cursor()
	if error == soup.find(id="maincontent").text.rstrip():
		try:
			cursor.execute('DELETE FROM cyanide WHERE comic_num=?',(comic_num,))
			print "DELETED " + str(comic_num) + " from cyanide.sqlite because COMIC does not exist! -- SUCCESS!"
			db.commit()
		except Exception:
			print "DELETED " + str(comic_num) + " from cyanide.sqlite because COMIC does not exist! -- FAILED!"
			db.rollback()

	elif soup.find_all('img')[9].get('src') == '/comics/play-button.png' or soup.find_all('img')[-8].get('src') == '/comics/play-button.png':
		try:
			cursor.execute('DELETE FROM cyanide WHERE comic_num=?',(comic_num,))
			print "DELETED " + str(comic_num) + " from cyanide.sqlite because it is a VIDEO! -- SUCCESS!"
			db.commit()
		except Exception:
			print "DELETED " + str(comic_num) + " from cyanide.sqlite because it is a VIDEO! -- FAILED!"
			db.rollback()
	else:
		#valid comic
		download_comic(comic_num,comic_link)
	db.close()
		
def main():
	print "CYANIDE & HAPPINESS COMICS DOWNLOADER v2.01a"
	print '\tChoices:\n\t\t1.Update the DATABASE with the LATEST comics, if available.\n\t\t2.Download comics which have not been downloaded.'
	choice = input('\t\tEnter choice : ')
	if choice == 1:
		update_db()
	elif choice == 2:
		get_links_from_db()


if __name__ == '__main__':
	main()