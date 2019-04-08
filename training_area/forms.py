from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, inlineformset_factory, ModelMultipleChoiceField, ModelChoiceField, DateInput
from django.db import transaction
from django.utils.translation import gettext_lazy as _


from training_area.models import Coach, Athlete, Team, User, Movement, Workout, Microcycle, RepMax, Event, Comment

class AthleteSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_athlete = True
        user.save()
        athlete = Athlete.objects.create(user=user)
        athlete.first_name = self.cleaned_data.get('first_name')
        athlete.last_name = self.cleaned_data.get('last_name')
        athlete.save()
        #student.interests.add(*self.cleaned_data.get('interests'))
        return user

class CoachSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_coach = True
        user.save()
        coach = Coach.objects.create(user=user)
        coach.first_name = self.cleaned_data.get('first_name')
        coach.last_name = self.cleaned_data.get('last_name')
        coach.save()
        #student.interests.add(*self.cleaned_data.get('interests'))
        return user

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ('workout_name',)
        labels = {
        "workout_name": _("Workout Name"),
    }

class MicroForm(forms.ModelForm):
    class Meta:
        model = Microcycle
        fields = ('microcycle_name',)
        labels = {
        "microcycle_name": _("Microcycle Name"),
    }

class AddWoToMicroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        athlete_id = kwargs.pop('athlete_id', None)
        print(athlete_id)
        super(AddWoToMicroForm, self).__init__(*args, **kwargs)
        self.fields["workouts"]=forms.ModelMultipleChoiceField(
            queryset=Workout.objects.filter(athlete__user__id = athlete_id, microcycle=None).order_by('created_at'),
            widget=forms.CheckboxSelectMultiple()
            )

class AddMicroToMesoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        athlete_id = kwargs.pop('athlete_id', None)
        print(athlete_id)
        super(AddMicroToMesoForm, self).__init__(*args, **kwargs)
        self.fields["microcycles"]=forms.ModelMultipleChoiceField(
            queryset=Microcycle.objects.filter(athlete__user__id = athlete_id).order_by('id'),
            widget=forms.CheckboxSelectMultiple()
            )


class EditMovementFormAthlete(forms.ModelForm):
    kg = forms.DecimalField(disabled=True, required=False)
    class Meta:
        model = Movement
        fields = ('kg', 'kg_done', 'num_reps_done', 'rpe')

class EditMovementFormCoach(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ('movement_name', 'percentage', 'kg', 'num_reps', 'rpe', 'is_backoff')

class AddRepMaxForm(forms.ModelForm):
    class Meta:
        model = RepMax
        fields = ('rep_max_name', 'rep_max')

class EditRepMaxForm(forms.ModelForm):
    class Meta:
        model = RepMax
        fields = ('rep_max_name', 'rep_max')

class AddMovementFormCoach(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ('movement_name', 'description', 'percentage', 'num_reps', 'kg', 'rpe', 'is_backoff', 'rep_max')

    rep_max = forms.ModelChoiceField(queryset = RepMax.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        self.fields['rep_max'].queryset = RepMax.objects.filter(
            athlete__user__id = pk)

class EventForm(ModelForm):
  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = ('title', 'description', 'start_time', 'end_time')

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

