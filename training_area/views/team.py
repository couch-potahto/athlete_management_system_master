from django.shortcuts import redirect, render
from django.views.generic import TemplateView

class SignUpView(TemplateView):
	template_name = 'registration/signup.html'

def home(request):
	if request.user.is_authenticated:
		if request.user.is_coach:
			return redirect('coach:dashboard')
		else:
			return redirect('athlete:dashboard')
	return render(request, 'home.html')
