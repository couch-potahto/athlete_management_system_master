from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from functools import reduce
import operator
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView, View
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
from decimal import Decimal
import calendar


from ..decorators import coach_required, athlete_required
from ..forms import CoachSignUpForm, EventForm, AddCommentForm
from ..models import User, Coach, Athlete, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, RepMax, Event, Notifications, Comment
from ..utils import Calendar
from rest_framework.views import APIView
from rest_framework.response import Response


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
		workout=self.get_object()
		context = super(WorkoutDetail, self).get_context_data(**kwargs)
		all_movements = Movement.objects.filter(workout=self.get_object()).order_by('id')
		unique_names = []
		descriptions = {}
		for item in all_movements:
			if item.movement_name not in unique_names:
				unique_names.append(item.movement_name)
			if item.movement_name not in descriptions:
				descriptions[item.movement_name]=item.description
		total = []
		for name in unique_names:
			movement = list(workout.work.all().filter(movement_name=name).order_by('id'))
			total.extend(movement)
		context['movements'] = total
		context['descriptions'] = descriptions
		context['accessories'] = workout.accessories.all().order_by('id')
		print(workout.accessories.all())

		#context['movements'] = Movement.objects.filter(workout=self.get_object()).order_by('movement_name').order_by('id')
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
		#print(result)
		query = self.request.GET.get('search_box')
		#print(self.request.GET.get('search_box'))
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
			#print(query_list)
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
	#print(comment_id)
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





class ChartView(View):
	def get(self, request, *args, **kwargs):
		#print(self.request.user)
		return render(request, 'training_area/app/chart.html', {})

	def post(self, request, *args, **kwargs):

		#print(request.POST)
		req = request.POST.get('athlete')
		lift = request.POST.get('lifts')
		#print("<<>>")
		#print(lift)
		athlete = Athlete.objects.filter(user__username=req)[0]
		mesocycle_of_interest = Mesocycle.objects.filter(athlete__user__id=athlete.pk)[0]
		labels = []
		e1rm = []
		for microcycle in mesocycle_of_interest.meso.all():
			labels.append(microcycle.microcycle_name)
			highest_rm = 0
			for workout in microcycle.micro.all():
				movements_of_interest = Movement.objects.filter(workout__id=workout.pk, movement_name=lift)
				if movements_of_interest:
					for movement in movements_of_interest:
						repetitions = movement.num_reps_done
						if repetitions > 10:
							continue
						exertion = movement.rpe
						corresponding_percentage = ExertionPerceived.objects.filter(rep_scale=repetitions, exertion_scale=exertion)[0].percent
						estimated_repmax = Decimal(movement.kg_done)/Decimal(corresponding_percentage)
						#print(estimated_repmax)
						if estimated_repmax>highest_rm:
							highest_rm = estimated_repmax

				e1rm.append(highest_rm)
				#print(movements_of_interest)
			#print(labels)
			#print(e1rm)
		#print(athlete)
		data = {
			"labels": labels,
			"default":e1rm,
		}
		return render(request, 'training_area/app/chart.html', {'data':data})

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# use today's date for the calendar
		all_athletes = self.request.user
		context['all_athletes'] = all_athletes
		return context

def get_data(request, *args, **kwargs):
	#print(request.POST.get('athlete'))
	data = {
		"sales":100,
		"customers":10,
	}
	return JsonResponse(data)


def load_lifts(request):
	#print('entered')
	mesocycle_pk = request.GET.get('mesocycle')

	mesocycle = get_object_or_404(Mesocycle, pk = int(mesocycle_pk))
	#print(mesocycle)
	microcycles = mesocycle.meso.all()
	lifts = []
	check = []
	for micro in microcycles:
		for workout in micro.micro.all():
			for lift in workout.work.all():
				if lift.movement_name not in check:
					lifts.append(lift)
					check.append(lift.movement_name)
	print(lifts)
	return render(request, 'training_area/app/lift_dropdown_list.html', {'all_lifts': lifts})

