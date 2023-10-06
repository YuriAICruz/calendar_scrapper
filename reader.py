from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pyperclip
import sys

date_format = "%B%d %Y - %I:%M%p"
date_formatB = "%B%d %Y - %I%p"

coma = ";"
soup_key = 'ynRLnc'


class CalendarEvent():
    pass

    def __str__(self):
        return self.title + coma + self.startDate.strftime("%Y-%m-%d %I:%M%p") + coma + self.endDate.strftime("%Y-%m-%d %I:%M%p")+coma+str(self.type)


def getDate(date_str, time):
    try:
        return datetime.strptime(
            date_str+"- "+time, date_format)
    except ValueError:
        return datetime.strptime(
            date_str+"- "+time, date_formatB)


def addCalendarEvent(event):
    lines = event.split(',')
    calendar_event = CalendarEvent()
    calendar_event.title = lines[1].replace("\n", " ").replace("  ", "")

    date = lines[len(
        lines)-2].replace("\n", " ").replace(" ", "").split(",")
    date.append(
        lines[len(lines)-1].replace("\n", " ").replace(" ", ""))
    date_str = "".join(d+" " for d in date)

    time = lines[0].replace(
        " to ", ",").replace(" ", "").split(",")

    calendar_event.startDate = getDate(date_str, time[0])
    calendar_event.endDate = getDate(date_str, time[1])

    calendar_event.type = 0
    if "Lunch" in calendar_event.title:
        calendar_event.type = 5
    if "Study" in calendar_event.title:
        calendar_event.type = 2
    if "focus" in calendar_event.title:
        calendar_event.type = 3

    return calendar_event


def CreateCalendarCsv(file_contents):
    out_file = "out.csv"
    soup = BeautifulSoup(file_contents, 'html.parser')

    event_titles = [event.text for event in soup.find_all(
        'div', class_=soup_key)]

    calendar_events = []
    for item in event_titles:
        if (len(item) < 2):
            continue
        event = addCalendarEvent(item)
        for ce in calendar_events:
            if (ce.startDate == event.startDate and ce.endDate == event.endDate):
                event.type = 4
        calendar_events.append(event)

    content = "title"+coma+"start"+coma+"end"+coma+"type\n" + "".join(
        str(e)+"\n" for e in calendar_events)
    f = open(out_file, "w", encoding="utf8")
    f.write(content)
    f.close()
    print("Saved " + out_file)
    pyperclip.copy(content)
    print("Result copied to clipboard")


def readFromFile(path='./content.html'):
    with open(path, encoding="utf8") as file:
        file_contents = file.read()
    CreateCalendarCsv(file_contents)


def readFromUrl(url='https://calendar.google.com/calendar/u/0/r'):
    response = requests.get(url)
    CreateCalendarCsv(response.text)


def readFromClipboard():
    clipboard_text = pyperclip.paste()
    CreateCalendarCsv(clipboard_text)


def printHelp():
    print(
        "Help\n-c copy from clipboard \n-f [path] read from file \n-h help \n-u [url] read from url \n-k [key] key used in the div class default["+soup_key+"]")


for index, arg in enumerate(sys.argv):
    if arg == "-h":
        printHelp()
        break
    if arg == "-k":
        soup_key = sys.argv[index+1]
        print("Using key ="+soup_key)
    if arg == "-c":
        readFromClipboard()
        break
    if arg == "-f":
        readFromFile(sys.argv[index+1])
        break
    if arg == "-u":
        readFromUrl(sys.argv[index+1])
        break

# build using pyinstaller --onefile .\reader.py
