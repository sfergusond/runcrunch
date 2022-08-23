from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from . import forms
from .models import Athlete, Activity
from .utils.callImporter import callImporter

def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      username=form.cleaned_data['username']
      new_user = authenticate(
        username=username,
        password=form.cleaned_data['password1']
        )
      login(request, new_user)
      Athlete.objects.create(user=request.user)
      return redirect('/connect-to-strava')
  else:
      form = UserCreationForm()
  return render(request, 'register/register.html', {'form': form})

@login_required(redirect_field_name='/login')
def connect_to_strava(request):
  queryString = dict(request.GET.items())
  if 'activity:read' in queryString.get('scope', ''):
    code = queryString.get('code')
    request.athlete.stravaAuthenticate(code)
    return redirect('account')
  
  redirectUrl = (
    'https://www.strava.com/oauth/authorize?' +
    f'client_id={settings.STRAVA_CLIENT_ID}&' +
    f'redirect_uri={settings.DOMAIN}/connect-to-strava&' +
    '&approval_prompt=auto&response_type=code&scope=activity%3Aread%2Cactivity%3Aread_all'
    )
  return render(request, 'home/connectToStrava.html', {'redirectUrl': redirectUrl})

@login_required(redirect_field_name='/login')
def account(request):
  if request.method == 'POST':
    if 'import' in request.POST:
      # Deny import if too many activities present
      activityCount = Activity.objects.filter(
        athlete=request.athlete
      ).count()
      if activityCount < 1000:
        callImporter(request.athlete)
  context = {}
  prForm = forms.PersonalRecord(request.POST)
  unitPreference = forms.UnitPreference(request.POST)
  context.update({
    'prForm': prForm,
    'unitPreference': unitPreference,
    })
  return render(request, 'home/account.html', context)

@login_required(redirect_field_name='/login')
def viewActivity(request, activityId):
  activity = Activity.objects.get(pk=activityId)
  if activity.athlete != request.athlete:
    return HttpResponse(status=403)
  # Make activity details
  activity.getStreams()
  activity.getFriendlyStats()
  activityJson = activity.toJson()
  #print(activity.__dict__)
  # Get activity streams
  return render(
    request,
    'home/viewActivity.html',
    {
      'activity': activity,
      'activityJson': activityJson
    }
  )
  
@login_required(redirect_field_name='/login')
def viewHeatmap(request):
  return render(request, 'home/viewHeatmap.html')