def load_meso(request):
	#print('entered')
	athlete_user = request.GET.get('athlete')

	athlete = Athlete.objects.filter(user__username = athlete_user)[0]
	#print(athlete)
	all_meso = athlete.meso_athlete.all()
	mesocycles = []
	check = []
	for meso in all_meso:
		mesocycles.append(meso)
	return render(request, 'training_area/app/mesocycle_dropdown_list.html', {'all_mesocycles': mesocycles})

def testpost(request):
		req = request.GET.get('athlete')
		lift = request.GET.getlist('lift[]')
		meso = request.GET.get('meso')
		athlete = Athlete.objects.filter(user__username=req)[0]
		mesocycle_of_interest = get_object_or_404(Mesocycle, pk=meso)
		labels = []

		all_e1rm = []
		i = 0;
		for movement in lift:
			movement_name = movement
			e1rm = []
			for microcycle in mesocycle_of_interest.meso.all():
				if microcycle.microcycle_name not in labels:
					labels.append(microcycle.microcycle_name)
				highest_rm = 0
				for workout in microcycle.micro.all():
					movements_of_interest = Movement.objects.filter(workout__id=workout.pk, movement_name=movement_name)

					if movements_of_interest:
						for movement in movements_of_interest:
							repetitions = movement.num_reps_done
							#print(movement.pk)
							if repetitions > 10:
								continue

							exertion = movement.rpe
							corresponding_percentage = ExertionPerceived.objects.filter(rep_scale=repetitions, exertion_scale=exertion)[0].percent
							estimated_repmax = Decimal(movement.kg_done)/Decimal(corresponding_percentage)
							if estimated_repmax>highest_rm:
								highest_rm = estimated_repmax

				e1rm.append(highest_rm)
			i = i + 1

			all_e1rm.append(e1rm)

		data = {
			"labels": labels,
			"default":all_e1rm,
			"name": lift,
		}
		return JsonResponse(data)

