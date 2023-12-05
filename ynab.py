from datetime import datetime, timedelta


def readFile(inputFile):
    data = []
    try:
        with open(inputFile) as myFile:
            data = myFile.read().splitlines()  # read each line of the file into a list
            return data
    except FileNotFoundError:
        print("The file does not exist, please try again")
        return data


def processFile(myData):
    newData = []

    def processItem(item):
        # stripping out commas, output is csv file and extra commas cause errors
        item = item.replace(",", "")
        if "+$" in item:
            item = item.replace("+$", "$")  # marking all inflows
        else:
            item = item.replace("$", "-$")  # marking all outflows
        return item

    # removing the line in the file with the % cashback, not needed
    newData = [processItem(item) for item in myData if "%" not in item]

    def getRelativeDate(relativeTerm):
        '''Apple card transactions will often state dates like Yesterday, and days of the week relative to the current date.  
        This funciton takes the relative term and translates it into a date'''
        today = datetime.now().date()

        if relativeTerm.lower() == 'yesterday':
            resultDate = today - timedelta(days=1)
        elif relativeTerm.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            # Get the current day of the week (Monday is 0 and Sunday is 6)
            currentDay = today.weekday()

            # Calculate the difference between the current day and the target day
            days_until_target = (currentDay - ['monday', 'tuesday', 'wednesday', 'thursday',
                                 'friday', 'saturday', 'sunday'].index(relativeTerm.lower())) % 7

            # Adjust the date accordingly
            resultDate = today - timedelta(days=days_until_target)
        else:
            # Default to today if the input is not recognized, this is useful for the times when Apple card reports hours from transaction
            resultDate = today

        # formatting the date as MM/DD/YYYY
        return resultDate.strftime("%m/%d/%Y")

    def processDate(dateText):
        '''The text in the captured apple data is User - date.  We are stripping out the name and only returning the date'''
        # just capture data after the -
        processedStr = dateText.split('-')[-1].strip()
        if ("/" in processedStr):  # if the date is already in the correct format
            # Parse the date string into a datetime object
            parsed_date = datetime.strptime(
                processedStr, '%m/%d/%y')  # format as MM/DD/YYYY
            # return in the same format as other dates
            return parsed_date.strftime('%m/%d/%Y')
        else:
            # get date if string is in relative form - yesterday or day of week
            return getRelativeDate(processedStr)

    # according to input file, the 4th line of every transacton contains the date info
    for index, item in enumerate(newData):
        if (index - 3) % 4 == 0:  # if you are on the line containing the date or relative date
            newData[index] = processDate(item)

    if len(newData) % 4 != 0:  # after removing the line with the cash back %, each transaction should contain 4 lines of data
        print("Error in input file, please check")
        return False

    # copy the list so we can move things around to the correct order
    finalData = newData[:]

    # setting up the final data list in this order: Date, Payee, Memo, Amount
    for i in range(0, len(newData), 4):
        for j, value in enumerate(newData[i:i+4]):
            if "$" in value:
                # the data containing the amount goes in the 4th spot
                finalData[i+3] = value
            elif "/" in value:
                # the data containing the date goes in the 1st spot
                finalData[i] = value
            elif j < 2:
                # there are 2 lines of plain text, payee and memo, the payee is first and goes in the 2nd spot
                finalData[i+1] = value
            else:
                finalData[i+2] = value  # the memo line, goes in the 3rd spot

    return finalData


def writeFile(myData):
    # this will overwrite any existing file with the same name
    fileName = input("What do you want to name your output file? ")
    with open(fileName, "w") as outputFile:
        outputFile.write("Date,Payee,Memo,Amount\n")  # write out headers
        for i in range(0, len(myData), 4):
            # join all the data for each transaction in a single line separated by commas
            line = ",".join(myData[i:i+4]) + "\n"
            outputFile.write(line)

    print(fileName, "was sucessfully created!")


def main():
    '''A program to take Apple card data and format as a CSV for easy input into YNAB.  This is accomplished by taking a screen shot 
    from the Apple wallet app transaction page and using a text OCR scanner to produce a text file.  Each purchase should have 5 lines (Amount
    Payee, Memo, Date and cash back %) Each payment should have 4 lines (same as payment except for cash back%).  Please ensure correct format of text 
    file before processing.  The date line might also contain the user who used the card and could contain a relative date.  The program will adjust 
    for this'''
    myData = []
    while not myData:  # looping incase of file name eroor
        file = input("What file do you want to process? or hit X to exit ")
        if file.lower() == 'x':
            return
        else:
            myData = readFile(file)  # read in contents of file into a list
            if not myData:
                continue
            else:
                myData = processFile(myData)  # process the data
                if not myData:
                    continue
                else:
                    writeFile(myData)  # write data to output file


main()
