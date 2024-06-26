from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Time, Employee, Surgeon, Cleaner, Patient, Surgery
import datetime
from django.utils import timezone
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required


# Create your views here.
# view function: request -> response (request handler)



class delete(TemplateView):
    """
    View for delete.html
    """
    template_name = 'delete.html'
    def post(self, request):
        #get id as post input 
        surgery_id = request.POST['ID']
        try:
            #if object exists, delete and redirect
            surgery = Surgery.objects.get(id=surgery_id)
            surgery.delete()
            return redirect('personschedule')
        except Surgery.DoesNotExist:
            #send error message otherwise
            messages.error(request, "Error: Surgery with this ID does not exist.")
            return redirect('delete')


#schedule appointment view
class appointment(TemplateView):
    """
    View for appointment.html
    """
    template_name = 'appointment.html'
    
    def post(self, request):
        #get inputs via POST
        patientfname = request.POST['fname']
        patientlname = request.POST['lname']
        cleanerfname = request.POST['cfname']
        cleanerlname = request.POST['clname']
        jfname = request.POST['jfname']
        jlname = request.POST['jlname']
        sfname = request.POST['sfname']
        slname = request.POST['slname']

        #get date and note inputs (also via POST)
        month = datetime.datetime.strptime(request.POST['Month'], "%B").month #converts month string into int
        day = int(request.POST['Day'])
        year = int(request.POST['Year'])
        start = request.POST['StartTime']
        end = request.POST['EndTime']
        notes = request.POST['Notes']
        start_str = f"{day}-{month}-{year} {start}" #converts date and time into string
        #converts string into datetime object of the surgery start time
        start_obj = datetime.datetime.strptime(start_str, '%d-%m-%Y %H:%M') 
        end_str = f"{day}-{month}-{year} {end}" #converts date and time into string
        #converts string into datetime object of the surgery start time
        end_obj = datetime.datetime.strptime(end_str, '%d-%m-%Y %H:%M') 
        timeperiod = Time(timestart=timezone.make_aware(start_obj), timeend=timezone.make_aware(end_obj)) 
        
        #list of months with 31 days
        list1 = [1, 3, 5, 7, 8, 10, 12]


        #date validation -> make sure the day actuall exists
        #if they do not render an error and redirect back to appointment page
        if month not in list1 and day >= 31:
            messages.error(request, "Day Error: Invalid Date.")
            return redirect('appointment')
        elif month == 2 and day >= 30:
            messages.error(request, "Day Error: Invalid Date.")
            return redirect('appointment')
        #tackle leap years (why are the rules so weird?)
        elif month == 2 and day == 29:
            if year % 4 == 0:
                if year % 400 == 0:
                    pass
                elif year % 100 == 0:
                    messages.error(request, "Day Error: Invalid Date.")
                    return redirect('appointment')
            else:
                messages.error(request, "Day Error: Invalid Date.")
                return redirect('appointment')
        
        
        #get all surgeries
        try:
            earliest_surgery = Surgery.objects.earliest('time_period__timestart')
            latest_surgery = Surgery.objects.latest('time_period__timestart')
        #validation
        except Surgery.DoesNotExist:
            earliest_surgery = None
            latest_surgery = None

        #validation
        if earliest_surgery is not None and latest_surgery is not None:
            allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date()) #gets the surgeries to be displayed from date_1 to date_2, which are datetime() objects
            for x in allsurgeries:
                #make sure there are no overlaps with other surgeries
                if x.time_period.timestart < timeperiod.timeend and timeperiod.timeend < x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('appointment')
                elif x.time_period.timestart < timeperiod.timestart and timeperiod.timestart < x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('appointment')
                elif timeperiod.timestart < x.time_period.timestart and x.time_period.timestart < timeperiod.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('appointment')
                elif timeperiod.timestart < x.time_period.timeend and x.time_period.timeend < timeperiod.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('appointment')
                elif timeperiod.timestart == x.time_period.timestart or timeperiod.timeend == x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('appointment')
            if timeperiod.timestart > timeperiod.timeend:
                messages.error(request, "Time error: Overlap Detected")
                return redirect('appointment')
               
        timeperiod.save()

        #make object classes and add them to surgery

        #junior surgeon object
        j = Surgeon(fullName=jfname + " " + jlname, exp="Jr", qualifications="Qualified")
        j.save()
        j.availability.add(Time.objects.get(id=1))

        #senior surgeon object
        s = Surgeon(fullName=sfname + " " + slname, exp="Jr", qualifications="Qualified")
        s.save()
        s.availability.add(Time.objects.get(id=1))

        #cleaner object
        c = Cleaner(fullName=cleanerfname + " " + cleanerlname)
        c.save()
        c.availability.add(Time.objects.get(id=1))

        #patient object
        patient = Patient(fullName=patientfname + " " + patientlname)
        patient.save()

        #surgery object using all aforementioned objects
        surgery = Surgery.objects.create(patient=patient, time_period=timeperiod, info = notes, is_checkup = False)
        surgery.save()

        #save surgery
        surgery.surgeons.add(j)
        surgery.surgeons.add(s)
        surgery.cleaners.add(c) 
        print(surgery)

        #redirect to main page
        return redirect('personschedule')


