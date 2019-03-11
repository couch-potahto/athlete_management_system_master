from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.views.generic.edit import DeleteView
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import formset_factory, inlineformset_factory
from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from ..decorators import coach_required
from ..forms import CoachSignUpForm, AddWoToMicroForm, WorkoutForm, EditMovementFormCoach, AddRepMaxForm, AddMovementFormCoach
from ..models import User, Coach, Athlete, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, RepMax


class CoachSignUpView(CreateView):
    model = User
    form_class = CoachSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Coach'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')


@method_decorator([login_required, coach_required], name='dispatch')
class DashboardView(ListView):
    model = Athlete
    context_object_name = 'available_athletes'
    template_name = 'training_area/coach/dashboard.html'

    def get_queryset(self):
        return Athlete.objects.filter(coach__user=self.request.user)

@method_decorator([login_required, coach_required], name='dispatch')
class AddWorkoutView(CreateView):
    model = Workout
    fields = ('workout_name', )
    labels = {
        "workout_name": _("Workout Stuff"),
    }
    context_object_name = 'Workout'
    template_name = 'training_area/coach/create_wo_form.html'

    def get_context_data(self, **kwargs):
        context = super(AddWorkoutView,self).get_context_data(**kwargs)
        context['pk']=self.kwargs['pk']
        return context

    def form_valid(self, form):
        workout = form.save()
        workout.coach = self.request.user.coach
        workout.athlete = Athlete.objects.filter(user__id=self.get_context_data()['pk'])[0]
        workout.save()
        messages.success(self.request, 'The Workout Was Created!')
        return redirect('coach:add_movement_test', workout.athlete.pk, workout.pk)

'''@method_decorator([login_required, coach_required], name='dispatch')
class AddMovementView(CreateView):
    model = Movement
    fields = ('movement_name', 'percentage', 'num_reps', 'kg', 'rpe', 'is_backoff')
    context_object_name = 'Movement'
    template_name = 'training_area/coach/create_movement_form.html'

    def get_context_data(self, **kwargs):
        context = super(AddMovementView,self).get_context_data(**kwargs)
        context['pk_2']=self.kwargs['pk_2']
        context['pk']=self.kwargs['pk']
        context['athlete']=RepMax.objects.filter(athlete__user__id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        print(form)
        movement = form.save()
        movement.workout = Workout.objects.filter(id=self.get_context_data()['pk_2'])[0]
        movement.save()
        messages.success(self.request, 'The movement Was Created!')
        return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)'''



@method_decorator([login_required, coach_required], name='dispatch')
class AddMovementViewTest(CreateView):
    model = Movement
    form_class = AddMovementFormCoach
    template_name = 'training_area/coach/create_movement_form_test.html'

    def get_context_data(self, **kwargs):
        context = super(AddMovementViewTest,self).get_context_data(**kwargs)
        context['pk_2']=self.kwargs['pk_2']
        context['pk']=self.kwargs['pk']
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        if form.errors:
            for field in form:
                print(field.errors)
                for error in field.errors:
                    messages.warning(self.request, error)

            return render(self.request, template, {"form" : form, "movement" : movement})

        movement=Movement.objects.create(
                movement_name=form.cleaned_data['movement_name'],
                num_reps=form.cleaned_data['num_reps'],
                percentage=form.cleaned_data['percentage'],
                is_backoff=form.cleaned_data['is_backoff'],
                rpe=form.cleaned_data['rpe']
                )
        if form.cleaned_data['rep_max']: #using a rep_max

            if not form.cleaned_data['percentage']:
                messages.warning(self.request, 'Please Put a %')
                form = AddWMovementFormCoach()
                return render(self.request, template, {"form" : form, "movement" : movement})
            rm = form.cleaned_data['rep_max'].rep_max
            movement.kg = round((rm * (form.cleaned_data['percentage']/Decimal(100)))/Decimal(2.5)) * Decimal(2.5)

        movement.workout = Workout.objects.filter(id=self.get_context_data()['pk_2'])[0]
        movement.save()
        return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)


