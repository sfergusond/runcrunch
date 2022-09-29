from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

from utils.convert import CONVERSIONS

def validateTime(value):
  if value >= 60:
    raise ValidationError(
      message=f'{value} is not less than 60',
      params={'value': value},
    )

def validatePos(value):
  if value < 0:
    raise ValidationError(
      message=f'{value} is not positive',
      params={'value': value},
    )

class RegisterForm(UserCreationForm):
  email = forms.EmailField(
    required=True
  )

class DatePicker(forms.DateInput):
  input_type='date'

class DateForm(forms.Form):
  fromDate = forms.DateField(
    required=True,
    label="From",
    widget=DatePicker(
      attrs={
        'class': "form-control",
        'type': "date"
      }
    )
  )
  toDate = forms.DateField(
    required=True,
    label="To",
    widget=DatePicker(
      attrs={
        'class': "form-control",
        'type': "date"
      }
    )
  )

class PersonalRecord(forms.Form):
  h = forms.IntegerField(
    widget=forms.NumberInput(
      attrs={
        'class': 'form-control',
        'type': 'number',
        'placeholder': 'hours'
      }
    ),
    label='',
    validators=[validatePos],
    initial=0
  )
  m = forms.IntegerField(
    widget=forms.NumberInput(
      attrs={
        'class': 'form-control',
        'type': 'number',
        'placeholder': 'minutes'
      }
    ),
    label='',
    validators=[validateTime, validatePos],
    initial=0
  )
  s = forms.IntegerField(
    widget=forms.NumberInput(
      attrs={
        'class': 'form-control',
        'type': 'number',
        'placeholder': 'seconds'
      }
    ),
    label='',
    validators=[validateTime, validatePos],
    initial=0
  )
  distance = forms.IntegerField(
    widget=forms.NumberInput(
      attrs={
        'class': 'form-control',
        'type': 'number',
        'value': '0'
        }
      ),
      label='',
      validators=[validatePos],
      initial=0
    )
  unit = forms.ChoiceField(
    widget=forms.Select(
      attrs={
        'class': 'form-control',
        'value': 'meters'
      }
    ),
    label='',
    choices=[
      ('m', 'meters'),
      ('km', 'kilometers'),
      ('mi', 'miles')
    ]
  )
  
  def save(self, athlete):
    data = self.cleaned_data
    distance = data['distance']
    if data['unit'] == 'km':
      distance = CONVERSIONS['kmToMeters'](distance)
    elif data['unit'] == 'mi':
      distance = CONVERSIONS['milesToMeters'](distance)
    hoursToSeconds = data['h']  * 60 * 60
    minsToSeconds = data['m'] * 60
    time = hoursToSeconds + minsToSeconds + data['s']
    athlete.prDistance = distance
    athlete.prTime = time
    athlete.save()

class UnitPreference(forms.Form):
  metric = forms.ChoiceField(
    choices=[
      ('M', 'metric (km, m)'),
      ('I', 'imperial (mi, ft)')
    ],
    required=True,
    widget=forms.RadioSelect(),
    label=''
  )
  
  def save(self, athlete):
    athlete.unitPreference = self.cleaned_data['metric']
    athlete.save()
