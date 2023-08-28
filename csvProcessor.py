#for command line arguments
import sys

#for time stamping
import time
from datetime import date, timedelta, datetime

#libraries for sending alert emails
import smtplib
from email.mime.text import MIMEText

#processed lists for CSV 1 and CSV 2 files
fileOne = []
fileTwo = []

#holds copies of 'fileOne' and 'fileTwo' lists for processing logic
tempFileOne = []
tempFileTwo = []

#holds date and time slot information for the alert email
totalString = ''

#boolean's for determining largest or same row csv count
moreRowsInFileOne = 0
moreRowsInFileTwo = 0
sameRowCountInFileOneAndTwo = 0
missingRows = 0

lineCounter = 0     #for skipping first csv line

tempCity = sys.argv[3]  #grab city name


################################################################
# Function: PreProcessCSVs()
#   -Open CSV files, process, and store within individual lists
#   -AM/PM elements are purged and the day number is added
################################################################
def PreProcessCSVs():
    #open specified (arguments) csv files
    csvOne = open(sys.argv[1],'r')
    csvTwo = open(sys.argv[2],'r')

    #stores data from csv files into lists
    global fileOne
    global fileTwo
    fileOne = csvOne.readlines()
    fileTwo = csvTwo.readlines()

    #close specified csv files
    csvOne.close()
    csvTwo.close()

    #holds current day (incremented) after passing an 'undefined' (new day) in the list
    dayCountFileOne = 0
    dayCountFileTwo = 0

    #loop through the first list (CSV 1)
    for item in list(fileOne):
        #remove AM and PM information from list
        if item == 'PM\"\n' or item == 'AM\"\n':
            fileOne.remove(item)
        else:
            #handle 'undefined' elements (used to increment the day count)
            if item == 'undefined\n' or item == 'undefined':
                #remove given line, and append list with the same line and day count
                fileOne.remove(item)
                fileOne.append('undefined\n' + str(dayCountFileOne))

                dayCountFileOne += 1    #increment day count
            #handle time slots
            else:
                #remove given line, and append list with the same line and day count
                tempItem = item
                fileOne.remove(item)
                fileOne.append(tempItem + str(dayCountFileOne))

    #same as above, but for CSV 2
    for item in list(fileTwo):
        if item == 'PM\"\n' or item == 'AM\"\n':
            fileTwo.remove(item)
        else:
            if item ==  'undefined\n' or item == 'undefined':
                fileTwo.remove(item)
                fileTwo.append('undefined\n' + str(dayCountFileTwo))
                dayCountFileTwo += 1
            else:
                tempItem = item
                fileTwo.remove(item)
                fileTwo.append(tempItem + str(dayCountFileTwo))


###########################################################
# Function: CountRows
#   -count rows for each csv file
#   -determine if they have the same amount
#    or one is greater than the other
###########################################################
def CountRows():
    rowCountFileOne = 0         #holds the amount of rows for csv #1
    rowCountFileTwo = 0         #holds the amount of rows for csv #2

    #Declaration handled to modify global variables
    global moreRowsInFileOne
    global moreRowsInFileTwo
    global sameRowCountInFileOneAndTwo
    global missingRows

    #calcuate row counts for both files
    for row in fileOne:
        rowCountFileOne += 1
    for row in fileTwo:
        rowCountFileTwo += 1

    #monitor counts
    print("File One: " + str(rowCountFileOne) + "  " + "File Two: " + str(rowCountFileTwo))

    #compare csv row counts and determine which is larger (or tie)
    if rowCountFileOne > rowCountFileTwo:
        moreRowsInFileOne = 1
        missingRows = rowCountFileOne - rowCountFileTwo

    elif rowCountFileTwo > rowCountFileOne:
        moreRowsInFileTwo = 1
        missingRows = rowCountFileTwo - rowCountFileOne

    else:
        sameRowCountInFileOneAndTwo = 1
        missingRows = 0

    print("Missing Row Count: " + str(missingRows))

    if (missingRows > 4):
        print("Row Count Exceeds Threshold")
    else:
        print("Row Count Does not Exceed Threshold")


