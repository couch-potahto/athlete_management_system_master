from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from functools import reduce
import operator
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from ..decorators import coach_required, athlete_required
from ..forms import CoachSignUpForm
from ..models import User, Coach, Athlete, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, RepMax

@method_decorator([login_required], name='dispatch')
class LogView(ListView):
	model = Athlete
	context_object_name = 'all_workouts'
	template_name = 'training_area/app/log_view.html'

	def get_queryset(self):
		return Workout.objects.filter(athlete__user__id=self.kwargs['pk']).order_by('completed', '-created_at')

	def get_context_data(self, **kwargs):
		context = super(LogView, self).get_context_data(**kwargs)
		context['pk'] = self.kwargs['pk']
		context['all_microcycles'] = Microcycle.objects.filter(athlete__user__id=self.kwargs['pk']).order_by('id')
		context['all_macrocycles'] = Macrocycle.objects.filter(athlete__user__id=self.kwargs['pk'])

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
