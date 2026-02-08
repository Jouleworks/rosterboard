import asyncio
import json
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.utils import timezone
from rest_framework.serializers import ModelSerializer


# Create your models here.

class Event(models.Model):
    key = models.SlugField(unique=True, help_text="This will be the url key of the event and must be unique")
    name = models.CharField(max_length=100, help_text="Name of the Event")
    notes = models.TextField(blank=True, null=True, help_text="Supports Basic Markdown")
    highVolumeMode = models.BooleanField(default=False, help_text="Enables Member Teaming and High Volume Roles for Rapid Response")
    codes = models.JSONField(default=dict, help_text="Codes for Calls in format [key, name, color]")
    feature_mesh = models.BooleanField(default=False, help_text="Enables the feature to mesh radios")
    feature_mesh_api_base = models.CharField(max_length=255, help_text="Base URL for Mesh API", blank=True, null=True)
    feature_mesh_api_key = models.CharField(max_length=255, help_text="API Key for Mesh API", blank=True, null=True)
    feature_mesh_channel = models.IntegerField(default=0, help_text="Channel ID for Mesh API", blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.key, self.name)


class AccessRight(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    board = models.ForeignKey(Event, on_delete=models.CASCADE)


class VolumeRole(models.Model):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    key = models.CharField(max_length=100, help_text="This will appear on the Member's Status Entry")
    color = ColorField(default='#FF0000')
    sortOrder = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % (self.key)

    def getMembersWhoHaveThisRole(self):
        return Member.objects.filter(volumeRole=self)

    def stringListOfMembers(self):
        return ",".join([x.name for x in self.getMembersWhoHaveThisRole()])


class Status(models.Model):
    STATUSTYPES = (
        ('A', 'Available'),
        ('C', 'On a Call'),
        ('X', 'AFK'),
        ('Y', 'TDY'),
        ('Z', 'Gone')
    )

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    key = models.CharField(max_length=4, choices=STATUSTYPES, default='A', help_text="This grouping determines which column this section will fall under")
    color = ColorField(default='#0066FF')
    name = models.CharField(max_length=100, help_text="Name of the Status Column")
    sortOrder = models.IntegerField(default=0)
    hideFromColumns = models.BooleanField(default=False, help_text="If checked, it will show underneath the main columns in a larger section. Meant for storing users not active in tracking.")
    default = models.BooleanField(default=False, help_text="If checked, new members will be assigned this status on creation.")

    def __str__(self):
        return "%s - %s" % (self.key, self.name)


class Duty(models.Model):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    key = models.CharField(max_length=5, help_text="Quick Key of the Duty for at-a-glance assignment")
    color = ColorField(default='#0066FF')
    name = models.CharField(max_length=100, help_text="Name of the Duty")
    sortOrder = models.IntegerField(default=0)
    default = models.BooleanField(default=False, help_text="If checked, new members will be assigned this duty on creation.")

    def __str__(self):
        return "%s - %s" % (self.key, self.name)


class Rank(models.Model):
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    key = models.CharField(max_length=5, help_text="Displays the Rank of the Member, typically used to distinguish different ranks of responders.")
    color = ColorField(default='#0066FF')
    name = models.CharField(max_length=100, help_text="Full name of the Rank")
    sortOrder = models.IntegerField(default=0)
    displayOnSidebar = models.BooleanField(default=True, help_text="If checked, a list of Members with this Rank will be displayed on the Sidebar of the Board.")
    default = models.BooleanField(default=False, help_text="If checked, new members will be assigned this Rank on creation if not preassigned.")

    def __str__(self):
        return "%s (%s)" % (self.name, self.key)

    def getMembersWhoHaveThisRank(self):
        return Member.objects.filter(rank=self)


class Member(models.Model):
    VACCINE_STATUSES = (
        ("?", "TBD"),
        ("R", "DANGER"),
        ("O", "RISK"),
        ("Y", "OKAY"),
        ("G", "OPTIMAL")
    )

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, help_text="Name of the Member which will show on the board.")
    vaccineStatus = models.CharField(max_length=2, choices=VACCINE_STATUSES, default="?", help_text="Used for Record Keeping")
    radioNumber = models.TextField(blank=True, null=True, help_text="Used for record keeping")
    details = models.TextField(blank=True, null=True, help_text="Shows in the Information Line of the Member's status entry.")
    lastUpdate = models.DateTimeField(auto_now=True)
    volumeRole = models.ForeignKey(VolumeRole, on_delete=models.SET_NULL, null=True, blank=True, help_text="Assigned Role during High Volume Operations. This can be assigned later.")
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True, help_text="Initial Status")
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True, help_text="Initial Rank")
    duty = models.ForeignKey(Duty, on_delete=models.SET_NULL, null=True, blank=True, help_text="Initial Duty")


    def getFirstTag(self):
        try:
            return Badge.objects.filter(member=self).first().tag
        except:
            return ""


    def decide_tag(self):
        if Badge.objects.filter(member=self).exists():

            bad = Badge.objects.filter(member=self).first().tag

            b = ""
            try:
                b = bad.split("-")[1]
            except:
                b = bad

            return bad + " // "

    def __str__(self):
        return "%s%s" % (self.decide_tag(), self.name)

    def getAllHistoryDurations(self):
        history = History.objects.filter(member=self).order_by('time_in')
        # sum all durations
        total_duration = sum([d.duration() for d in history], timedelta())
        return total_duration

    def getHistory(self):
        return History.objects.filter(member=self).order_by('time_in')

    def save(self, bypass_webook_fire=False, *args, **kwargs):
        old_instance = Member.objects.filter(pk=self.pk).first()
        sv = super(Member, self).save(*args, **kwargs)
        if(self.event == None):
            return sv
        #print(old_instance.status, self.status)
        if self.status != None and old_instance.status != None:
            if(old_instance != None):
                if ((old_instance.status.key == "A" or old_instance.status.key == "Y") and (self.status.key == "Z" or self.status.key == "X")):
                    History.objects.create(
                        event=self.event,
                        member=self,
                        status=self.status,
                        duty=self.duty,
                        time_in=old_instance.lastUpdate,
                        time_out=timezone.now(),
                        notes=self.details
                    )

        #from channels.layers import get_channel_layer
        if(bypass_webook_fire == False):
            ChatConsumer.send_online({
                "type": "action.move",
                "userid": str(self.id),
                "userdata": None,
                "client": "SAVEMODEL"
            }, self.event.key)
        #print("Hello??")
        try:
            return super(Member, self).save(*args, **kwargs)
        except IntegrityError:
            pass
        # ChatConsumer().send(text_data=json.dumps({
        #    "type": "user.inplacechange",
        #    "userid": str(self.id),
        #    "userdata": InjectMemberSerializer(instance=self).data
        # }))


