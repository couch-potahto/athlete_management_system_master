from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from functools import reduce
import operator
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta, date
from django.views import generic
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import template
from django.core.paginator import Paginator
import calendar


from ..decorators import coach_required, athlete_required
from ..forms import CoachSignUpForm, EventForm, AddCommentForm
from ..models import User, Coach, Athlete, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, RepMax, Event, Notifications, Comment
from ..utils import Calendar

@method_decorator([login_required], name='dispatch')
class LogView(ListView):
	model = Athlete
	context_object_name = 'all_workouts'
	template_name = 'training_area/app/log_view.html'
	paginate_by = 5

	def get_queryset(self):
		return Workout.objects.filter(athlete__user__id=self.kwargs['pk']).order_by('completed', '-created_at')

	def get_context_data(self, **kwargs):
		context = super(LogView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		#p = Paginator(Microcycle.objects.filter(athlete__user__id=self.kwargs['pk']).order_by('-id'), self.paginate_by)
		#context['lolol'] = p.page(context['page_obj'].number)
		context['all_microcycles'] = Microcycle.objects.filter(athlete__user__id=self.kwargs['pk']).order_by('-id')
		context['all_mesocycles'] = Mesocycle.objects.filter(athlete__user__id=self.kwargs['pk'])

		return context

@method_decorator([login_required], name='dispatch')
class MicrocycleDetail(DetailView):
	model = Microcycle
	context_object_name = 'microcycle'
	pk_url_kwarg = 'pk_2'
	template_name = 'training_area/app/micro_detail.html'

	def get_context_data(self, **kwargs):
		report = {}
		context = super(MicrocycleDetail, self).get_context_data(**kwargs)
		workouts_in_micro = Workout.objects.filter(microcycle_id=self.kwargs['pk_2']).order_by('created_at')
		for workout in workouts_in_micro:
			report[workout.workout_name]={}
			for movement in workout.work.all().order_by('id'):
				if movement.movement_name not in report[workout.workout_name]:
					report[workout.workout_name][movement.movement_name]=[[movement.kg, movement.num_reps, movement.rpe, movement.kg_done],]
				else:
					report[workout.workout_name][movement.movement_name].append([movement.kg, movement.num_reps, movement.rpe, movement.kg_done])
		context['report'] = report
		context['all_workouts'] = workouts_in_micro
		return context

@method_decorator([login_required], name='dispatch')
class WorkoutDetail(DetailView):
	model = Workout
	context_object_name = 'workout'
	pk_url_kwarg = 'pk_2'
	template_name = 'training_area/app/workout_detail.html'

	def get_context_data(self, **kwargs):
		 # xxx will be available in the template as the related objects
		context = super(WorkoutDetail, self).get_context_data(**kwargs)
		context['movements'] = Movement.objects.filter(workout=self.get_object()).order_by('id')
		context['rm'] = RepMax.objects.filter(athlete__user_id=self.kwargs['pk'])
		context['comments'] = Comment.objects.filter(workout__id=self.kwargs['pk_2']).order_by('-created_at')
		return context

@method_decorator([login_required], name='dispatch')
class ProfileView(DetailView):
	model = User
	slug_field = "username"
	template_name = 'training_area/app/user_detail.html'


@method_decorator([login_required, athlete_required], name='dispatch')
class SearchCoachView(ListView):
	model = Coach
	context_object_name = 'relevant_coaches'
	template_name = 'training_area/app/coach_search.html'

	def get_queryset(self):
		result = Coach.objects.all()
		print(result)
		query = self.request.GET.get('search_box')
		print(self.request.GET.get('search_box'))
		if query:
			query_list = query.split()
			result = result.filter(
				reduce(operator.and_,
						(Q(user__username__icontains=q) for q in query_list))
			)
		return result


@method_decorator([login_required], name='dispatch')
class RPEView(ListView):
	model = ExertionPerceived
	context_object_name = 'all_rpe'
	template_name = 'training_area/app/rpe_chart.html'

	def get_queryset(self):
		return ExertionPerceived.objects.filter(scale_type=self.kwargs['chart_type']).order_by('-exertion_scale', '-percent')

	def get_context_data(self, **kwargs):
		context = super(RPEView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		return context

@method_decorator([login_required, coach_required], name='dispatch')
class SearchAthleteView(ListView):
	model = Athlete
	context_object_name = 'relevant_athletes'
	template_name = 'training_area/app/athlete_search.html'

	def get_queryset(self):
		result = Athlete.objects.filter(coach__user__id=self.kwargs['pk'])
		query = self.request.GET.get('search_box')
		if query:
			query_list = query.split()
			print(query_list)
			result = result.filter(
				reduce(operator.and_,
						(Q(user__username__icontains=q) for q in query_list))
			)

		return result

@method_decorator([login_required], name='dispatch')
class SearchWorkoutView(ListView):
	model = Workout
	context_object_name = 'relevant_workouts'
	template_name = 'training_area/app/workout_search.html'

	def get_queryset(self):
		result = Workout.objects.filter(athlete__user__id=self.kwargs['pk'])
		query = self.request.GET.get('search_box')
		if query:
			query_list = query.split()
			result = result.filter(
				reduce(operator.and_,
						(Q(workout_name__icontains=q) for q in query_list))
			)

		return result



def delete_notification(request, notif_id):
	notif = get_object_or_404(Notifications, pk=notif_id)
	person = notif.reciever
	notif.delete()
	if person.is_coach:
		return redirect('coach:dashboard')
	else:
		return redirect('athlete:dashboard')

def delete_all_notifications(request):
	notif = Notifications.objects.filter(reciever=request.user)
	for item in notif:
		item.delete()
	if request.user.is_coach:
		return redirect('coach:dashboard')
	else:
		return redirect('athlete:dashboard')

def add_comment(request, workout_id):
	if request.POST:
		form = AddCommentForm(request.POST)
		if form.is_valid():
			comment = form.save()
			comment.workout = Workout.objects.filter(id=workout_id)[0]
			comment.creator = request.user
			comment.save()
			message = comment.creator.username + " has added a comment to " + comment.workout.get_html_url
			if comment.creator.is_coach:
				notification = Notifications(title=message, sender=comment.creator, reciever=comment.workout.athlete.user)
			else:
				notification = Notifications(title=message, sender=comment.creator, reciever=comment.creator.athlete.coach.user)
			notification.save()
			messages.success(request, 'The Comment was Created!')
		return redirect('app:workout_detail', comment.workout.athlete.pk, comment.workout.pk)

def delete_comment(request, comment_id):
	print(comment_id)
	comment = get_object_or_404(Comment, pk=comment_id)
	workout = comment.workout
	comment.delete()
	messages.success(request, "The Comment was Deleted!")
	return redirect('app:workout_detail', workout.athlete.pk, workout.pk)

register = template.Library()
@register.inclusion_tag("training_area/tags/my_calendar.html")
class CalendarView(generic.ListView):
    model = Event
    template_name = 'training_area/app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(self.request.user, d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

#@method_decorator([login_required], name='dispatch')
@login_required
def event(request, event_id=None):
	instance = Event()
	if event_id:
		instance = get_object_or_404(Event, pk=event_id)
	else:
		instance = Event()

	form = EventForm(request.POST or None, instance=instance)
	if request.POST and form.is_valid():
		event = form.save()
		event.user = request.user
		event.save()
		message = event.user.username + " has added an event: " + event.get_html_url
		if event.user.is_coach:
			for athlete in event.user.coach.coach.all():
				notification = Notifications(title=message, sender=event.user, reciever=athlete.user)
				notification.save()
		else:
			notification = Notifications(title=message, sender=event.user, reciever=event.user.athlete.coach.user)
			
		notification.save()
		return HttpResponseRedirect(reverse('app:calendar'))
		messages.success(request, "Event has been added!")
	return render(request, 'training_area/app/event.html', {'form': form})

def delete_event(request, event_id):
	event = get_object_or_404(Event, pk=event_id)
	event.delete()
	messages.success(request, "Event has been deleted!")
	return redirect('app:calendar')