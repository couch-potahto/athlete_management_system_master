from django.urls import include, path, re_path
from .views import team, athlete, coach, app

urlpatterns = [
    path('', team.home, name='home'),

    path('app/', include(([
        path('user=<int:pk>/log', app.LogView.as_view(), name='log_view'),
        path('workout=<int:workout_id>/add_comment', app.add_comment, name='add_comment'),
        path('comment=<int:comment_id>/delete_comment', app.delete_comment, name='delete_comment'),
        path('<int:notif_id>/delete_notification', app.delete_notification, name='delete_notif'),
        path('delete_all_notifications', app.delete_all_notifications, name='delete_all_notif'),
        path('user=<int:pk>/workout=<int:pk_2>', app.WorkoutDetail.as_view(), name='workout_detail'),
        path('user=<int:pk>/micro=<int:pk_2>', app.MicrocycleDetail.as_view(), name='micro_detail'),
        path('<str:slug>/profile', app.ProfileView.as_view(), name='profile_view'),
        path('search_coach', app.SearchCoachView.as_view(), name='search_coach'),
        path('<int:pk>/search_athlete', app.SearchAthleteView.as_view(), name='search_athlete'),
        path('<int:pk>/search_workout', app.SearchWorkoutView.as_view(), name='search_workout'),
        path('calendar', app.CalendarView.as_view(), name='calendar'),
        path('calendar/new_event', app.event, name='event_new'),
        path('calendar/event=<int:event_id>', app.event, name='event_edit'),
        path('user=<int:pk>/chart_type=<str:chart_type>', app.RPEView.as_view(), name='view_rpe'),
        #######
        path('analytics', app.ChartView.as_view(), name='analytics'),
        path('api/chartdata', app.ChartData.as_view(), name ='testdata'),
        path('testviews/api/chartdata', app.ChartData.as_view(), name ='testdata'),
        path('api/data', app.get_data, name='api-data'),
        path('ajax/load-lifts/', app.load_lifts, name = 'ajax_load_lifts'),
        path('ajax/display-metrics/', app.display_metrics, name = 'ajax_display_metrics'),
        path('ajax/load-meso/', app.load_meso, name = 'ajax_load_meso'),
        path('ajax/testpost/', app.testpost, name = 'ajax_test_post'),

    ], 'training_area'), namespace='app')),

    path('athlete/', include(([
        path('edit/<int:workout_id>', athlete.edit_workout, name = 'edit_workout'),
    	path('search_coach/', athlete.SearchCoachView.as_view(), name='search_coach'),
        path('dashboard/', athlete.DashboardView.as_view(), name='dashboard'),
        #path('<str:slug>/', athlete.AthleteDetailView.as_view(), name = 'athlete_detail'),
        path('add_coach/<int:coach_id>/', athlete.add_coach, name = 'add_coach'),
        path('remove_coach/<int:coach_id>/', athlete.remove_coach, name = 'remove_coach'),
        path('program_view/<int:pk>/', athlete.ProgramDetailView.as_view(), name = 'program_view'),
        path('<int:movement_id>/edit', athlete.edit_movement, name = 'edit_movement'),
        path('<int:movement_id>/gen_backoff', athlete.gen_backoff, name = 'generate_backoff'),
        path('submit/<int:workout_id>', athlete.submit_workout, name = 'submit'),

    ], 'training_area'), namespace='athlete')),

    path('coach/', include(([
        path('delete_workout/<int:athlete_id>/<int:workout_id>', coach.WorkoutDeleteView.as_view(), name = 'delete_workout'),
        path('delete_micro/<int:athlete_id>/<int:microcycle_id>', coach.MicrocycleDeleteView.as_view(), name = 'delete_micro'),
        path('delete_meso/<int:athlete_id>/<int:mesocycle_id>', coach.MesocycleDeleteView.as_view(), name = 'delete_meso'),
        path('dashboard/', coach.DashboardView.as_view(), name='dashboard'),
        path('<str:slug>/', coach.CoachDetailView.as_view(), name = 'coach_detail'),
        path('athlete=<int:pk>/add_workout', coach.AddWorkoutView.as_view(), name = 'add_workout'),
        path('<int:microcycle_id>/edit_micro_name', coach.edit_micro_name, name = 'edit_micro_name'),
        path('duplicate/<int:movement_id>', coach.duplicate, name = 'duplicate'),
        path('duplicate_micro/<int:microcycle_id>', coach.duplicate_microcycle, name = 'duplicate_micro'),
        path('delete/<int:movement_id>', coach.delete_movement, name = 'delete'),
        path('editrm/<int:rep_max_id>', coach.edit_rep_max, name = 'edit_rep_max'),
        path('deleterm/<int:rep_max_id>', coach.delete_rep_max, name = 'delete_rep_max'),
        path('edit/<int:workout_id>', coach.edit_workout, name = 'edit_workout'),
        path('edit_profile/<int:pk>', coach.UpdateCoach.as_view(), name = 'edit_profile'),
        path('athlete=<int:pk>/create_micro', coach.CreateMicrocycleView.as_view(), name = 'create_micro'),
        path('athlete=<int:pk>/create_meso', coach.CreateMesocycleView.as_view(), name = 'create_meso'),
        path('athlete=<int:athlete_id>/micro=<int:pk_2>/add', coach.add_wo_to_micro, name = 'add_wo_to_micro'),
        path('athlete=<int:athlete_id>/meso=<int:pk_2>/add', coach.add_micro_to_meso, name = 'add_micro_to_meso'),
        path('<int:movement_id>/quick_edit', coach.edit_movement_quick, name = 'edit_movement_quick'),
        path('<int:athlete_id>/add_rep_max', coach.add_rep_max, name = 'add_rep_max'),
        path('athlete=<int:pk>/workout=<int:pk_2>/add_movement_test', coach.AddMovementViewTest.as_view(), name = 'add_movement_test'),
    ], 'training_area'), namespace='coach')),
    #re_path(r'^coach/(?P<user>[\w-]+)/$', coach.CoachDetailView.as_view(), name = 'coach_detail'),
]
