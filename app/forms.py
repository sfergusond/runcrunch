from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

metricChoices = [
  ('dist', 'Distance'),
  ('time', 'Time'),
  ('elev', 'Elevation'),
  ('pace', 'Pace'),
  ('avg_hr', 'Avg HR'),
  ('intensity', 'Intensity')
  ]

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

class DatePicker(forms.DateInput):
  input_type='date'

class DateForm(forms.Form):
  dateStart = forms.DateField(
    required=True,
    label="From",
    widget=DatePicker(
      attrs={
        'class': "form-control",
        'type': "date"
      }
    )
  )
  dateEnd = forms.DateField(
    required=True,
    label="To",
    widget=DatePicker(
      attrs={
        'class': "form-control",
        'type': "date"
      }
    )
  )

class HorizRadioRenderer(forms.RadioSelect):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class MetricPicker(forms.Form):
  metric = forms.ChoiceField(
    choices=metricChoices,
    required=False,
    widget=forms.RadioSelect(
      attrs={
        'style': 'margin-left: 20px;'
      }
    ),
    label='',
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
    validators=[validatePos]
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
    validators=[validateTime, validatePos]
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
    validators=[validateTime, validatePos]
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
      validators=[validatePos]
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

class UnitPreference(forms.Form):
  metric = forms.ChoiceField(
    choices=[
      ('metric', 'metric (km, m)'),
      ('imperial', 'imperial (mi, ft)')
    ],
    required=False,
    widget=forms.RadioSelect(),
    label=''
  )
  