###########################################################
# Function: SetVariablesForCSVComparison
#   -pushes copies of the csv lists to temporary variables
#   -used for comparing row values (exceed loop bound purposes)
###########################################################
def SetVariablesForCSVComparison():
    global tempFileOne
    global tempFileTwo

    if moreRowsInFileOne == 1:
        tempFileOne = list(fileTwo)
        tempFileTwo = list(fileOne)
        print("Higher Row Count in File One")

    if moreRowsInFileTwo == 1:
        tempFileOne = list(fileOne)
        tempFileTwo = list(fileTwo)
        print("Higher Row Count in File Two")

    if sameRowCountInFileOneAndTwo == 1:
        tempFileOne = list(fileOne)
        tempFileTwo = list(fileTwo)
        print("Same Row Count in Both Files")

    print()


###########################################################
# Function: FindValueDifferencesInRows
#   -pushes copies of the csv lists to temporary variables
#   -used for comparing row values and to not exceed loop bounds
###########################################################
def FindValueDifferencesInRows():
    global lineCounter      #utilized to progress through File 2's lines
    global totalString      #holds string (info) to send within alert emails
    today = date.today()    #grab todays date
    timeAndDayNumber = []   #holds time slot and day number from a file line

    print('Flagged:\n')

    #loop through bookings and process
    for i in tempFileOne:
        loopFlag = 0        #for 'while' loop processing (sequential time slot bookings)

        #skips fist row of CSV
        if lineCounter != 0:
            splitFileOneLine = i.split(",")             #utilize delimiter to create list (from line)
            tempFileTwoLine = tempFileTwo[lineCounter]     #create copy of second list's line
            splitFileTwoLine = tempFileTwoLine.split(",")      #utilize delimiter to create list (from line)

            #create list (time slot, day number) from file two if comparison is unsuccessful
            if splitFileOneLine[0] != splitFileTwoLine[0]:
                timeAndDayNumber = tempFileTwoLine.split("\n")

                #process if time slot is not undefined
                if timeAndDayNumber[0] != 'undefined':
                    #print date and times to command line
                    print(today + timedelta(days = int(timeAndDayNumber[1])))
                    print(timeAndDayNumber[0] + '\n')

                    #store date and time for alert email
                    tempString = '\n' + str(datetime.today().date() + timedelta(days = int(timeAndDayNumber[1]))) + '\n'
                    totalString += tempString + timeAndDayNumber[0] + '\n'

                    #loop handles consecutive time slots when progressing through file two
                    while (loopFlag == 0):
                        #proceed to next line of file 2
                        lineCounter += 1
                        tempFileTwoLine = tempFileTwo[lineCounter]

                        #grab the next time slot
                        splitFileTwoLine = tempFileTwoLine.split(",")
                        additionalTimeSlot = splitFileTwoLine[0].split("\n")

                        #compare current list one tim slot to new list two time slot
                        if splitFileOneLine[0] != splitFileTwoLine[0]:
                            #print time to command line and send to email string
                            print(additionalTimeSlot[0] + '\n')
                            totalString += additionalTimeSlot[0] + '\n'
                        else:
                            #stop loop if timeslots match
                            loopFlag = 1

        lineCounter += 1    #increment row in file two


###########################################################
# Function: SendAlertMessage
#   -connects to mail server and sends alerts
#   -an "App" password was generated for account access
###########################################################
def SendAlertMessage():
    #modify for sending/recieving addresses, using an 'app' password
    sender = ''
    receiver = ''
    password = ''

    port = ''

    message = MIMEText('Flagged: ' + tempCity + '\n' + totalString) #Holds message for email

    #attributes of MIMEText object
    message['Subject'] = 'Booking Alert: ' + tempCity
    message['From'] = sender
    message['To'] = receiver

    print("Attempting to send an email...")

    #Establish local connection and test
    with smtplib.SMTP('smtp.gmail.com', port) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [receiver], message.as_string())

        print("An email has been sent.")
        server.close()


#############################################################
# "Main' area for general logic handling (function calls)
#############################################################
PreProcessCSVs()
CountRows()
SetVariablesForCSVComparison()
FindValueDifferencesInRows()
SendAlertMessage()
