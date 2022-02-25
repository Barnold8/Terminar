import requests
from os.path import exists
import datetime
from datetime import date
import sys


#13 elems per tile

class cal_COMP: #calendar component

    def __init__(self):

        self.data = []     # Raw data coming in
        self.filtered = [] # Cleaned up data

        self.date = None
        self.professor = None
        self.open = None   # If lecture is still happening
        self.location = None
        self.lecture = None
        self.lecture_type = None
        self.module_code = None
        self.start = None
        self.end = None

    def selfClean(self):
        self.data = self.data[59:]

    def filter(self):
        indexs = [1,2,8,9,10,11]
        for x in indexs:
            self.filtered.append(self.data[x])

    def printALL(self):

        vars = [self.date,self.professor,self.open,self.location,self.lecture,self.lecture_type,self.module_code]

        print("="*16+"Object"+"="*16)
        for v in vars:
            print(v)
        print("="*38)

    def setDate(self): # I didnt know the string of the numbers was the date. So credit goes to Louis Edwards

        Year = ""
        Month =  ""
        Day = ""

        try:
            x = self.filtered[0].split(":")
            x = x[1].split("T")
            
            for i in range(len(x[0])):
                if( i < 4):
                    Year += x[0][i]
                elif(i >= 4 and i < 6):
                    Month += x[0][i]
                else:
                    Day += x[0][i]

            YMD = [Year,Month,Day]
            self.date = YMD
            
        except Exception as e:
            print("Cannot process empty filter. Process self.data first")
    
    def isOn(self):
        self.open = True if  "CONFIRMED" in self.filtered[2] else False

    def setTitle(self):
        self.lecture = ((self.filtered[3].split(":"))[1].split("-"))[0]
        self.lecture_type =  ((self.filtered[3].split(":"))[1].split("-"))[1]
    
    def setProfessor(self):
        self.professor = ((self.filtered[4].split("\\n"))[0].split(":"))[2]
        self.module_code = (((self.filtered[4].split("\\n")))[2].split(":"))[1]

    def setLocale(self):
        self.location = "" + (self.filtered[5].split(":"))[0]+": " + (self.filtered[5].split(":"))[1]

    def getTime(self):
        start = str(((self.filtered[0].split(":"))[1].split("T"))[1])
        end = str(((self.filtered[1].split(":"))[1].split("T"))[1])
        start_final = ""
        end_final = ""

        for i in range(len(start)):
            
            if i == 2:
                start_final += ":"
                end_final += ":"
            else:
                start_final += start[i]
                end_final += end[i]

        self.start = start_final[:-1]
        self.end = end_final[:-1]


    def configALL(self):
        
        self.filter()
        self.setDate()
        self.setLocale()
        self.setProfessor()
        self.setTitle()
        self.isOn()
        self.getTime()
        
def check_link(): # there could be checking for the reading file to make sure the file is valid with its link but i cba

    if exists("cal_link.txt") != True:
        
        link = input("No link exists for the calendar.\nPlease input it here: ").lower() # Santise input link by lowering chars, making it processable for me
        linkSplit = None

        if "http://" not in link and "https://" not in link:
            print("http:// or https:// not found in link, making it invalid. Please provide a valid link next time")
            exit()

        linkSplit = (link[8:] if "https://" in link else link[7:]).split(".")

        if linkSplit[0] != "ical":
            print("Expected an ical link but got {} instead".format(linkSplit[0]))
            exit()
        
        with open("cal_link.txt","w") as file:
            file.write(link)
        return link
    else:
        with open("cal_link.txt", "r") as file:
            link = (file.readlines())[0]
        return link
        
def r_get(link): # wrapper function that handles

    try:
        r = requests.get(check_link())
        if(r.status_code != 200):
            print("Got HTTP response code {} when 200 was expected. Ensure the link is valid".format(r.status_code))
            exit()
        
    except Exception as e:
        print("ERROR: couldnt make request to site. This is a hard exception, the highest possibility is that the link itself is invalid but passed the main checks.")
        print("The error in question:\n\n")
        print(e)
        exit()
    return r

def impData(r):
    data = []
    objs = []
    x = 1
    elems = (r.text).split("\n")
    elems = elems[:-1]
    
    for e in elems:
        
        if "END:VEVENT" in e:
            c = cal_COMP()
            c.data = data
            objs.append(c)
            data = []
        else:
            data.append(e)
           
    return objs

def isCurrWeek(date): # refactored from https://stackoverflow.com/questions/37169362/what-would-be-the-pythonic-way-to-find-out-if-a-given-date-belongs-to-the-curren 
    x = date[0]+date[1]+date[2]
    x_year = int(date[0])
    x = datetime.datetime.strptime(x,'%Y%m%d').isocalendar()[1]
    y = datetime.datetime.today()
    return x == y.isocalendar()[1] \
                and x_year == y.year

def getWeek():
    this_week = []
    x = impData(r_get(check_link()))
    x[0].selfClean() # The first chunk of data is very messy so it needs cleaning
    for a in x:
        a.filter()
        a.configALL()
        if(isCurrWeek(a.date)):
            this_week.append(a)

    return this_week

def getWeekDay(date):
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
    return days[day.weekday()]

def populate_week(week):

    week_arr = [[],[],[],[],[],[],[]]

    for x in week: # Gross if elif 
        if getWeekDay(x.date) == "Monday":
            week_arr[0].append(x)
        elif getWeekDay(x.date) == "Tuesday":
            week_arr[1].append(x)
        elif getWeekDay(x.date) == "Wednesday":
            week_arr[2].append(x)
        elif getWeekDay(x.date) == "Thursday":
            week_arr[3].append(x)
        elif getWeekDay(x.date) == "Friday":
            week_arr[4].append(x)
        elif getWeekDay(x.date) == "Saturday":
            week_arr[5].append(x)
        elif getWeekDay(x.date) == "Sunday":
            week_arr[6].append(x)
    
    return week_arr



def simple_print(week,condense):

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    string = "Coming up this week"
    print("+"+"="*32+string+"="*32+"+")

    for i in range(len(week)-2): #-2 because we dont do weekends at uni
        print("\n\t\t\t\t       "+days[i])
        for y in range(len(week[i])):
            d = week[i][y]
            if condense:
                print("\n")
                print("LESSON: "+ d.lecture)
                print("START: "+d.location)
                print("START: "+d.start)
                print("END: "+ d.end)
                print("TYPE: "+ d.lecture_type)
                print("BY: "+ d.professor)
                print("MODULE: "+ d.module_code)
                print("HAPPENING: "+str(d.open)) 
            else:
                print("\n")
                print("LESSON: "+ d.lecture)
                print("\t"+"|\n\t+----- "+ d.location)
                print("\t"+"|\n\t+----- START: "+ d.start)
                print("\t"+"|\n\t+----- END: "+ d.end)
                print("\t"+"|\n\t+----- TYPE: "+ d.lecture_type)
                print("\t"+"|\n\t+----- BY: "+ d.professor)
                print("\t"+"|\n\t+----- MODULE: "+ d.module_code)
                print("\t"+"|\n\t+----- HAPPENING: "+ str(d.open))
            
        

    print("+"+"="*(32+(len(string)))+"="*32+"+")





def main():

    condense = False

    for x in sys.argv:

        if x == "-C":
            condense = True

    week = populate_week(getWeek())

    simple_print(week,condense)

main()
