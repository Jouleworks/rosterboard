from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from roster.models import Event, Member, Rank, Duty, Status, AccessRight, VolumeRole


class Command(BaseCommand):
    help = "Set all accounts sudo_until to now"

    def add_arguments(self, parser):
        parser.add_argument('from_event', type=str)
        parser.add_argument('to_event', type=str)
        parser.add_argument('--members', action='store_true', help='copies members objects')
        parser.add_argument('--ranks', action='store_true', help='copies rank objects, keeps member ranks if selected in tandem')
        parser.add_argument('--duties', action='store_true', help='copies duty objects, keeps member duties if selected in tandem')
        parser.add_argument('--statuses', action='store_true', help='copies status objects, keeps member column location if selected in tandem')
        parser.add_argument('--clean', action='store_true', help='Pass to wipe config from the destination event before copying')
        parser.add_argument('--volumeRoles', action='store_true', help='copies volume roles objects, keeps member column location if selected in tandem')


    def handle(self, *args, **options):
        event1 = Event.objects.get(key=options['from_event'])
        event2 = Event.objects.get(key=options['to_event'])
        if options['clean']:
            self.stdout.write(self.style.WARNING('Cleaning destination event config...'))
            Member.objects.filter(event=event2).delete()
            Rank.objects.filter(event=event2).delete()
            Duty.objects.filter(event=event2).delete()
            Status.objects.filter(event=event2).delete()
            VolumeRole.objects.filter(event=event2).delete()
            event2.save()
        event2.notes = event1.notes
        event2.highVolumeMode = event1.highVolumeMode
        eA = AccessRight.objects.filter(board=event1)

        rank_lib = {

        }
        duty_lib = {

        }
        status_lib = {

        }
        volumeRole_lib = {

        }

        for a in eA:
            AccessRight.objects.create(board=event2, user=a.user)
        if options['ranks']:
            print("Copying ranks...")
            for rank in Rank.objects.filter(event=event1):
                rank2 = Rank.objects.create(event=event2,
                                    key=rank.key,
                                    color=rank.color,
                                    name=rank.name,
                                    sortOrder=rank.sortOrder,
                                    default=rank.default,
                                    displayOnSidebar=rank.displayOnSidebar)
                rank_lib[rank.key] = rank2
        if options['duties']:
            print("Copying duties...")
            for duty in Duty.objects.filter(event=event1):
                duty2 = Duty.objects.create(event=event2,
                                    key=duty.key,
                                    color=duty.color,
                                    name=duty.name,
                                    sortOrder=duty.sortOrder,
                                    default=duty.default)
                duty_lib[duty.key] = duty2
        if options['statuses']:
            print("Copying statuses...")
            for status in Status.objects.filter(event=event1):
                status2 = Status.objects.create(event=event2,
                                    key=status.key,
                                    color=status.color,
                                    name=status.name,
                                    sortOrder=status.sortOrder,
                                    hideFromColumns=status.hideFromColumns,
                                    default=status.default)
                status_lib[status.key] = status2
        if options['volumeRoles']:
            print("Copying volume roles...")
            for volumeRole in VolumeRole.objects.filter(event=event1):
                volumeRole2 = VolumeRole.objects.create(event=event2,
                                    key=volumeRole.key,
                                    sortOrder=volumeRole.sortOrder,
                                    color=volumeRole.color)
                volumeRole_lib[volumeRole.key] = volumeRole2
        if options['members']:
            print("Copying members...")
            default_rank = Rank.objects.filter(event=event2, default=True).first()
            default_status = Status.objects.filter(event=event2, default=True).first()
            default_duty = Duty.objects.filter(event=event2, default=True).first()
            for member in Member.objects.filter(event=event1):
                m2 = Member.objects.create(event=event2,
                                           name=member.name,
                                           vaccineStatus=member.vaccineStatus,
                                           radioNumber=member.radioNumber,
                                           details=member.details)
                if options['ranks']:
                    m2.rank = rank_lib.get(member.rank.key, default_rank)
                if options['statuses']:
                    m2.status = status_lib.get(member.status.key, default_status)
                if options['duties']:
                    m2.duty = duty_lib.get(member.duty.key, default_duty)
                if options['volumeRoles']:
                    try:
                        m2.volumeRole = volumeRole_lib.get(member.volumeRole.key, None)
                    except AttributeError:
                        pass
                m2.save()