@method_decorator([login_required, coach_required], name='dispatch')
class CoachDetailView(DetailView):
    model = Coach
    template_name = 'training_area/coach/coach_detail.html'
    slug_field = "user__username"

'''@method_decorator([login_required, coach_required], name='dispatch')
class CreateProgramView(CreateView):
    model = Macrocycle
    fields = ('macrocycle_name', 'descripton', )
    context_object_name = 'Macrocycle'
    template_name = 'training_area/coach/create_program_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProgramView,self).get_context_data(**kwargs)
        context['pk']=self.kwargs['pk']
        return context

    def form_valid(self, form):
        program = form.save()
        program.coach = self.request.user.coach
        program.athlete = Athlete.objects.filter(user__id=self.get_context_data()['pk'])[0]
        program.save()
        messages.success(self.request, 'The Program Was Created!')
        return redirect('coach:program_view', program.athlete.pk, program.pk)'''

'''@method_decorator([login_required, coach_required], name='dispatch')
class ProgramDetailView(DetailView):
    model = Macrocycle
    template_name = 'training_area/coach/program_view.html'
    pk_url_kwarg = 'pk_2'

@method_decorator([login_required, coach_required], name='dispatch')
class MesoDetailView(DetailView):
    model = Mesocycle
    template_name = 'training_area/coach/meso_view.html'
    pk_url_kwarg = 'pk_3'

@method_decorator([login_required, coach_required], name='dispatch')
class CreateMesoView(CreateView):
    model = Mesocycle
    fields = ('mesocycle_name', )
    template_name = 'training_area/coach/create_meso_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateMesoView,self).get_context_data(**kwargs)
        context['pk_2']=self.kwargs['pk_2']
        return context

    def form_valid(self, form):
        meso = form.save()
        meso.macrocycle = Macrocycle.objects.filter(id=self.get_context_data()['pk_2'])[0]
        meso.save()
        messages.success(self.request, 'Mesocycle Created!')
        return redirect('coach:meso_view', meso.macrocycle.athlete.pk, meso.macrocycle.pk, meso.pk)

@method_decorator([login_required, coach_required], name='dispatch')
class CreateMicroView(CreateView):
    model = Microcycle
    fields = ('microcycle_name', )
    template_name = 'training_area/coach/create_micro_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateMicroView,self).get_context_data(**kwargs)
        context['pk_3']=self.kwargs['pk_3']
        return context

    def form_valid(self, form):
        micro = form.save()
        micro.mesocycle = Mesocycle.objects.filter(id=self.get_context_data()['pk_3'])[0]
        micro.save()
        messages.success(self.request, 'Microcycle Created!')
        return redirect('coach:micro_view', micro.mesocycle.macrocycle.athlete.pk, micro.mesocycle.macrocycle.pk,
                micro.mesocycle.pk, micro.pk)

@method_decorator([login_required, coach_required], name='dispatch')
class MicroDetailView(DetailView):
    model = Microcycle
    template_name = 'training_area/coach/micro_view.html'
    pk_url_kwarg = 'pk_4'''

'''@method_decorator([login_required, coach_required], name='dispatch')
class CreateWoView(CreateView):
    model = Workout
    fields = ('workout_name', )
    template_name = 'training_area/coach/create_wo_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateWoView,self).get_context_data(**kwargs)
        context['pk_4']=self.kwargs['pk_4']
        return context

    def form_valid(self, form):
        workout = form.save()
        workout.microcycle = Microcycle.objects.filter(id=self.get_context_data()['pk_4'])[0]
        workout.save()
        messages.success(self.request, 'workout Created!')
        return redirect('coach:create_mo', workout.microcycle.mesocycle.macrocycle.athlete.pk, workout.microcycle.mesocycle.macrocycle.pk,
                workout.microcycle.mesocycle.pk, workout.microcycle.pk, workout.pk)'''

