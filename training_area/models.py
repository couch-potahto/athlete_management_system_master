from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.html import escape, mark_safe
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from decimal import *

class User(AbstractUser):
	is_athlete = models.BooleanField(default = False)
	is_coach = models.BooleanField(default = False)
	email = models.EmailField(max_length=255, blank=True)

class Coach(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
	first_name = models.CharField(max_length = 255, blank = False, verbose_name= _('First Name'))
	last_name = models.CharField(max_length = 255, blank = True, verbose_name= _('Last Name'))
	bio = models.TextField(max_length = 500, blank = True)

	def get_absolute_url(self):
		#return "/coach/%i/" % self.user_id
		return "/coach/%s/" % self.user

class Team(models.Model):
	team_name = models.CharField(max_length = 255, blank = False)
	description = models.TextField(max_length = 500, blank = True)
	coach = models.ForeignKey(Coach, related_name = 'team_coach', on_delete = models.CASCADE, null = True)

class Athlete(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
	first_name = models.TextField(max_length = 50, blank = False, verbose_name= _('First Name'))
	last_name = models.TextField(max_length = 50, blank = False, verbose_name= _('Last Name'))
	team = models.ForeignKey(Team, related_name = 'team', on_delete = models.CASCADE, null = True)
	coach = models.ForeignKey(Coach, related_name = 'coach', on_delete = models.CASCADE, null = True)

	def get_absolute_url(self):
		#return "/coach/%i/" % self.user_id
		return "/athlete/%s/" % self.user


class RepMax(models.Model):
	rep_max_name = models.CharField(max_length=255, blank = False, verbose_name= _('RM Name'))
	athlete = models.ForeignKey(Athlete, related_name = 'athlete_rm',
		on_delete = models.CASCADE, null=True)
	rep_max = models.SmallIntegerField(null = True, verbose_name= _('1-RM'))

	def __str__(self):
		presented = self.rep_max_name + ': ' + str(self.rep_max)
		return presented


class Macrocycle(models.Model):
	macrocycle_name = models.CharField(max_length=255, blank = False, verbose_name= _('Macrocycle Name'))
	descripton = models.TextField(max_length = 500, null = True)
	athlete = models.ForeignKey(Athlete, related_name = 'mac_athlete',
		on_delete = models.CASCADE, null=True)
	coach = models.ForeignKey(Coach, related_name = 'mac_coach',
		on_delete = models.CASCADE, null=True)
	completed = models.BooleanField(default = False)

class Mesocycle(models.Model):
	mesocycle_name = models.CharField(max_length = 255, blank = False, verbose_name= _('Mesocycle Name'))
	descripton = models.TextField(max_length = 500, null = True)
	macrocycle = models.ForeignKey(Macrocycle, related_name = 'mac_cycle',
		on_delete = models.CASCADE, null = True)
	completed = models.BooleanField(default = False)
	athlete = models.ForeignKey(Athlete, related_name = 'meso_athlete',
		on_delete = models.CASCADE, null=True)
	coach = models.ForeignKey(Coach, related_name = 'meso_coach',
		on_delete = models.CASCADE, null=True)

class Microcycle(models.Model):
	microcycle_name = models.CharField(max_length = 255, blank = False, verbose_name= _('Microcycle Name'))
	mesocycle = models.ForeignKey(Mesocycle, related_name = 'meso',
		on_delete = models.CASCADE, null = True)
	completed = models.BooleanField(default = False)
	athlete = models.ForeignKey(Athlete, related_name = 'micro_athlete',
		on_delete = models.CASCADE, null=True)
	coach = models.ForeignKey(Coach, related_name = 'micro_coach',
		on_delete = models.CASCADE, null=True)

	def __str__(self):
		return self.microcycle_name

	@property
	def get_html_url(self):
		url = reverse('app:micro_detail', args=(self.athlete.user.id, self.id))
		return f'<a href="{url}"> {self.microcycle_name} </a>'

class Workout(models.Model):
	workout_name = models.CharField(max_length = 255, blank = False, verbose_name= _('Workout Name'))
	alert = models.BooleanField(default = False, null = True)
	feedback = models.TextField(max_length = 500, blank = True)
	microcycle = models.ForeignKey(Microcycle, related_name = 'micro',
		on_delete = models.SET_NULL, null = True)
	completed = models.BooleanField(default = False)
	athlete = models.ForeignKey(Athlete, related_name = 'workout_athlete',
		on_delete = models.CASCADE, null=True)
	coach = models.ForeignKey(Coach, related_name = 'workout_coach',
		on_delete = models.CASCADE, null=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return self.workout_name

class Movement(models.Model):
	movement_name = models.CharField(max_length = 255,blank = False, verbose_name= _('Movement Name'))
	num_reps = models.SmallIntegerField(verbose_name= _('Repetitions'))
	num_reps_done = models.SmallIntegerField(null = True, verbose_name= _('Repetitions Completed'))
	kg_done = models.DecimalField(
		null = True,
		max_digits=6,
		decimal_places=2,
		verbose_name= _('Load Completed')
	)
	rpe = models.DecimalField(null = True,
		max_digits=3,
		decimal_places=1,
		blank=True, verbose_name= _('RPE'),
		validators=[MaxValueValidator(10), MinValueValidator(0)]
	)
	kg = models.DecimalField(
		blank=True,
		null = True,
		max_digits=6,
		decimal_places=2,
		verbose_name= _('Load')
	)
	workout = models.ForeignKey(Workout, related_name = 'work',
		on_delete = models.CASCADE, null = True)
	is_backoff = models.BooleanField(default = False, verbose_name= _('Backoff set?'))
	percentage = models.DecimalField(
		null = True,
		blank=True,
		max_digits=5,
		decimal_places=2,
		validators=[MaxValueValidator(100), MinValueValidator(0)]
	)

class ExertionPerceived(models.Model):
	RTS = 'RTS'
	TSA = 'TSA'
	SCALE_TYPE_CHOICES = (
		(RTS, 'RTS'),
		(TSA, 'TSA')
	)
	scale_type = models.CharField(
		max_length=10,
		choices=SCALE_TYPE_CHOICES,
		default=RTS,
		verbose_name= _('Chart Type'))
	rep_scale = models.SmallIntegerField(null=True,
		blank=True
	)
	exertion_scale = models.DecimalField(null=True,
		blank=True,
		max_digits=3,
		decimal_places=1,
		validators=[MaxValueValidator(10), MinValueValidator(0)]
	)
	percent = models.DecimalField(
		null = True,
		blank=True,
		max_digits=5,
		decimal_places=4,
		validators=[MaxValueValidator(1), MinValueValidator(0)]
	)

	def get_percent(self):
		return self.percent * Decimal(100)
# Create your models here.

class Event(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank = True, null = True)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	user = models.ForeignKey(User, related_name = 'user_calendar',
		on_delete = models.CASCADE, null=True, blank=True)

	@property
	def get_html_url(self):
		url = reverse('app:event_edit', args=(self.id,))
		return f'<a href="{url}"> {self.user}: {self.title} </a>'

class Notifications(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	title = models.CharField(max_length=150, verbose_name="Title")
	content = models.TextField(verbose_name="Content", blank = True)
	sender = models.ForeignKey(User, related_name = "notif_send", null = True, on_delete=models.CASCADE)
	reciever = models.ForeignKey(User, related_name = "notif_recieve", null = True, on_delete=models.CASCADE)

class Comment(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, null=True)
	updated_at = models.DateTimeField(auto_now=True)
	workout = models.ForeignKey(Workout, related_name = 'comments',
		on_delete = models.CASCADE, null = True)
	creator = models.ForeignKey(User, related_name = "user_comments", null = True, on_delete=models.CASCADE)
	content = models.TextField(verbose_name="Content")