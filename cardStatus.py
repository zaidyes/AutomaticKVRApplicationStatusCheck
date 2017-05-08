import sys, getopt
import os.path
import mechanize
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from enum import Enum
import easygui


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
			result = Result(code, Status.FAILURE, answers[count-1].string)#.encode('utf-8'))
			results.append(result)
			continue

		answers = soup.find_all("font", attrs={"color":"green"})
		count = len(answers)
		if count != 0 :
			result = Result(code, Status.READY, answers[count-1].string)#.encode('utf-8'))
			results.append(result)
			continue

		answers = soup.find_all("font", attrs={"color":"black"})
		count = len(answers)
		if count != 0 :
			result = Result(code, Status.NOT_READY, answers[count-1].string)#.encode('utf-8'))
			results.append(result)
			continue
		
		result = Result(code, Status.UNKNOWN, soup)
		results.append(result)

	return results

def emailResults(eFrom, pwd, eTo, results):
	readyResults = []
	for result in results:
		if result.status == Status.READY:
			readyResults.append(result)

	if len(readyResults) < 1:
		return False

	try:
		server = smtplib.SMTP_SSL('mail.kohlmag.com', 465)
		server.ehlo()
	except Exception, e:
		print "Could not shake hands with email server because: " + str(e)
		return False

	try:
		login = server.login(eFrom, pwd)
		if login :
			print "Login as: " + eFrom

	except Exception, e:
		print "Could not login because: " + str(e)
		print "Aborting email sequence..."
		return False

	for readyRes in readyResults:
		try:
			msg = MIMEText("Code: " + readyRes.code + " | Status: " + str(readyRes.status) + " | Message: " + readyRes.message.encode('utf-8'))
			msg['Subject'] = 'Some applications are ready'
			msg['From'] = eFrom
			msg['To'] = eTo
			server.sendmail(eFrom, [eTo], msg.as_string())
			print "Email sent to: " + eTo
		except Exception, e:
			print "Could not send email because: " + str(e)
			return False

	server.quit()
	return True

def showReadyDialog(results):
	toShow = ""
	for result in results:
		if result.status == Status.READY or result.status == Status.UNKNOWN:
			toShow += "Code: " + result.code + " | Status: " + str(result.status) + " | Message: " + result.message + "\n"
	
	if len(toShow) > 0:
		print "Showing ready dialog..."
		easygui.msgbox(toShow, 'Ready Application Ids')

def main(argv):
	codeFile = ''
	username = ''
	emailTo = ''

	try:
		opts,args = getopt.getopt(argv,"hc:u:p:t:",["codefile=","username=", "password=", "emailto="])
	except getopt.GetoptError:
		print 'cardStatus.py -c <codefile> -u <username> -p <password> -t <emailto>'
		sys.exit('Arguements missing')

	for opt,arg in opts:
	    if opt == '-h':
	        print 'cardStatus.py -c <codefile> -u <username> -p <password> -t <emailto>'
	        print 'example: cardStatus.py -c codefile.txt -f myemail@myemail.com -p mypassword -t youremail@youremail.com'
	        sys.exit()
	    elif opt in ("-c", "--codefile"):
	    	codeFile = arg
	    elif opt in ("-u", "--username"):
	    	username = arg
	    elif opt in ("-p", "--password"):
	    	password = arg
	    elif opt in ("-t", "--emailto"):
	    	emailTo = arg

	if not validateCodeFile(codeFile):
		sys.exit('Please provide a valid code file see help')
	

	codes = getCodesFromFile(codeFile)
	if len(codes) < 1:
		sys.exit('No codes found in file')

	results = getCodeResults(codes)
	if len(results) < 1:
		sys.exit('No results could be computed please check internet connection')

	for result in results:
		print "Code: " + result.code + " | Status: " + str(result.status) + " | Message: " + result.message

	showDg = False
	if username and password and emailTo:
		if emailResults(username, password, emailTo, results):
			print "Results emailed"
		else:
			showDg = True
	else:
		print "Email not configured...exiting"
		showDg = True

	if showDg:
		showReadyDialog(results)

	sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
