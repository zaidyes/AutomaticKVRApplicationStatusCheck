import sys, getopt
import os.path
import mechanize
from bs4 import BeautifulSoup
import smtplib
from enum import Enum

class State(Enum):
	READY = 0
	NOT_READY = 1
	FAILURE = 2
	UNKNOWN

class Result(object):
	def __init__(self, code, state, message):

def main(argv):


# Get file as input parameter
argLen = len(sys.argv)
if argLen < 2:
	print 'Please run the script again passing abhol number file as arguement'
	sys.exit(2)
else:
	fileName = str(sys.argv[1])

if os.path.isfile(fileName):
	print 'reading abhol numbers from: ' + fileName
else:
	print 'invalid file: ' + fileName
	sys.exit(2)

if os.stat(fileName).st_size == 0:
	print 'Empty file: ' + fileName
	sys.exit(2)

# Open a browser 
br = mechanize.Browser()
br.open("https://www17.muenchen.de/EATWebSearch/")

assert br.viewing_html()

# Read the codes in the file line by line
with open(fileName) as file:
	content = file.readlines()

content = [x.strip() for x in content]

# Create a list to store results we want to email
toEmail = []
def getCodeResults(content, results):

# Check each code's status and deal accordingly
for code in content:
	br.select_form(name='mainForm')
	br.form['zapnummer'] = code
	br.submit()

	response = br.response().read()
	soup = BeautifulSoup(response, "lxml")

	#result = soup.find(string='liegt noch nicht zur Abholung bereit')
	#result = soup.find(string='wurde bereits ausgehandigt')
	#answers = soup.find_all("td", attrs={"class":"Font2b"})
	answers = soup.find_all("font", attrs={"color":"red"})
	count = len(answers)
	if count != 0 :
		print 'failure for code: ' + code + ' | answer: ' + answers[count-1].string
		continue

	answers = soup.find_all("font", attrs={"color":"green"})
	count = len(answers)
	if count != 0 :
		success = 'ready for code: ' + code + ' | answer: ' + answers[count-1].string
		print success
		toEmail.append(success)
		continue

	answers = soup.find_all("font", attrs={"color":"black"})
	count = len(answers)
	if count != 0 :
		print 'not ready for code: ' + code + ' | answer: ' + answers[count-1].string
		continue
	
	print 'Unknown scenario: ' + soup


if(toEmail.count)
# Email the results if necessary
fromaddr = 'user_me@gmail.com'
toaddrs  = 'user_you@gmail.com'