class Badge(models.Model):
    member = models.ForeignKey('roster.Member', on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey('roster.Event', on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True)
    tag = models.CharField(max_length=100)
    def __str__(self):
        return self.tag

class ServiceKiosk(models.Model):
    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    event = models.ForeignKey('roster.Event', on_delete=models.CASCADE, blank=True, null=True)
    single_state_only = models.BooleanField(default=False)
    automated_check_in_out = models.BooleanField(default=False, help_text="Puts Kiosk into Automated Mode. If Single State is False, will display Check-In and Check-Out automations. If Single State is True, will Display only Check-In automation.")
    allow_status_selection = models.BooleanField(default=False, help_text="Allows the selection of a Status if in Self Service Mode (Automated Checkin False, Single State False).")
    allow_duty_selection = models.BooleanField(default=False, help_text="Allows the selection of a Duty if in Self Service Mode (Automated Checkin False, Single State False).")
    check_in_status = models.ForeignKey('roster.Status', related_name='check_in_status', on_delete=models.SET_NULL, blank=True, null=True)
    check_in_duty = models.ForeignKey('roster.Duty', related_name='check_in_duty', on_delete=models.SET_NULL, blank=True, null=True)
    check_out_status = models.ForeignKey('roster.Status', related_name='check_out_status', on_delete=models.SET_NULL, blank=True, null=True)
    check_out_duty = models.ForeignKey('roster.Duty', related_name='check_out_duty', on_delete=models.SET_NULL, blank=True, null=True)


class InjectMemberSerializer(ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @staticmethod
    def send_online(data, receiver_pk):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_{}'.format(receiver_pk),
            data
        )

class History(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    duty = models.ForeignKey(Duty, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    time_in = models.DateTimeField(blank=True, null=True)
    time_out = models.DateTimeField(blank=True, null=True)
    def duration(self):
        if self.time_out and self.time_in:
            return self.time_out - self.time_in
        else:
            return None

class Call(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    callKey = models.CharField(default="NEW", max_length=255)
    title = models.CharField(max_length=100)
    callStart = models.DateTimeField(blank=True, null=True)
    callEnd = models.DateTimeField(blank=True, null=True)
    initialCode = models.CharField(max_length=100, blank=True, null=True)
    revisedCode = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    membersAttached = models.ManyToManyField(Member, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if (self.callKey == "NEW"):
            self.callKey = Call.objects.filter(event=self.event).count()
        super().save(*args, **kwargs)