'''@method_decorator([login_required, coach_required], name='dispatch')
class WoDetailView(DetailView):
    model = Workout
    context_object_name = 'all_movements'
    template_name = 'training_area/coach/wo_view.html'
    pk_url_kwarg = 'pk_5'

    def get_queryset(self):
        return Movement.objects.filter(workout_id=self.kwargs.get(self.pk_url_kwarg))'''

@method_decorator([login_required, coach_required], name='dispatch') #contact form
class CreateMovementView(CreateView):
    model = Movement
    fields = ('movement_name', 'kg', 'num_reps', 'rpe', 'is_backoff' )
    template_name = 'training_area/coach/create_movement_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateMovementView,self).get_context_data(**kwargs)
        context['pk_5']=self.kwargs['pk_5']
        return context

    def form_valid(self, form):
        movement = form.save()
        movement.workout = Workout.objects.filter(id=self.get_context_data()['pk_5'])[0]
        movement.save()
        messages.success(self.request, 'Movement Created!')
        return redirect('coach:wo_view', movement.workout.microcycle.mesocycle.macrocycle.athlete.pk, movement.workout.microcycle.mesocycle.macrocycle.pk,
                movement.workout.microcycle.mesocycle.pk, movement.workout.microcycle.pk, movement.workout.pk)

@login_required
@coach_required
def duplicate(request, movement_id):
    copy_movement = get_object_or_404(Movement, pk=movement_id)
    copy_movement.pk = None
    copy_movement.save()
    messages.success(request, "Duplicated!")
    return redirect('app:workout_detail', copy_movement.workout.athlete.pk, copy_movement.workout.pk)

@login_required
@coach_required
def delete_movement(request, movement_id):
    movement = get_object_or_404(Movement, pk=movement_id)
    athlete_key = movement.workout.athlete.pk
    ownkey = movement.workout.pk
    movement.delete()
    messages.success(request, "Deleted!")
    return redirect('app:workout_detail', athlete_key, ownkey)


@method_decorator([login_required, coach_required], name='dispatch')
class WorkoutDeleteView(DeleteView):
    model = Workout
    context_object_name = 'workout'
    template_name = 'training_area/coach/workout_confirm_delete.html'
    pk_url_kwarg = 'workout_id'
    #success_url = reverse_lazy('coach:dashboard')

    def delete(self, request, *args, **kwargs):
        workout = self.get_object()
        messages.success(request, 'The workout %s was deleted with success!' % workout.workout_name)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        athlete= self.kwargs.get('athlete_id')
        # I don't see why you would need a lazy inside a method...
        return reverse('app:log_view',
                       kwargs = {'pk': athlete})

@method_decorator([login_required, coach_required], name='dispatch')
class MicrocycleDeleteView(DeleteView):
    model = Microcycle
    context_object_name = 'microcycle'
    template_name = 'training_area/coach/microcycle_confirm_delete.html'
    pk_url_kwarg = 'microcycle_id'
    #success_url = reverse_lazy('coach:dashboard')

    def delete(self, request, *args, **kwargs):
        microcycle = self.get_object()
        messages.success(request, 'The microcycle %s was deleted with success!' % microcycle.microcycle_name)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        athlete= self.kwargs.get('athlete_id')
        return reverse('app:log_view',
                       kwargs = {'pk': athlete})

@method_decorator([login_required, coach_required], name='dispatch')
class CreateMicrocycleView(CreateView):
    model=Microcycle
    fields = ('microcycle_name', )
    template_name = 'training_area/coach/create_micro_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateMicrocycleView,self).get_context_data(**kwargs)
        context['pk']=self.kwargs['pk']
        return context

    def form_valid(self, form):
        microcycle = form.save()
        microcycle.athlete = Athlete.objects.filter(user__id=self.get_context_data()['pk'])[0]
        microcycle.coach = microcycle.athlete.coach
        microcycle.save()
        messages.success(self.request, 'Micro Created!')
        return redirect('coach:add_wo_to_micro', microcycle.athlete.pk, microcycle.pk)