#followups code (similar to appointment)
def followups(request):
    if request.method == "POST":
        #get all inputs as POST
        patientfname = request.POST['fname']
        patientlname = request.POST['lname']
        surgfname = request.POST['surgfname']
        surglname = request.POST['surglname']
    
        #convert everything to int
        month = datetime.datetime.strptime(request.POST['Month'], "%B").month #converts month string into int
        day = int(request.POST['Day'])
        year = int(request.POST['Year'])
        start = request.POST['StartTime']
        end = request.POST['EndTime']
        #no notes for checkups
        info = 'No notes for checkup'

        start_str = f"{day}-{month}-{year} {start}" #converts date and time into string
        #converts string into datetime object of the surgery start time
        start_obj = datetime.datetime.strptime(start_str, '%d-%m-%Y %H:%M') 
        end_str = f"{day}-{month}-{year} {end}" #converts date and time into string
        #converts string into datetime object of the surgery start time
        end_obj = datetime.datetime.strptime(end_str, '%d-%m-%Y %H:%M') 
        timeperiod = Time(timestart=timezone.make_aware(start_obj), timeend=timezone.make_aware(end_obj))
         #get all surgeries
        try:
            earliest_surgery = Surgery.objects.earliest('time_period__timestart')
            latest_surgery = Surgery.objects.latest('time_period__timestart')
        #validation
        except Surgery.DoesNotExist:
            earliest_surgery = None
            latest_surgery = None

        #validation
        if earliest_surgery is not None and latest_surgery is not None:
            allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date()) #gets the surgeries to be displayed from date_1 to date_2, which are datetime() objects
            for x in allsurgeries:
                #make sure there are no overlaps with other surgeries
                if x.time_period.timestart < timeperiod.timeend and timeperiod.timeend < x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('followups')
                elif x.time_period.timestart < timeperiod.timestart and timeperiod.timestart < x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('followups')
                elif timeperiod.timestart < x.time_period.timestart and x.time_period.timestart < timeperiod.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('followups')
                elif timeperiod.timestart < x.time_period.timeend and x.time_period.timeend < timeperiod.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('followups')
                elif timeperiod.timestart == x.time_period.timestart or timeperiod.timeend == x.time_period.timeend:
                    messages.error(request, "Time error: Overlap Detected")
                    return redirect('followups')
            if timeperiod.timestart > timeperiod.timeend:
                messages.error(request, "Time error: Overlap Detected")
                return redirect('followups')


        timeperiod.save()

        

        #list of months with 31 days
        list1 = [1, 3, 5, 7, 8, 10, 12]

        #validate the date as a correct one
        if month not in list1 and day >= 31:
            messages.error(request, "Day Error: Invalid Date.")
            return redirect('appointment')
        elif month == 2 and day >= 30:
            messages.error(request, "Day Error: Invalid Date.")
            return redirect('appointment')
        elif month == 2 and day == 29:
            if year % 4 == 0:
                if year % 400 == 0:
                    pass
                elif year % 100 == 0:
                    messages.error(request, "Day Error: Invalid Date.")
                    return redirect('appointment')
            else:
                messages.error(request, "Day Error: Invalid Date.")
                return redirect('appointment')      

        #surgeon object
        surg = Surgeon(fullName=surgfname + " " + surglname, exp="Jr", qualifications="Q2")
        surg.save()
        surg.availability.add(Time.objects.get(id=1))

        #patient object
        patient = Patient(fullName=patientfname + " " + patientlname)
        patient.save()

        #create surgery object using aforementioned objects
        surgery = Surgery.objects.create(patient=patient, time_period=timeperiod, info=info, is_checkup = True)
        surgery.save()
        surgery.surgeons.add(surg)
        print(surgery)

        #save and redirect

        return redirect('personschedule')
    #if not post, render followups
    return render(request, "followups.html")



