from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.forms import formset_factory, inlineformset_factory
from decimal import *
from datetime import datetime, timedelta
from django.db.models import Q

from ..decorators import athlete_required
from ..forms import AthleteSignUpForm, WorkoutForm, EditMovementFormAthlete
from ..models import User, Coach, Athlete, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, Event, Notifications, Comment, Accessory

class AthleteSignUpView(CreateView):
	model = User
	form_class = AthleteSignUpForm
	template_name = 'registration/signup_form.html'

	def get_context_data(self, **kwargs):
		kwargs['user_type'] = 'Athlete'
		return super().get_context_data(**kwargs)

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return redirect('login')


@method_decorator([login_required, athlete_required], name='dispatch')
class DashboardView(ListView):
	model = Workout
	context_object_name = 'all_workouts'
	template_name = 'training_area/athlete/dashboard.html'

	def get_queryset(self):
		return Workout.objects.filter(athlete__user=self.request.user).order_by('completed', '-created_at')[:10]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		calendar = {}
		today = datetime.now() + timedelta(days=-1)

		x=today
		in_thirty_days = today + timedelta(days=30)
		#print(in_thirty_days)
		events = Event.objects.filter(start_time__gte=today, end_time__lte=in_thirty_days)
		if events:
			if self.request.user.athlete.coach:
				events=events.filter(Q(user=self.request.user) | Q(user=self.request.user.athlete.coach.user))
			else:
				events=events.filter(Q(user=self.request.user))
			for item in events:
				calendar[item.title]=[item.start_time, item.end_time]
			context['calendar'] = calendar
		notifications = Notifications.objects.filter(reciever=self.request.user)
		context['notif'] = notifications

		return context


class SearchCoachView(ListView):
	model = Coach
	context_object_name = 'available_coaches'
	queryset = Coach.objects.all()
	template_name = 'training_area/athlete/search_coach.html'

class AthleteDetailView(DetailView):
	model = Athlete
	template_name = 'training_area/athlete/athlete_detail.html'
	slug_field = 'user__username'
	#program here
class ProgramDetailView(DetailView):
	model = Macrocycle
	template_name = 'training_area/athlete/program_view.html'

