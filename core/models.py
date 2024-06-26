from django.db import models
from django.conf import settings 
# Create your models here.
"""
Classes for scheduling, employees (including surgeons, cleaner), patients.
Time, Employee, Surgeon, Cleaner, Patient, Surgery, Schedule
Progress: 
1/24/2024 - Classes for people created and initialized 
1/30/2024 - Classes for schedule created, some validation done 
2/06/2024 - Occupy and Conflict functions created 
2/06/2024 to 2/22/2024 - minor levels of cooking 
2/28/2024 - Changed intializes, added strings for all 
4/07 - Changed the class styling to have Django fields from regular python properties
"""
class Time(models.Model):
    """
    A model to represent a time interval with a start and end time.
    
    Attributes:
        timestart (DateTimeField): The starting time of the interval.
        timeend (DateTimeField): The ending time of the interval.
    """
    
    timestart = models.DateTimeField()
    timeend = models.DateTimeField()

    def __str__(self):
        """
        Returns:
            str: A string displaying the start and end time of the interval.
        """
        return f"Start: {self.timestart} End: {self.timeend}"

    def conflict(self, timeobject):
        """
        Determines if there is a conflict with another Time object.
        Args:
            timeobject (Time): Another Time object to compare with.
        
        Returns:
            bool: True if there is a conflict, False otherwise.
        """
        return self.timestart < timeobject.timeend and self.timeend > timeobject.timestart


class Employee(models.Model):
	'''
	Model to represent an employee.

	Attributes
		fullName (charfield): the fullname of the employeje
		availability (ManytoManyField of Time model): the time intervals at which the employee is available
		sched (ManytoManyField of Time model): the time intervals at which the employee is scheduled for work 
	'''
	fullName = models.CharField(max_length=100)
	availability = models.ManyToManyField(Time, related_name='available_employees')
	sched = models.ManyToManyField(Time, related_name='scheduled_employees')

	def __str__(self):
		"""
		String (representation of employee)
		"""
		return f"Type: Employee \nName: {self._fullName}\n\n"

class Surgeon(Employee):
	'''
	Model to represent a surgeon, which is a child of Employee
	Attributes 
		Inheritance from Employee attributes
		qualifications (charField): the qualifications of the surgeon
		exp (charField): the experience of the surgeon
	'''
	qualifications = models.CharField(max_length=100)
	exp = models.CharField(max_length=2)


	def __str__(self):
		"""
		String (for testing printing)
		"""
		return f"Surgeon Name: {self.fullName} \nExperience: {self.exp}\n\n"

	def qualcheck(self, type, title):
		"""
		determine qualifications for surgery
		"""
		if title == "Sr":
			if self.exp == "Jr":
				return False
		if type not in self.qualifications:
			return False
		return True

		
	def assignsurgeon(self, type, title, timestart, timeend):
		"""
		Give assignment to surgeon and change their availability and assignments
		Note: This is DIFFERENT than assigning a regular employee
		Attributes
			Self (surgeon)
			type - Surgery type
			title - title required (jr or sr)
			timestart (1d list of ints) - start of assignment
			timeend (1d list of ints) - end of assignment

		Returns
			True - Operation could be done
			False - Operation could not be done
		"""
		#if the surgeon does not have the necessary credentials
		if self.qualcheck(self, type, title) == False:
			return False
		else:
			#otherwise assign - this doesnt necessarily return True, if there is a conflict it will return False in self.conflict()
			self.assign(self, timestart, timeend)
			return True
	

class Cleaner(Employee):
	'''
	A child of the Employee model, this class represents an employee
	'''
	def __str__(self):
		"""
		String (for testing printing)
		"""
		return f"Cleaner Name: {self.fullName}\n"

class Patient(models.Model):
	'''
	Model represents a patient in the hospital
	Attributes
		fullName (charfield): the Patient's full name
		condition_type (charfield): the medical condition of the patient'
		severity (charfield): the level of severity of the surgery
		admission_date (DateField): the date of admission, when condition was first known
		status (charField): the current status of the surgery
	'''
	fullName = models.CharField(max_length=255)
	condition_type = models.CharField(max_length=255, null=True)
	severity = models.CharField(max_length=255, null=True)
	admission_date = models.DateField(null=True)
	status = models.CharField(max_length=255, null=True)

	def __str__(self):
		"""
		String (for testing printing)
		"""
		return f"Patient Name: {self.fullName} \nCondition Type: {self.condition_type} \nSeverity: {self.severity}\n\n"
 
class Surgery(models.Model):
	"""
	Class for a specific Surgery
	Attributes
		surgeons - surgeon object
		cleaners - cleaner object
		patient - patient object
		time - time object
		info - string
		ischeckup - boolean 
		user - user object
	"""
	surgeons = models.ManyToManyField(Surgeon)
	cleaners = models.ManyToManyField(Cleaner)
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	time_period = models.ForeignKey(Time, on_delete=models.CASCADE) 
	info = models.CharField(max_length=500, null=True, blank=True)
	is_checkup = models.BooleanField(default = False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True )

	
	def date(self):
		'''
		Returns date of surgery
		'''
		return self.time_period.timestart.date()

	def __str__(self):
		"""
		print statement for testing
		"""
		s1 = ''
		s2 = ''
		for surgeon in self.surgeons.all():
			s1 += str(surgeon) 
		for cleaner in self.cleaners.all():
			s2 += str(cleaner) 
		return f"Surgeons:\n {s1} \nCleaners: \n{s2} \nPatient: \n{self.patient} {self.time_period}\n\n"
	


