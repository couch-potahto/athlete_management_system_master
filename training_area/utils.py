from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import *
from django.db.models import Q

class Calendar(HTMLCalendar):
	def __init__(self, person, year=None, month=None):
		self.year = year
		self.month = month
		self.person = person
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day)
		if self.person.is_athlete and events_per_day and self.person.athlete.coach:
			events_per_day = events_per_day.filter(Q(user=self.person) | Q(user=self.person.athlete.coach.user))
		elif self.person.is_coach and events_per_day and self.person.coach.coach.all:
			print('T')
			athlete_list = Athlete.objects.filter(coach=self.person.coach)
			print(athlete_list)
			for athlete in athlete_list:
				events_per_day = events_per_day.filter(Q(user=self.person) | Q(user=athlete.user))


		d = ''
		for event in events_per_day:
			d += f'<li> {event.get_html_url} </li>'

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