@login_required
@coach_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    MovementFormSet = inlineformset_factory(
        Workout,
        Movement,
        fields=('movement_name', 'percentage', 'kg', 'num_reps', 'rpe'),
        can_delete=False,
        extra=0
    )
    if request.method == 'POST':

        form = WorkoutForm(request.POST, instance=workout)
        formset=MovementFormSet(request.POST, request.FILES, instance=workout)
        if formset.is_valid():
            print('<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            #form.save()
            formset.save()
            messages.success(request, 'Workout changed!')
            return redirect('app:workout_detail', workout.athlete.pk, workout.pk)
        else:
            print(formset.errors)

    else:

        form = WorkoutForm(instance=workout)
        formset=MovementFormSet(instance=workout)

    return render(request, 'training_area/coach/workout_edit_form.html', {
        'formset': formset,
        'form': form,
        'workout': workout
    })

@method_decorator([login_required, coach_required], name='dispatch')
class UpdateCoach(UpdateView):
    model = Coach
    fields = ['first_name', 'last_name', 'bio',] # Keep listing whatever fields
    # the combined UserProfile and User exposes.
    template_name = 'training_area/coach/change_profile.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('coach:dashboard')
'''@login_required
@coach_required
def change_profile(request):
    form = ProfileForm()'''


@login_required
@coach_required
def add_wo_to_micro(request, athlete_id, pk_2):
    print(athlete_id)
    template = 'training_area/coach/add_wo_to_micro.html'
    microcycle = Microcycle.objects.get(pk=pk_2)
    if request.method == "POST":

        form = AddWoToMicroForm(request.POST, athlete_id=athlete_id)


        workouts = []
        print(request.POST.getlist("workouts"))
        for pk in request.POST.getlist("workouts"):
            workout = get_object_or_404(Workout, pk=pk)
            print(workout.athlete)
            workout.microcycle = microcycle
            workout.save()
            microcycle.save()
        return redirect('app:log_view', athlete_id)
    else:
        form = AddWoToMicroForm(athlete_id=athlete_id)
        return render(request, template, {"form" : form, "microcycle" : microcycle})

@login_required
@coach_required
def edit_movement_quick(request, movement_id):
    movement = get_object_or_404(Movement, pk=movement_id)
    if request.POST:
        print('<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>')
        form = EditMovementFormCoach(request.POST, instance=movement)
        print(request.POST['rm'])
        if form.is_valid():
            form.save()

            if request.POST['rm'] != 'None':
                rm = request.POST['rm']

                if movement.percentage:
                    movement.kg = round((Decimal(rm) * (Decimal(movement.percentage)/Decimal(100)))/Decimal(2.5)) * Decimal(2.5)
                    movement.save()
                else:
                    messages.warning(request, 'No Percentage Given')

            messages.success(request, 'Movement Saved!')
            return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)
        else:
            for field in form:
                print(field.errors)
                for error in field.errors:
                    if 'equal to 10' in error:
                        error += " RPE"
                    messages.warning(request, error)

            return redirect('app:workout_detail', movement.workout.athlete.pk, movement.workout.pk)

@login_required
@coach_required
def add_rep_max(request, athlete_id):
    template = 'training_area/coach/add_rep_max.html'
    athlete = get_object_or_404(Athlete, pk=athlete_id)
    if request.method == 'POST':
        form = AddRepMaxForm(request.POST)
        if form.is_valid():
            rep_max = form.save()
            rep_max.athlete=athlete
            rep_max.save()
            messages.success(request, rep_max.rep_max_name + ' Was Created!')
            return redirect('app:profile_view', athlete.user)
    else:
        form = AddRepMaxForm()
        return render(request, template, {"form" : form, "athlete" : athlete})