@login_required
@athlete_required
def add_coach(request, coach_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	athlete = Athlete.objects.get(user=request.user)
	athlete.coach = coach
	athlete.save()
	messages.success(request, "Coach Added!")
	return HttpResponseRedirect(reverse('athlete:dashboard'))

@login_required
@athlete_required
def remove_coach(request, coach_id):
	coach = get_object_or_404(Coach, pk = coach_id)
	athlete = Athlete.objects.get(user=request.user)
	athlete.coach = None
	athlete.workout_athlete.clear()
	athlete.save()
	messages.success(request, "Coach Removed!")
	return HttpResponseRedirect(reverse('athlete:dashboard'))

@login_required
@athlete_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    MovementFormSet = inlineformset_factory(
        Workout,
        Movement,
        form = EditMovementFormAthlete,
        fields=( 'kg', 'kg_done', 'num_reps_done', 'rpe'),
        can_delete=False,
        extra=0
    )
    if request.method == 'POST':

        form = WorkoutForm(request.POST, instance=workout)
        formset=MovementFormSet(request.POST, request.FILES, instance=workout)
        #print(form.errors)
        if formset.is_valid() and form.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Workout Changed!')
            return redirect('app:workout_detail', workout.athlete.pk, workout.pk)
    else:
        #form = WorkoutForm(instance=workout)

        formset=MovementFormSet(instance=workout)

    return render(request, 'training_area/athlete/workout_edit_form.html', {
        'formset': formset
    })

@login_required
@athlete_required
def edit_movement(request, movement_id):
	movement = get_object_or_404(Movement, pk=movement_id)
	if request.POST:
		form = EditMovementFormAthlete(request.POST, instance=movement)
		if form.is_valid():
			form.save()
			messages.success(request, 'Movement Changed!')
			return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
		else:
			for field in form:
				#print(field.errors)
				for error in field.errors:
					if 'equal to 10' in error:
						error += " RPE"
					messages.warning(request, error)

			return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
@login_required
@athlete_required
def gen_backoff(request, movement_id):
	movement = get_object_or_404(Movement, pk=movement_id)
	print(movement)
	workout = movement.workout
	if request.POST:
		exertion = ExertionPerceived.objects.filter(rep_scale=movement.num_reps, exertion_scale=movement.rpe) #gives the object
		if not exertion:
			messages.warning(request, "RPE invalid!")
			return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
		else:
			exertion = exertion[0]
		load_percent = exertion.percent
		if movement.kg_done == None:
			messages.warning(request, "No load done!")
			return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
		daily_rm = movement.kg_done / load_percent
		backoff_movements = Movement.objects.filter(workout=workout, is_backoff=True, movement_name=movement.movement_name) #queryset
		if not backoff_movements:
			messages.warning(request, "No backoffs ticked!")
			return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
		for backoff in backoff_movements: #update all objects
			backoff.kg = round((daily_rm * (backoff.percentage/Decimal(100)))/Decimal(2.5)) * Decimal(2.5)
			backoff.save()
		messages.success(request, "Backoff generated!")
		return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
	else:
		messages.error(request, "Oops, something went wrong!")

@login_required
@athlete_required
def submit_workout(request, workout_id):
	workout = get_object_or_404(Workout, pk=workout_id)
	for movement in workout.work.all():
		if not movement.num_reps_done:
			movement.num_reps_done = movement.num_reps
			movement.save()
		if not movement.kg_done:
			movement.kg_done = movement.kg
			movement.save()
		if not movement.rpe:
			messages.warning(request, "Fill in all your RPEs")
			return redirect('app:workout_detail', workout.athlete.pk, workout.pk)
	if workout.completed == False:
		workout.completed = True
	else:
		workout.completed = False
	workout.save()
	if workout.microcycle:
		uncompleted = workout.microcycle.micro.all().filter(completed=False)
		#print(uncompleted)
		if not uncompleted:
			message = workout.athlete.user.username + " has completed " + workout.microcycle.get_html_url
			notification = Notifications(title=message, sender=workout.athlete.user, reciever=workout.athlete.coach.user)
			notification.save()
	return redirect('app:workout_detail', workout.athlete.pk, workout.pk)

def submit_fatigue(request):
	multiplier = {
		0: 1.12,
		1: 1.1,
		2: 1.07,
		3: 1.05,
		4: 1.02,
		5: 1,
		6: 0.97,
		7: 0.95,
		8: 0.92,
		9: 0.9,
		10: 0.88
	}
	workout_pk = request.POST.get('pk')
	fatigue_rating = request.POST.get('fatigue')

	workout_of_interest = get_object_or_404(Workout, pk=workout_pk)
	old_rating = workout_of_interest.fatigue_rating
	workout_of_interest.fatigue_rating = fatigue_rating
	for movement in workout_of_interest.work.all():
		if movement.kg:
			movement.kg = round(movement.kg / Decimal(multiplier[int(old_rating)]) * Decimal(multiplier[int(fatigue_rating)])/Decimal(2.5))* Decimal(2.5)
		elif movement.percentage:
			movement.percentage = Decimal(movement.percentage) / Decimal(multiplier[int(old_rating)]) * Decimal(multiplier[int(fatigue_rating)])
		movement.save()
	workout_of_interest.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def accessory_load_done(request):
	pk = request.POST.get('pk')
	load_done = request.POST.get('load_done')

	accessory = get_object_or_404(Accessory, pk=pk)
	accessory.load_done = load_done
	accessory.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)

def accessory_protocol_done(request):
	pk = request.POST.get('pk')
	prot_done = request.POST.get('prot_done')

	accessory = get_object_or_404(Accessory, pk=pk)
	accessory.measurement_done = prot_done
	accessory.save()
	data = {
		"lol": "lol"
	}
	return JsonResponse(data)