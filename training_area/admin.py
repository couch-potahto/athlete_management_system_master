from django.contrib import admin
from .models import Athlete, Coach, Team, Macrocycle, Mesocycle, Microcycle, Workout, Movement, ExertionPerceived, RepMax, User

# Register your models here.
admin.site.register(User)
admin.site.register(Athlete)
admin.site.register(Coach)
admin.site.register(Team)
admin.site.register(Macrocycle)
admin.site.register(Mesocycle)
admin.site.register(Microcycle)
admin.site.register(Workout)
admin.site.register(Movement)
admin.site.register(ExertionPerceived)
admin.site.register(RepMax)