class personschedule(TemplateView):
    """
    personal schedule template (calendar)
    """
    #html refs
    template_name = 'personschedule.html'
    template_2 = 'event-sample.html'

    #get request
    def get(self, request):
        '''
        View function displays calls template to display schedule
        Input:
            request (HTML request)
        Output:
            render() (HTML file): note 
        '''

        #days tracker
        days = [[]]
        

        surgeries = list(Surgery.objects.all())
        #if there are surgeries, try to access all of them
        try:
            earliest_surgery = Surgery.objects.earliest('time_period__timestart')
            latest_surgery = Surgery.objects.latest('time_period__timestart')
        except Surgery.DoesNotExist:
            earliest_surgery = None
            latest_surgery = None
        if earliest_surgery is not None and latest_surgery is not None:
            allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date())
        else:
            allsurgeries = []

        #get todays date
        today = datetime.datetime.today()
        month1 = today.month
        day1 = today.day
        year1 = today.year

        #mimic todays date, these dates will move accordingly as the for loop runs
        month2 = today.month
        day2 = today.day
        year2 = today.year
        
        #list of months with 31 days
        list1 = [1, 3, 5, 7, 8, 10, 12]
        #list from 1 to 12
        list2 = [x for x in range(1, 13)]
        days = [] #list of surgery objects within seven days
        daytracker = [] #tracker
        #extend schedule 7 days
        for _ in range(7):
            #append days and tracker lists
            days.append([])
            daytracker.append([month2, day2, year2])

            #increment the day by 1 
            day2 += 1

            #handle if month/year changes
            if day2 == 32:
                day2 = 1
                if list2.index(month2) == 11:
                    year2 += 1
                    month2 = 1
                else:
                    month2 += 1
            elif month2 not in list1 and day2 == 31:
                day2 = 1
                month2 += 1
            elif month2 == 2 and day2 == 30:
                day2 = 1
                month2 = 3
            #leap year validation
            elif month2 == 2 and day2 == 29:
                if year2 % 4 == 0:
                    if year2 % 400 == 0:
                        pass
                    elif year2 % 100 == 0:
                        day2 = 1
                        month2 = 3
                else:
                    day2 = 1
                    month2 = 3

        #append again to daytracker to make up for the last one            
        daytracker.append([month2, day2, year2])
        
        #test strings
        teststring = f'{month1}{day1}{year1}'
        teststring2 = f'{month2}{day2}{year2}'
        result = request.GET.get('result', None)
        teststring3 = f'{result}'

        #days is now [[],[],[],[], ...]
        #daytracker is now [[firstday], [secondday], ...]

        #fills days
        for x in allsurgeries:
            #find a surgery 
            month = x.time_period.timestart.month
            day = x.time_period.timestart.day
            year = x.time_period.timestart.year
            try:
                #try to find the surgery in the range of days
                ind = daytracker.index([month, day, year])
                days[ind].append(x)
                #antoher test
                teststring += f' {month}{day}{year}'
            except ValueError:
                #if its not in the list just pass and go next 
                continue 
        #fills days_string
        days_string = f''
        print(daytracker)
        for x in range(7):
            
            #get the day of the week
            year = daytracker[x][2]
            month = daytracker[x][0]
            day = daytracker[x][1]
            dayofweek = datetime.datetime(year, month, day).weekday()
            print(dayofweek)

            #turn day of week int into string
            #yes, i know this is a braindead way of doing it, don't judge me
            if dayofweek == 0:
                dayofweek = "Monday"
            elif dayofweek == 1:
                dayofweek = "Tuesday"
            elif dayofweek == 2:
                dayofweek = "Wednesday"
            elif dayofweek == 3:
                dayofweek = "Thursday"
            elif dayofweek == 4:
                dayofweek = "Friday"
            elif dayofweek == 5:
                dayofweek = "Saturday"
            elif dayofweek == 6:
                dayofweek = "Sunday"
            print(dayofweek)

            #set up first html string
            appointments = f'<ul>'


            for y in days[x]:
                #loop through days[x] to get all surgeries

                #make sure all time values are HH:MM
                a = int(y.time_period.timestart.hour)
                if a < 10:
                    a = f"0{a}"
                b = int(y.time_period.timestart.minute)
                if b < 10:
                    b = f"0{b}"
                c = int(y.time_period.timeend.hour)
                if c < 10:
                    c = f"0{c}"
                d = int(y.time_period.timeend.minute)
                if d < 10:
                    d = f"0{d}"
                
                #variables 
                timestart = f"{a}:{b}"
                timeend = f"{c}:{d}"


                timedate = f"{day}/{month}/{year}"
                patient = y.patient
                patientname = patient.fullName 
                is_checkup = y.is_checkup
                #if its a checkup, add proper html string
                if is_checkup:
                    name = f"Followup for {patientname}"
                    appointments += f'<li class="cd-schedule__event"><a data-start="{timestart}" data-end="{timeend}" data-content="event-sample" data-event="event-1" href = "event-sample.html" data-date="{timedate}"> <em class="cd-schedule__name">{name}</em></a></li>'
                else:
                    #add surgery string otherwise 
                    name = f"Surgery for {patientname}"
                    appointments += f'<li class="cd-schedule__event"><a data-start="{timestart}" data-end="{timeend}" data-content="event-sample" data-event="event-2" href = "event-sample.html" data-date="{timedate}"> <em class="cd-schedule__name">{name}</em></a></li>'
            

            #setup html string uses list elements and divisions 
            appointments += '</ul>' 
            day_string = f'<li class="cd-schedule__group"><div class="cd-schedule__top-info"><span>{dayofweek}</span></div><ul>'
            #add all appointments to the day
            day_string += appointments
            #make sure they close properly :)
            day_string += '</ul></li>'
            #add all days to the days string
            days_string += day_string
        
        #the big string :)
        #add the days string to the actual big string 
        schedule_string = f'<div class = "cd-schedule__events"><ul>{days_string}</ul></div>'
        #render and pass all strings
        return render(request, self.template_name,
                      {"schedule_string": schedule_string, 
                       "teststring":teststring, 
                       "teststring2":teststring2, 
                       "teststring3":teststring3, 
                       "day_string":day_string, 
                       "days_string":days_string,
                       "template_2":self.template_2}
                       )



