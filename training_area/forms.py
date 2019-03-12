from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, inlineformset_factory, ModelMultipleChoiceField, ModelChoiceField
from django.db import transaction
from django.utils.translation import gettext_lazy as _


from training_area.models import Coach, Athlete, Team, User, Movement, Workout, Microcycle, RepMax

class AthleteSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name']

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
        fields = ['username', 'first_name', 'last_name']

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

class AddWoToMicroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        athlete_id = kwargs.pop('athlete_id', None)
        print(athlete_id)
        super(AddWoToMicroForm, self).__init__(*args, **kwargs)
        self.fields["workouts"]=forms.ModelMultipleChoiceField(
            queryset=Workout.objects.filter(athlete__user__id = athlete_id),
            widget=forms.CheckboxSelectMultiple()
            )

class AddMicroToMacroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        athlete_id = kwargs.pop('athlete_id', None)
        print(athlete_id)
        super(AddMicroToMacroForm, self).__init__(*args, **kwargs)
        self.fields["microcycles"]=forms.ModelMultipleChoiceField(
            queryset=Microcycle.objects.filter(athlete__user__id = athlete_id),
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

class AddMovementFormCoach(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ('movement_name', 'percentage', 'num_reps', 'kg', 'rpe', 'is_backoff', 'rep_max')

    rep_max = forms.ModelChoiceField(queryset = RepMax.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        self.fields['rep_max'].queryset = RepMax.objects.filter(
            athlete__user__id = pk)

'''class ProfileForm(forms.ModelForm):
    class Meta:
        model = Coach

    first_name = forms.CharField(label='Your Bio', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(label='Your Bio', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    bio = forms.CharField(label='Your Bio', widget=forms.TextInput(attrs={'placeholder': 'Bio'}))'''

