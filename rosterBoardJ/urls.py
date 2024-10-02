"""
URL configuration for rosterBoardJ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path, include, reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.routers import DefaultRouter

from roster.forms import MemberForm, RankForm, StatusForm, DutyForm, EventForm, VolumeRoleForm, KioskForm, BadgeForm, \
    HistoryForm
from roster.models import Event, Duty, Status, Member, Rank, VolumeRole, AccessRight, ServiceKiosk, Badge, History
from roster.serializers import DutySerializer, StatusSerializer, MemberSerializer, VolumeRoleSerializer, RankSerializer, \
    EventSerializer, KioskSerializer, BadgeSerializer, HistorySerializer
from django.utils.translation import gettext_lazy as _

def renderBoard(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'index.html', {"event": event_obj})

def renderKiosk(request, event, kiosk_pk):
    event_obj = get_object_or_404(Event, key=event)
    kiosk_obj = get_object_or_404(ServiceKiosk, uuid=kiosk_pk)
    return render(request, 'kiosk/index.html', context = {"event": event_obj, "kiosk": kiosk_obj})

def lookupBadgeNumberKiosk(request, event, kiosk_pk, badge_number):
    event_obj = get_object_or_404(Event, key=event)
    kiosk_obj = get_object_or_404(ServiceKiosk, uuid=kiosk_pk)
    badge_obj = get_object_or_404(Badge, tag=badge_number, event=event_obj)
    return JsonResponse({
        "member": MemberSerializer(instance=badge_obj.member).data,
        "rank": RankSerializer(instance=badge_obj.member.rank).data,
        "status": StatusSerializer(instance=badge_obj.member.status).data,
        "duty": DutySerializer(instance=badge_obj.member.duty).data,
        "kiosk": KioskSerializer(instance=kiosk_obj).data,
    }, safe=False)

def renderKioskData(request, event, kiosk_pk):
    event_obj = get_object_or_404(Event, key=event)
    kiosk_obj = get_object_or_404(ServiceKiosk, uuid=kiosk_pk)

    return JsonResponse({"kiosk": KioskSerializer(instance=kiosk_obj).data})

def renderKioskTemplate(request, event, kiosk_pk, template_name):
    event_obj = get_object_or_404(Event, key=event)
    kiosk_obj = get_object_or_404(ServiceKiosk, uuid=kiosk_pk)

    return render(request, 'kiosk/interface/'+template_name+'.html', context={"kiosk": kiosk_obj})


def addMember(request, event):
    event_obj = get_object_or_404(Event, key=event)
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            px = form.save()
            return JsonResponse({"done": True})
    else:
        form = MemberForm(initial={'event': event_obj})
        form.fields['rank'].queryset = Rank.objects.filter(event=event_obj)
        #form.fields['duty'].queryset = Duty.objects.filter(event=event_obj)
        #form.fields['status'].queryset = Status.objects.filter(event=event_obj)
        form.fields['volumeRole'].queryset = VolumeRole.objects.filter(event=event_obj)
        return render(request, 'form_crispy.html', context={"form": form})


def memberList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/member_list.html', context={"event": event_obj, "members": Member.objects.filter(event=event_obj)})

def getVolumeRoles(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return JsonResponse(VolumeRoleSerializer(instance=VolumeRole.objects.filter(event=event_obj), many=True).data, safe=False)

def getMembers(request, event):
    event_obj = get_object_or_404(Event, key=event)

    members = Member.objects.filter(event=event_obj)
    for x in members:
        if x.rank == None:
            x.rank = Rank.objects.filter(event=event_obj, default=True).first()
            x.save(bypass_webook_fire=True)
        if x.status == None:
            x.status = Status.objects.filter(event=event_obj, default=True).first()
            x.save(bypass_webook_fire=True)
        if x.duty == None:
            x.duty = Duty.objects.filter(event=event_obj, default=True).first()
            x.save(bypass_webook_fire=True)

    return JsonResponse(MemberSerializer(instance=members, many=True).data, safe=False)

def getStatuses(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return JsonResponse(StatusSerializer(instance=Status.objects.filter(event=event_obj), many=True).data, safe=False)

def getTasks(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return JsonResponse(DutySerializer(instance=Duty.objects.filter(event=event_obj), many=True).data, safe=False)

def getMainColumns(request, event):
    event_obj = get_object_or_404(Event, key=event)
    column_defs = Status.STATUSTYPES
    columns = []
    for x,y in column_defs:
        columns.append([{"name": x.name, "id": x.pk, "key": x.key} for x in Status.objects.filter(event=event_obj, key=x, hideFromColumns=False).order_by('sortOrder')])
    return JsonResponse(columns, safe=False)

def getAuxColumns(request, event):
    event_obj = get_object_or_404(Event, key=event)
    column_defs = Status.STATUSTYPES
    columns = []
    for x, y in column_defs:
        columns.append([{"name": x.name, "id": x.pk, "key": x.key} for x in
                        Status.objects.filter(event=event_obj, key=x, hideFromColumns=True).order_by('sortOrder')])
    return JsonResponse(columns, safe=False)

def updateMembersStatus(request, event, member_id, status_id):
    event_obj = get_object_or_404(Event, key=event)
    member_obj = get_object_or_404(Member, pk=member_id)
    status = get_object_or_404(Status, pk=status_id)
    member_obj.status = status
    member_obj.save(bypass_webook_fire=True)
    return JsonResponse(MemberSerializer(instance=member_obj).data, safe=False)

def updateMembersDuty(request, event, member_id, duty_id):
    event_obj = get_object_or_404(Event, key=event)
    member_obj = get_object_or_404(Member, pk=member_id)
    duty = get_object_or_404(Duty, pk=duty_id)
    member_obj.duty = duty
    member_obj.save(bypass_webook_fire=True)
    return JsonResponse(MemberSerializer(instance=member_obj).data, safe=False)

def eventManagementPane(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/manage_event.html', context={"event": event_obj})

def rankList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/rank_list.html',
                  context={"event": event_obj, "ranks": Rank.objects.filter(event=event_obj)})


def rankAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = RankForm(initial={'event': event_obj})
    return render(request, 'form_crispy.html', context={"form": form})


def historyList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/history_list.html',
                  context={"event": event_obj, "histories": History.objects.filter(event=event_obj, time_out__isnull=False)})


def historyAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = HistoryForm(initial={'event': event_obj})
    form.fields['status'].queryset = Status.objects.filter(event=event_obj)
    form.fields['duty'].queryset = Duty.objects.filter(event=event_obj)
    form.fields['member'].queryset = Member.objects.filter(event=event_obj)
    form.fields['time_in'].widget = forms.TextInput(attrs={'type': 'datetime-local'})
    form.fields['time_out'].widget = forms.TextInput(attrs={'type': 'datetime-local'})
    return render(request, 'form_crispy.html', context={"form": form})



def statusList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/status_list.html',
                  context={"event": event_obj, "ranks": Status.objects.filter(event=event_obj)})


def statusAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = StatusForm(initial={'event': event_obj})
    return render(request, 'form_crispy.html', context={"form": form})


def getTimesheets(request, event):
    event_obj = get_object_or_404(Event, key=event)

    data = [{"member": x, "history": x.getHistory()} for x in Member.objects.filter(event=event_obj)]

    return render(request, 'modals/timesheet_modals.html',
                  context={"event": event_obj, "package": data})

def dutiesList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/duty_list.html',
                  context={"event": event_obj, "duties": Duty.objects.filter(event=event_obj)})


def dutiesAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = DutyForm(initial={'event': event_obj})
    return render(request, 'form_crispy.html', context={"form": form})

def badgesList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/badge_list.html',
                  context={"event": event_obj, "badges": Badge.objects.filter(event=event_obj)})


def badgesAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = BadgeForm(initial={'event': event_obj})
    form.fields['member'].queryset = Member.objects.filter(event=event_obj)
    return render(request, 'form_crispy.html', context={"form": form})

def kioskList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/kiosk_list.html',
                  context={"event": event_obj, "kiosks": ServiceKiosk.objects.filter(event=event_obj)})


def kioskAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = KioskForm(initial={'event': event_obj})
    form.fields['uuid'].widget = forms.HiddenInput()
    form.fields['check_in_status'].queryset = Status.objects.filter(event=event_obj)
    form.fields['check_out_status'].queryset = Status.objects.filter(event=event_obj)
    form.fields['check_in_duty'].queryset = Duty.objects.filter(event=event_obj)
    form.fields['check_out_duty'].queryset = Duty.objects.filter(event=event_obj)
    return render(request, 'form_crispy.html', context={"form": form})


def volumeRolesList(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/volumerole_list.html',
                  context={"event": event_obj, "volumeroles": VolumeRole.objects.filter(event=event_obj)})


def volumeRolesAdd(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = VolumeRoleForm(initial={'event': event_obj})
    return render(request, 'form_crispy.html', context={"form": form})

def eventDetailsForm(request, event):
    event_obj = get_object_or_404(Event, key=event)
    form = EventForm(instance=event_obj, include_submit_button=False)
    form.fields['key'].widget = forms.HiddenInput()
    return render(request, 'form_crispy.html', context={"form": form})

@login_required(login_url='/accounts/login/')
def newEvent(request):
    if request.method == 'POST':
        form = EventForm(data=request.POST)
        if form.is_valid():
            px = form.save()
            acc = AccessRight.objects.create(user=request.user,board=px)
            Status.objects.create(event=px,
                                  key="A",
                                  name="Available",
                                  default=True)
            Status.objects.create(event=px,
                                  key="X",
                                  name="Away")
            Status.objects.create(event=px,
                                  key="Z",
                                  name="Off-Site",
                                  hideFromColumns=True)
            Rank.objects.create(event=px,
                                name="Default",
                                key="DF",
                                default=True)
            Duty.objects.create(event=px,
                                name="Default",
                                key="DF",
                                default=True)
            return redirect("index")
    form = EventForm()
    return render(request, 'ui/form.html', context={"form": form})


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def updateMembersDetails(request, event, member_id):
    event_obj = get_object_or_404(Event, key=event)
    member_obj = get_object_or_404(Member, pk=member_id)
    member_obj.details = request.data['details']
    member_obj.save(bypass_webook_fire=True)
    return JsonResponse(MemberSerializer(instance=member_obj).data, safe=False)


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required(login_url='/accounts/login/')
def index(request):
    events = AccessRight.objects.filter(user=request.user)
    return render(request, 'ui/index.html', {"access": events})

def renderEventDetails(request, event):
    event_obj = get_object_or_404(Event, key=event)
    return render(request, 'modals/event_details_markdown_render.html', {"event": event_obj})

def getMember(request, event, id):
    event_obj = get_object_or_404(Event, key=event)
    x = get_object_or_404(Member, pk=id)
    if x.rank == None:
        x.rank = Rank.objects.filter(event=event_obj, default=True).first()
        x.save(bypass_webook_fire=True)
    if x.status == None:
        x.status = Status.objects.filter(event=event_obj, default=True).first()
        x.save(bypass_webook_fire=True)
    if x.duty == None:
        x.duty = Duty.objects.filter(event=event_obj, default=True).first()
        x.save(bypass_webook_fire=True)
    return JsonResponse(MemberSerializer(instance=x).data, safe=False)

def sidebarMembers(request, event):
    event_obj = get_object_or_404(Event, key=event)
    ranks = Rank.objects.filter(event=event_obj, displayOnSidebar=True).order_by('-sortOrder')
    return render(request, 'modals/event_sidepane_usefuls.html', {"ranks": ranks})


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def postAdd(request, event, name):
    dat0 = request.data.copy()
    dat = {}
    for x in dat0.keys():
        dat[x] = dat0[x]
        if dat0[x] == "true":
            dat[x] = True
        if dat0[x] == "false":
            dat[x] = False
    del dat['csrfmiddlewaretoken']
    model = None
    if name == 'member':
        model = MemberSerializer().create(dat)
        ser = MemberSerializer(model)
    if name == 'history':
        model = HistorySerializer().create(dat)
        ser = HistorySerializer(model)
    if name == 'status':
        model = StatusSerializer().create(dat)
        ser = StatusSerializer(model)
    if name == 'rank':
        model = RankSerializer().create(dat)
        ser = RankSerializer(model)
    if name == 'duty':
        model = DutySerializer().create(dat)
        ser = DutySerializer(model)
    if name == 'volumerole':
        model = VolumeRoleSerializer().create(dat)
        ser = VolumeRoleSerializer(model)
    if name == 'kiosk':
        model = KioskSerializer().create(dat)
        ser = KioskSerializer(model)
    if name == 'badge':
        model = BadgeSerializer().create(dat)
        ser = BadgeSerializer(model)
    return JsonResponse(ser.data, safe=False)


@csrf_exempt
def deleteObj(request, event, name, pk):
    event_obj = get_object_or_404(Event, key=event)
    if name == 'member':
        model = Member.objects.get(pk=pk).delete()
    if name == 'status':
        model = Status.objects.get(pk=pk).delete()
    if name == 'rank':
        model = Rank.objects.get(pk=pk).delete()
    if name == 'duty':
        model = Duty.objects.get(pk=pk).delete()
    if name == 'volumerole':
        model = VolumeRole.objects.get(pk=pk).delete()
    if name == 'kiosk':
        model = ServiceKiosk.objects.get(pk=pk).delete()
    if name == 'badge':
        model = Badge.objects.get(pk=pk).delete()
    if name == 'history':
        model = History.objects.get(pk=pk).delete()
    return JsonResponse({"status": "success"}, safe=False)


@csrf_exempt
def editModal(request, event, name, pk):
    event_obj = get_object_or_404(Event, key=event)
    if name == 'member':
        model = Member.objects.get(pk=pk)
        form = MemberForm(instance=model)
        form.fields['volumeRole'].queryset = VolumeRole.objects.filter(event=event_obj)
        form.fields['rank'].queryset = Rank.objects.filter(event=event_obj)
    if name == 'status':
        model = Status.objects.get(pk=pk)
        form = StatusForm(instance=model)
    if name == 'rank':
        model = Rank.objects.get(pk=pk)
        form = RankForm(instance=model)
    if name == 'duty':
        model = Duty.objects.get(pk=pk)
        form = DutyForm(instance=model)
    if name == 'volumerole':
        model = VolumeRole.objects.get(pk=pk)
        form = VolumeRoleForm(instance=model)

    if name == 'kiosk':
        model = ServiceKiosk.objects.get(pk=pk)
        form = KioskForm(instance=model)
        form.fields['check_in_duty'].queryset = Duty.objects.filter(event=event_obj)
        form.fields['check_out_duty'].queryset = Duty.objects.filter(event=event_obj)
        form.fields['check_in_status'].queryset = Status.objects.filter(event=event_obj)
        form.fields['check_out_status'].queryset = Status.objects.filter(event=event_obj)
    if name == 'badge':
        model = Badge.objects.get(pk=pk)
        form = BadgeForm(instance=model)
        form.fields['member'].queryset = Member.objects.filter(event=event_obj)
    if name == 'history':
        model = History.objects.get(pk=pk)
        form = HistoryForm(instance=model)
        form.fields['member'].queryset = Member.objects.filter(event=event_obj)
        form.fields['status'].queryset = Status.objects.filter(event=event_obj)
        form.fields['duty'].queryset = Duty.objects.filter(event=event_obj)


    form.fields['event'].widget = forms.HiddenInput()

    return render(request, 'form_crispy.html', context={"form": form, "event": event_obj})

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def postEdit(request, event, name, pk):
    dat0 = request.data.copy()
    dat = {}
    #print(dat0)
    for x in dat0.keys():
        #print(x)
        dat[x] = dat0[x]
        if dat0[x] == "":
            dat[x] = None
        if dat0[x] == "true":
            dat[x] = True
        if dat0[x] == "false":
            dat[x] = False
    del dat['csrfmiddlewaretoken']
    model = None
    #print(dat)
    if name == 'member':
        ob = Member.objects.get(pk=pk)
        model = MemberSerializer().update(ob,dat)
        ser = MemberSerializer(instance=model)
    if name == 'status':
        ob = Status.objects.get(pk=pk)
        model = StatusSerializer().update(ob,dat)
        ser = StatusSerializer(instance=model)
    if name == 'rank':
        ob = Rank.objects.get(pk=pk)
        model = RankSerializer().update(ob,dat)
        ser = RankSerializer(instance=model)
    if name == 'duty':
        ob = Duty.objects.get(pk=pk)
        model = DutySerializer().update(ob,dat)
        ser = DutySerializer(instance=model)
    if name == 'volumerole':
        ob = VolumeRole.objects.get(pk=pk)
        model = VolumeRoleSerializer().update(ob,dat)
        ser = VolumeRoleSerializer(instance=model)
    if name == 'kiosk':
        ob = ServiceKiosk.objects.get(pk=pk)
        model = KioskSerializer().update(ob,dat)
        ser = KioskSerializer(instance=model)
    if name == 'badge':
        ob = Badge.objects.get(pk=pk)
        model = BadgeSerializer().update(ob,dat)
        ser = BadgeSerializer(instance=model)
    if name == 'event':
        ob = Event.objects.get(pk=pk)
        model = EventSerializer().update(ob,dat)
        ser = EventSerializer(instance=model)
    if name == 'history':
        ob = History.objects.get(pk=pk)
        model = HistorySerializer().update(ob,dat)
        ser = HistorySerializer(instance=model)
    model.save()
    return JsonResponse(ser.data, safe=False)

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bulkEventExecute(request, event):
    event_obj = get_object_or_404(Event, key=event)
    dn = request.data
    dat0 = request.data.copy()
    dat = {}
    print(dat0)
    for x in dat0.keys():
        print(x)
        if(x == 'names[]'):
            pass
        else:
            dat[x] = dat0[x]
    members = []
    for x in dn.getlist('names[]'):
        if x[0] == 'm':
            pk = x[1:]
            modal = Member.objects.get(pk=pk)
            members.append(modal)
        if x[0] == 'v':
            pk = x[1:]
            modal = VolumeRole.objects.get(pk=pk)
            for mbr in modal.getMembersWhoHaveThisRole():
                members.append(mbr)
    for member in members:
        duty = None
        try:
            duty = Duty.objects.get(pk=dat['task'])
        except:
            pass
        status = None
        try:
            status = Status.objects.get(pk=dat['status'])
        except:
            pass
        member.status = status
        member.duty = duty
        if dat0['content'] != '':
            member.details = dat0['content']
        member.save()
    return JsonResponse({"status": "success"}, safe=False)


def setKioskDuty(request, event, kiosk_pk, badge_number, duty_id):
    event_obj = get_object_or_404(Event, key=event)
    kiosk = get_object_or_404(ServiceKiosk, pk=kiosk_pk)
    badge = get_object_or_404(Badge, tag=badge_number, event=event_obj)
    duty = get_object_or_404(Duty, pk=duty_id)
    badge.member.duty = duty
    badge.member.save()
    return JsonResponse({"status": "success"}, safe=False)

def setKioskStatus(request, event, kiosk_pk, badge_number, status_id):
    event_obj = get_object_or_404(Event, key=event)
    kiosk = get_object_or_404(ServiceKiosk, pk=kiosk_pk)
    badge = get_object_or_404(Badge, tag=badge_number, event=event_obj)
    status = get_object_or_404(Status, pk=status_id)
    badge.member.status = status
    badge.member.save()
    return JsonResponse({"status": "success"}, safe=False)

def kioskStatuses(request, event, kiosk_pk):
    event_obj = get_object_or_404(Event, key=event)
    kiosk = get_object_or_404(ServiceKiosk, pk=kiosk_pk)
    statuses = Status.objects.filter(event=event_obj).order_by('key')
    return JsonResponse({"statuses": StatusSerializer(instance=statuses, many=True).data}, safe=False)

def kioskDuties(request, event, kiosk_pk):
    event_obj = get_object_or_404(Event, key=event)
    kiosk = get_object_or_404(ServiceKiosk, pk=kiosk_pk)
    duties = Duty.objects.filter(event=event_obj).order_by('key')
    return JsonResponse({"duties": DutySerializer(instance=duties, many=True).data}, safe=False)

class MemberAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"

class RankAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = "__all__"

class BadgeAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberAPISerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event']

class RankViewSet(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankAPISerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event']

class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeAPISerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event']


router = DefaultRouter()
router.register('api/v1/members', MemberViewSet)
router.register('api/v1/ranks', RankViewSet)
router.register('api/v1/badges', BadgeViewSet)

urlpatterns = [
    path('board/<str:event>/api/aux/', getAuxColumns),
    path('board/<str:event>/api/columns/', getMainColumns),
    path('board/<str:event>/api/members/', getMembers),
    path('board/<str:event>/api/member/<str:id>/', getMember),
    path('board/<str:event>/api/statuses/', getStatuses),
    path('board/<str:event>/api/tasks/', getTasks),
    path('board/<str:event>/api/tasks/', getTasks),
    path('board/<str:event>/api/volumeRoles/', getVolumeRoles),
    path('board/<str:event>/api/post/bulk/', bulkEventExecute),
    path('board/<str:event>/api/post/add/<str:name>/', postAdd),
    path('board/<str:event>/api/post/edit/<str:name>/<str:pk>/', postEdit),
    path('board/<str:event>/api/del/<str:name>/<str:pk>/', deleteObj),
    path('board/<str:event>/api/updateMember/<str:member_id>/status/<str:status_id>/', updateMembersStatus),
    path('board/<str:event>/api/updateMember/<str:member_id>/duty/<str:duty_id>/', updateMembersDuty),
    path('board/<str:event>/api/updateMember/<str:member_id>/details/', updateMembersDetails),
    path('board/<str:event>/timesheets/', getTimesheets),
    path('board/<str:event>/modals/sidebar/', sidebarMembers),
    path('board/<str:event>/modals/settings/', eventManagementPane),
    path('board/<str:event>/modals/event/details/', renderEventDetails),
    path('board/<str:event>/', renderBoard),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/', renderKiosk),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/set/<str:badge_number>/duty/<str:duty_id>/', setKioskDuty),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/set/<str:badge_number>/status/<str:status_id>/', setKioskStatus),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/statuses/', kioskStatuses),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/duties/', kioskDuties),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/badge/<str:badge_number>/', lookupBadgeNumberKiosk),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/data/', renderKioskData),
    path('board/<str:event>/kiosk/<str:kiosk_pk>/state/<str:template_name>/', renderKioskTemplate),
    path('board/<str:event>/modals/edit/<str:name>/<str:pk>/', editModal),
    path('board/<str:event>/modals/member/add/', addMember),
    path('board/<str:event>/modals/member/list/', memberList),
    path('board/<str:event>/modals/rank/list/', rankList),
    path('board/<str:event>/modals/rank/add/', rankAdd),
      path('board/<str:event>/modals/history/list/', historyList),
      path('board/<str:event>/modals/history/add/', historyAdd),
    path('board/<str:event>/modals/status/add/', statusAdd),
    path('board/<str:event>/modals/status/list/', statusList),
    path('board/<str:event>/modals/duty/add/', dutiesAdd),
    path('board/<str:event>/modals/duty/list/', dutiesList),
    path('board/<str:event>/modals/badge/add/', badgesAdd),
    path('board/<str:event>/modals/badge/list/', badgesList),
    path('board/<str:event>/modals/kiosk/add/', kioskAdd),
    path('board/<str:event>/modals/kiosk/list/', kioskList),
    path('board/<str:event>/modals/volumerole/add/', volumeRolesAdd),
    path('board/<str:event>/modals/volumerole/list/', volumeRolesList),
    path('board/<str:event>/modals/event/list/', eventDetailsForm),
    path('register/', SignUpView.as_view(), name='register'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('new/', newEvent, name='new'),
    path("select2/", include("django_select2.urls")),
    path('', index, name='index'),
] + router.urls