class index(TemplateView):
    template_name = 'index.html'
    def post(self, request):
        '''
        View function displays calls template to display current surgeons
        Input:
            request (HTML request)
        Output:
            render() (HTML file): note 
        '''
        return render(request, self.template_name,{})

class archive(TemplateView):
    """
    Archive template View
    renders archive.html
    """
    #global variables
    template_name = 'archive.html'
    today = datetime.datetime.today()
    day = today.day
    month = today.month
    year = today.year

    #post request
    def post(self, request):
        #get inputs via POST
        self.month = datetime.datetime.strptime(request.POST['Month'], "%B").month #converts month string into int
        self.day = int(request.POST['Day'])
        self.year = int(request.POST['Year'])
        #return the get function
        return archive.get(self, request)

    #get function
    def get(self, request):
        dayofweek = 0
        try:
            #try to find all surgeries
            earliest_surgery = Surgery.objects.earliest('time_period__timestart')
            latest_surgery = Surgery.objects.latest('time_period__timestart')
        except Surgery.DoesNotExist:
            earliest_surgery = None
            latest_surgery = None
        if earliest_surgery is not None and latest_surgery is not None:
            allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date())
        else:
            allsurgeries = []
        display_surgeries = [] #list of surgery objects on the display date

        #loop through all surgeries
        for x in allsurgeries:
            #get the date of the surgery 
            month = x.time_period.timestart.month
            day = x.time_period.timestart.day
            year = x.time_period.timestart.year
            if [month, day, year] == [self.month, self.day, self.year]:
                #if the date is the date inputed, append
                display_surgeries.append(x)
                dayofweek = datetime.datetime(year, month, day).weekday()
                #convert day of week to string
                if dayofweek == 0:
                    dayofweek = "Monday"
                elif dayofweek == 1:
                    dayofweek = "Tuesday"
                elif dayofweek == 2:
                    dayofweek = "Wednesday"
                elif dayofweek == 3:
                    dayofweek = "Thursday"
                elif dayofweek == 4:
                    dayofweek = "Friday"
                elif dayofweek == 5:
                    dayofweek = "Saturday"
                elif dayofweek == 6:
                    dayofweek = "Sunday"

        #setup days string
        days_string = f''        
        #html string of all appointments
        appointments = f'<ul>'
        
        #loop through all surgeries necessary to display
        for x in display_surgeries:
            #make sure time is in HH:MM
            a = int(x.time_period.timestart.hour)
            if a < 10:
                a = f"0{a}"
            b = int(x.time_period.timestart.minute)
            if b < 10:
                b = f"0{b}"
            c = int(x.time_period.timeend.hour)
            if c < 10:
                c = f"0{c}"
            d = int(x.time_period.timeend.minute)
            if d < 10:
                d = f"0{d}"
            timestart = f"{a}:{b}"
            timeend = f"{c}:{d}"

            #vars
            timedate = f"{day}/{month}/{year}"
            patient = x.patient
            patientname = patient.fullName 
            is_checkup = x.is_checkup
            #get the proper strings
            if is_checkup:
                name = f"Followup for {patientname}"
                appointments += f'<li class="cd-schedule__event"><a data-start="{timestart}" data-end="{timeend}" data-content="event-sample" data-event="event-1" href = "event-sample.html" data-date="{timedate}"> <em class="cd-schedule__name">{name}</em></a></li>'
            else:
                name = f"Surgery for {patientname}"
                appointments += f'<li class="cd-schedule__event"><a data-start="{timestart}" data-end="{timeend}" data-content="event-sample" data-event="event-2" href = "event-sample.html" data-date="{timedate}"> <em class="cd-schedule__name">{name}</em></a></li>'
            appointments += '</ul>' 

        #add like you did before 
        day_string = f'<li class="cd-schedule__group"><div class="cd-schedule__top-info"><span>{dayofweek}</span></div><ul>'
        day_string += appointments
        day_string += '</ul></li>'
        days_string += day_string
    
        #the big string :)
        #<li class="cd-schedule__group"><div class="cd-schedule__top-info"><span></span></div><ul></ul></li>
        schedule_string = f'<div class = "cd-schedule__events"><ul><li class="cd-schedule__group"><div class="cd-schedule__top-info"><span></span></div><ul></ul></li><li class="cd-schedule__group"><div class="cd-schedule__top-info"><span></span></div><ul></ul></li>{days_string}<li class="cd-schedule__group"><div class="cd-schedule__top-info"><span></span></div><ul></ul></li><li class="cd-schedule__group"><div class="cd-schedule__top-info"><span></span></div><ul></ul></li></ul></div>'
        title = f'All Surgeries for {self.day}/{self.month}/{self.year} (dd/mm/yyyy)'
        #render
        return render(request, self.template_name, {"schedule_string":schedule_string, "title":title})