def display_metrics(request):
	mesocycle_pk = request.GET.get('mesocycle')
	mesocycle= get_object_or_404(Mesocycle, pk=int(mesocycle_pk))
	microcycles = mesocycle.meso.all()
	average_weekly_squat_rpe = []
	average_weekly_bench_rpe = []
	average_weekly_deadlift_rpe = []
	average_weekly_squat_volume = []
	average_weekly_bench_volume = []
	average_weekly_deadlift_volume = []
	average_weekly_squat_intensity = []
	average_weekly_bench_intensity = []
	average_weekly_deadlift_intensity = []
	squat_workouts = []
	squat_day = 1
	bench_workouts = []
	bench_day = 1
	deadlift_workouts = []
	deadlift_day = 1
	workoutly_fatigue = []
	all_workouts = []
	week = []
	for micro in microcycles:
		for workout in micro.micro.all().order_by('id'):
			if not workout.completed:
				continue
			workoutly_fatigue.append(workout.fatigue_rating)
			all_workouts.append(micro.microcycle_name+' '+workout.workout_name)
			all_movements = Movement.objects.filter(
				workout=workout)
			squats = all_movements.filter(movement_name__icontains='squat')
			bench = all_movements.filter(movement_name__icontains='press')
			deadlift = all_movements.filter(movement_name__icontains='deadlift')
			week.append(micro.microcycle_name)
		#NT = NL * %1rm
			if squats:
				#average_weekly_squat_rpe.append(0)
				#average_weekly_squat_volume.append(0)
			#else:
				total_NT = 0
				total_RPE = 0
				total_reps = 0
				for movement in squats:
				#print(movement.rpe)
					if movement.rpe < 2 or movement.rpe > 10:
						messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has invalid RPE")
						continue
					elif movement.num_reps<1 or movement.num_reps > 10:
						if movement.percentage:
							NT = movement.num_reps * (Decimal(movement.percentage)/Decimal(100))
						else:
							messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has no percentage or repetitions")
							continue
					else:
						exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe)[0]
						NT = movement.num_reps * exertion.percent
				#print(exertion)
					
					total_NT = total_NT + NT
					total_RPE = total_RPE + movement.rpe
					total_reps += movement.num_reps
				average_weekly_squat_rpe.append(float(total_RPE / len(squats)))
				average_weekly_squat_volume.append(float(total_NT))
				average_weekly_squat_intensity.append(float(total_NT/total_reps))
				squat_workouts.append(micro.microcycle_name+' S' + str(squat_day))
				squat_day+=1
			#print(average_weekly_squat_rpe)
			#print(average_weekly_squat_volume)

			if bench:
			#	average_weekly_bench_rpe.append(0)
			#	average_weekly_bench_volume.append(0)
			#else:
				total_NT = 0
				total_RPE = 0
				total_reps = 0
				for movement in bench:
					if movement.rpe < 2 or movement.rpe > 10:
						messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has invalid RPE")
						continue
					elif movement.num_reps<1 or movement.num_reps > 10:
						if movement.percentage:
							NT = movement.num_reps * (Decimal(movement.percentage)/Decimal(100))
						else:
							messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has no percentage or repetitions")
							continue
					else:
						exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe)[0]
						NT = movement.num_reps * exertion.percent
				#print(movement.rpe)
					#exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe)[0]
				#print(exertion)
					NT = movement.num_reps * exertion.percent
					total_NT = total_NT + NT
					total_RPE = total_RPE + movement.rpe
					total_reps += movement.num_reps
				average_weekly_bench_rpe.append(float(total_RPE / len(bench)))
				average_weekly_bench_volume.append(float(total_NT))
				average_weekly_bench_intensity.append(float(total_NT/total_reps))
				bench_workouts.append(micro.microcycle_name+' B' + str(bench_day))
				bench_day+=1
			if deadlift:
				#average_weekly_deadlift_rpe.append(0)
				#average_weekly_deadlift_volume.append(0)
			#else:
				total_NT = 0
				total_RPE = 0
				total_reps = 0
				for movement in deadlift:
					if movement.rpe < 2 or movement.rpe > 10:
						messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has invalid RPE")
						continue
					elif movement.num_reps<1 or movement.num_reps > 10:
						if movement.percentage:
							NT = movement.num_reps * (Decimal(movement.percentage)/Decimal(100))
						else:
							messages.warning(request, movement.movement_name+" in"+movement.workout.workout_name+" has no percentage or repetitions")
							continue
					else:
						exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe)[0]
						NT = movement.num_reps * exertion.percent
				#print(movement.rpe)
					#exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe)[0]
				#print(exertion)
					NT = movement.num_reps * exertion.percent
					total_NT = total_NT + NT
					total_RPE = total_RPE + movement.rpe
					total_reps += movement.num_reps
				average_weekly_deadlift_rpe.append(float(total_RPE / len(deadlift)))
				average_weekly_deadlift_volume.append(float(total_NT))
				average_weekly_deadlift_intensity.append(float(total_NT/total_reps))
				deadlift_workouts.append(micro.microcycle_name+' D' + str(deadlift_day))
				deadlift_day+=1

	data = {
		"test": mesocycle_pk,
		"average_weekly_squat_rpe": average_weekly_squat_rpe,
		"average_weekly_bench_rpe": average_weekly_bench_rpe,
		"average_weekly_deadlift_rpe": average_weekly_deadlift_rpe,
		"average_weekly_squat_volume": average_weekly_squat_volume,
		"average_weekly_bench_volume": average_weekly_bench_volume,
		"average_weekly_deadlift_volume": average_weekly_deadlift_volume,
		"average_weekly_squat_intensity": average_weekly_squat_intensity,
		"average_weekly_bench_intensity": average_weekly_bench_intensity,
		"average_weekly_deadlift_intensity": average_weekly_deadlift_intensity,
		"squat_workouts": squat_workouts,
		"bench_workouts": bench_workouts,
		"deadlift_workouts": deadlift_workouts,
		"workoutly_fatigue": workoutly_fatigue,
		"all_workouts": all_workouts,
		"week": week,
	}
	return JsonResponse(data)

def validate_kg(request):
	#print(request.user)
	movement_pk = request.POST.get('pk')
	movement_kg = request.POST.get('kg_done')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	if request.user.is_athlete:
		movement_of_interest.kg_done = movement_kg
	else:
		movement_of_interest.kg = movement_kg
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_num_reps(request):
	movement_pk = request.POST.get('pk')
	movement_num_reps = request.POST.get('num_reps_done')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	if request.user.is_athlete:
		movement_of_interest.num_reps_done = movement_num_reps
	else:
		movement_of_interest.num_reps = movement_num_reps
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)


