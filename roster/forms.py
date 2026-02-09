from crispy_forms.layout import Submit
from django import forms
from crispy_forms.helper import FormHelper
from roster.models import Member, Rank, Status, Duty, Event, VolumeRole, ServiceKiosk, Badge, History


class EventForm(forms.ModelForm):
    def __init__(self, include_submit_button=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if(include_submit_button == True):
            self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Event
        exclude = ['codes', 'feature_mesh', 'feature_mesh_channel', 'feature_mesh_api_key', 'feature_mesh_api_base']

class MemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Member
        fields = ['event','name','rank','volumeRole','vaccineStatus','radioNumber','details']

class VolumeRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = VolumeRole
        fields = '__all__'

class RankForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Rank
        fields = '__all__'

from django_select2 import forms as s2forms
class MemberWidget(s2forms.Select2Widget):
    pass

class HistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.fields['member'].widget = MemberWidget()


        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = History
        fields = '__all__'

class KioskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = ServiceKiosk
        fields = '__all__'

class BadgeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Badge
        fields = '__all__'

class StatusForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Status
        fields = '__all__'

class DutyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['event'].widget = forms.HiddenInput()
        #self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Duty
        fields = '__all__'