from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_protect
def eventsurgery(request):
    #get method, default for when rendered 
    if request.method == 'GET':
        #get GET data via Ajax response
        dataend = request.GET.get('dataend')
        if dataend:
            #get GET data via Ajax response
            datadate = request.GET.get('datadate')
            print(f'info:{dataend}{datadate}')
            dataend = dataend.split(':')
            #convert all to int
            dataend[0] = int(dataend[0])
            dataend[1] = int(dataend[1])
            datadate = datadate.split('/')
            datadate[0] = int(datadate[0])
            datadate[1] = int(datadate[1])
            datadate[2] = int(datadate[2])
            #^ all the values of the surgery we want to display 
            string = ''
            surgery = ''
            earliest_surgery = Surgery.objects.earliest('time_period__timestart')
            latest_surgery = Surgery.objects.latest('time_period__timestart')
            allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date())
            #loop through all surgeries
            for x in allsurgeries:
                #if the surgery is the right one to display break
                month = x.time_period.timeend.month
                day = x.time_period.timeend.day
                year = x.time_period.timeend.year
                hour = x.time_period.timeend.hour
                minute = x.time_period.timeend.minute
                if minute == dataend[1] and hour == dataend[0] and day == datadate[0] and month == datadate[1] and year == datadate[2]:
                    surgery = x
                    print('success')
                    break
            
            #info of the surgery itself
            patient = surgery.patient.fullName
            cleaners = ''
            print(surgery.cleaners)
            #add cleaners to info 
            for cleaner in surgery.cleaners.all():
                cleaners += f'{cleaner.fullName}, '
            cleaners = cleaners[:-2]
            
            notes = surgery.info
            surgeons = ''
            #add surgeon to info
            for surgeon in surgery.surgeons.all():
                surgeons += f'{surgeon.fullName}, '
            surgeons = surgeons[:-2]

            id = surgery.id
            is_checkup = surgery.is_checkup
            
            #display proper html link
            if not is_checkup:
                string = f'<!DOCTYPE html><html><head><link rel="stylesheet" href="/static/css/style.css"><script src = "/static/js/util.js"></script> <!-- util functions included in the CodyHouse framework --><script src = "/static/js/main.js"></script></head><body><div class="cd-schedule-modal__event-info"><h1>  Surgery Info</h1> <br> <h4>ID: {id} <h4><h4>Patient Name: {patient}</h4><h4>Surgeons: {surgeons}</h4><h4>Cleaners: {cleaners}</h4><h4>Notes: {notes}</h4><br><br><br><button onclick="Delete({dataend}, {datadate})">Delete Appointment</button></div></body></html>'
            else:
                string = f'<!DOCTYPE html><html><head><link rel="stylesheet" href="/static/css/style.css"><script src = "/static/js/util.js"></script> <!-- util functions included in the CodyHouse framework --><script src = "/static/js/main.js"></script></head><body><div class="cd-schedule-modal__event-info"><h1>  Followup Info</h1> <br> <h4>ID: {id} <h4><h4>Patient Name: {patient}</h4><h4>Surgeons: {surgeons}</h4><h4>Cleaners: {cleaners}</h4><h4>Notes: {notes}</h4><br><br><br><button onclick="Delete({dataend}, {datadate})">Delete Appointment</button></div></body></html>'
            
            #send data back to JS
            data = {'string':string}
            return JsonResponse(data)
        
    #post method, for the delete function
    else:
        #get the surgery info needed to delete 
        targetday = int(request.POST.get('day'))
        targetmonth = int(request.POST.get('month'))
        targetyear = int(request.POST.get('year'))
        targetminute = int(request.POST.get('minute'))
        targethour = int(request.POST.get('hour'))
        earliest_surgery = Surgery.objects.earliest('time_period__timestart')
        latest_surgery = Surgery.objects.latest('time_period__timestart')
        allsurgeries = get_surgeries(earliest_surgery.time_period.timestart.date(), latest_surgery.time_period.timestart.date())
        surgery = ''
        #loop through all surgeries
        for x in allsurgeries:
            month = x.time_period.timeend.month
            day = x.time_period.timeend.day
            year = x.time_period.timeend.year
            hour = x.time_period.timeend.hour
            minute = x.time_period.timeend.minute
            #if the surgery matches
            if minute == targetminute and hour == targethour and day == targetday and month == targetmonth and year == targetyear:
                #delete surgery
                x.delete()
                break
        #redirect back to personschedule
        return redirect('personschedule')


def get_surgeries(date_1, date_2):
	'''
	Returns all surgery objects with a start date between date_1 and date_2
	date_1, date_2 - date objects, ex: datetime.now().date()
	'''
    #all objects
	surgeries = Surgery.objects.all()
    #tracker
	filtered_surgeries = []
    #loop through
	for surgery in surgeries:
        #if between dates, append
		if surgery.date() >= date_1 and surgery.date() <= date_2:
			filtered_surgeries.append(surgery)

    #return 
	return filtered_surgeries