def validate_rpe(request):
	movement_pk = request.POST.get('pk')
	movement_rpe = request.POST.get('rpe')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	movement_of_interest.rpe = movement_rpe
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_movement_name(request):
	movement_pk = request.POST.get('pk')
	movement_name = request.POST.get('movement_name')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	movement_of_interest.movement_name = movement_name
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_percentage(request):
	movement_pk = request.POST.get('pk')
	percentage = request.POST.get('percentage')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	movement_of_interest.percentage = percentage
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_rm(request):
	movement_pk = request.POST.get('pk')
	rm = request.POST.get('rm')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	if movement_of_interest.percentage:
		movement_of_interest.kg = round((Decimal(rm) * (Decimal(movement_of_interest.percentage)/Decimal(100)))/Decimal(2.5)) * Decimal(2.5)
		movement_of_interest.save()
	else:
		messages.warning(request, 'No Percentage Given')
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_checked(request):
	movement_pk = request.POST.get('pk')
	checked = request.POST.get('checked')
	movement_of_interest = get_object_or_404(Movement, pk=movement_pk)
	movement_of_interest.is_backoff = not movement_of_interest.is_backoff
	movement_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_workout_name(request):
	workout_pk = request.POST.get('pk')
	workout_name = request.POST.get('workout_name')
	workout_of_interest = get_object_or_404(Workout, pk=workout_pk)
	workout_of_interest.workout_name = workout_name
	workout_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_description(request):
	workout_pk = request.POST.get('pk')
	description = request.POST.get('description')
	old_name = request.POST.get('old_name')
	workout_of_interest = get_object_or_404(Workout, pk=workout_pk)
	movements_of_interest = workout_of_interest.work.all().filter(movement_name=old_name)
	for item in movements_of_interest:
		item.description = description
		item.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_movement_group_name(request):
	workout_pk = request.POST.get('pk')
	movement_name = request.POST.get('movement_name')
	old_name = request.POST.get('old_name')

	workout_of_interest = get_object_or_404(Workout, pk=workout_pk)
	movements_of_interest = workout_of_interest.work.all().filter(movement_name=old_name)
	for item in movements_of_interest:
		item.movement_name = movement_name
		item.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def validate_mesocycle_name(request):
	mesocycle_pk = request.POST.get('pk')
	mesocycle_name = request.POST.get('mesocycle_name')
	mesocycle_of_interest = get_object_or_404(Mesocycle, pk=mesocycle_pk)
	mesocycle_of_interest.mesocycle_name = mesocycle_name
	mesocycle_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

class ChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self,request,format=None):
		qs_count = User.objects.all().count()
		labels = ['Users', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
		default_items = [qs_count, 1234, 12, 10, 111, 999]
		data = {
			"labels":labels,
			"default":default_items,
		}
		return Response(data)

	def post(self, request):
		req = request.POST.get('athlete')
		lift = request.POST.get('lifts')

		athlete = Athlete.objects.filter(user__username=req)[0]
		mesocycle_of_interest = Mesocycle.objects.filter(athlete__user__id=athlete.pk)[0]
		labels = []
		e1rm = []
		for microcycle in mesocycle_of_interest.meso.all():
			labels.append(microcycle.microcycle_name)
			highest_rm = 0
			for workout in microcycle.micro.all():
				movements_of_interest = Movement.objects.filter(workout__id=workout.pk, movement_name=lift)
				if movements_of_interest:
					for movement in movements_of_interest:
						repetitions = movement.num_reps_done
						if repetitions > 10:
							continue
						exertion = movement.rpe
						corresponding_percentage = ExertionPerceived.objects.filter(rep_scale=repetitions, exertion_scale=exertion)[0].percent
						estimated_repmax = Decimal(movement.kg_done)/Decimal(corresponding_percentage)

						if estimated_repmax>highest_rm:
							highest_rm = estimated_repmax

				e1rm.append(highest_rm)
				#print(movements_of_interest)

		data = {
			"labels": labels,
			"default":e1rm,
		}
		return Response(data)



