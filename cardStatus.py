import sys, getopt
import os.path
import mechanize
from bs4 import BeautifulSoup
import smtplib
from enum import Enum

class Status(Enum):
	READY = 0
	NOT_READY = 1
	FAILURE = 2
	UNKNOWN = 3

class Result(object):

	def __init__(self, code, status, message):
		self.code = code
		self.status = status
		self.message = message

# Get file as input parameter
argLen = len(sys.argv)
if argLen < 2:
	print 'Please run the script again passing abhol number file as arguement'
	sys.exit(2)
else:
	fileName = str(sys.argv[1])

def validateCodeFile(fileName):
	if not fileName:
		print 'Empty code file name'
		return False

	if os.path.isfile(fileName):
		print 'valid file: ' + fileName
	else:
		print 'invalid file: ' + fileName
		return False
		
	if os.stat(fileName).st_size == 0:
		print 'Empty file: ' + fileName
		return False

	return True

# Read and parse codes from file
def getCodesFromFile(fileName):
	# Read the codes in the file line by line
	with open(fileName) as file:
		content = file.readlines()

	content = [x.strip() for x in content]
	return content

# Get the Results given the codes
def getCodeResults(content):
	results = []

	# Open a browser 
	br = mechanize.Browser()
	br.open("https://www17.muenchen.de/EATWebSearch/")

	assert br.viewing_html()

	# Check each code's status and deal accordingly
	for code in content:
		br.select_form(name='mainForm')
		br.form['zapnummer'] = code
		br.submit()

		response = br.response().read()
		soup = BeautifulSoup(response, "lxml")

		answers = soup.find_all("font", attrs={"color":"red"})
		count = len(answers)
		if count != 0 :
			result = Result(code, Status.FAILURE, answers[count-1].string)
			results.append(result)
			continue

		answers = soup.find_all("font", attrs={"color":"green"})
		count = len(answers)
		if count != 0 :
			result = Result(code, Status.READY, answers[count-1].string)
			results.append(result)
			continue

		answers = soup.find_all("font", attrs={"color":"black"})
		count = len(answers)
		if count != 0 :
			result = Result(code, Status.NOT_READY, answers[count-1].string)
			results.append(result)
			continue
		
		result = Result(code, Status.UNKNOWN, soup)
		results.append(result)

	return results

def main(argv):
	codeFile = ''
	emailFrom = ''
	emailTo = ''

	try:
		opts,args = getopt.getopt(argv,"hc:f:t:",["codefile=","emailfrom=", "emailto="])
	except getopt.GetoptError:
		print 'cardStatus.py -c <codefile> -f <emailfrom> -t <emailto>'
	  	sys.exit(2)

	for opt,arg in opts:
	    if opt == '-h':
	        print 'cardStatus.py -c <codefile> -f <emailfrom> -t <emailto>'
	        print 'example: cardStatus.py -c codefile.txt -f myemail@myemail.com -t youremail@youremail.com'
	        sys.exit()
	    elif opt in ("-c", "--codefile"):
	    	codeFile = arg
	    elif opt in ("-f", "--emailfrom"):
	    	emailFrom = arg
	    elif opt in ("-t", "--emailto"):
	    	emailTo = arg

	if not validateCodeFile(codeFile):
		print 'Please provide a valid code file see help'
		sys.exit(2)
	

	codes = getCodesFromFile(codeFile)
	if len(codes) < 1:
		print 'No codes found in file'
		sys.exit(2)

	results = getCodeResults(codes)
	if len(results) < 1:
		print 'No results could be computed please check internet connection'
		sys.exit(2)

	for result in results:
		print "Code: " + result.code + " | Status: " + str(result.status) + " | Message: " + result.message

if __name__ == "__main__":
   main(sys.argv[1:])