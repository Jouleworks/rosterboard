from rest_framework import serializers

from roster.models import Call, Duty, Event, VolumeRole, Status, Rank, Member, ServiceKiosk, Badge, History


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = '__all__'


class DutySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        event_data = validated_data.pop('event')
        return super().update(instance=instance, validated_data=validated_data)
    def create(self, validated_data):
        event_data = validated_data.pop('event')
        if validated_data['default'] == "on":
            validated_data['default'] = True
        else:
            validated_data['default'] = False
        duty = Duty.objects.create(**validated_data)
        duty.event = Event.objects.get(id=event_data)
        duty.save()
        return duty

    class Meta:
        model = Duty
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        volumeRole_data = None
        status_data = None
        rank_data = None
        duty_data = None

        event_data = validated_data.pop('event')
        try:
            if validated_data.get('volumeRole') != None:
                volumeRole_data = validated_data.pop('volumeRole')
        except:
            pass
        try:
            if validated_data.get('status') != None:
                status_data = validated_data.pop('status')
        except:
            pass
        try:
            if validated_data.get('rank') != None:
                rank_data = validated_data.pop('rank')
        except:
            pass
        try:
            if validated_data.get('duty') != None:
                duty_data = validated_data.pop('duty')
        except:
            pass

        member = super().update(instance=instance, validated_data=validated_data)
        try:
            member.volumeRole = VolumeRole.objects.get(pk=volumeRole_data)
        except:
            pass
        try:
            member.status = Status.objects.get(pk=status_data)
        except:
            pass
        try:
            member.rank = Rank.objects.get(pk=rank_data)
        except:
            pass
        try:
            member.duty = Duty.objects.get(pk=duty_data)
        except:
            pass
        member.save()
        return member
    def create(self, validated_data):

        volumeRole_data = None
        status_data = None
        rank_data = None
        duty_data = None

        event_data = validated_data.pop('event')
        try:
            volumeRole_data = validated_data.pop('volumeRole')
        except:
            pass
        try:
            status_data = validated_data.pop('status')
        except:
            pass
        try:
            rank_data = validated_data.pop('rank')
        except:
            pass
        try:
            duty_data = validated_data.pop('duty')
        except:
            pass

        member = Member.objects.create(**validated_data)
        member.event = Event.objects.get(id=event_data)
        try:
            member.volumeRole = VolumeRole.objects.get(pk=volumeRole_data)
        except:
            pass
        try:
            member.status = Status.objects.get(pk=status_data)
        except:
            pass
        try:
            member.rank = Rank.objects.get(pk=rank_data)
        except:
            pass
        try:
            member.duty = Duty.objects.get(pk=duty_data)
        except:
            pass
        member.save()
        return member

    class Meta:
        model = Member
        fields = '__all__'
        depth = 2


class RankSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        event_data = validated_data.pop('event')
        return super().update(instance=instance, validated_data=validated_data)
    def create(self, validated_data):
        event_data = validated_data.pop('event')
        try:
            if validated_data['displayOnSidebar'] == "on":
                validated_data['displayOnSidebar'] = True
            else:
                validated_data['displayOnSidebar'] = False
        except KeyError:
            validated_data['displayOnSidebar'] = False
        try:
            if validated_data['default'] == "on":
                validated_data['default'] = True
            else:
                validated_data['default'] = False
        except KeyError:
            validated_data['default'] = False
        rank = Rank.objects.create(**validated_data)
        rank.event = Event.objects.get(id=event_data)
        rank.save()
        return rank

    class Meta:
        model = Rank
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        event_data = validated_data.pop('event')
        return super().update(instance=instance, validated_data=validated_data)
    def create(self, validated_data):
        event_data = validated_data.pop('event')
        status = Status.objects.create(**validated_data)
        status.event = Event.objects.get(id=event_data)
        status.save()
        return status

    class Meta:
        model = Status
        fields = '__all__'



class BadgeSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        member_data = None

        event_data = validated_data.pop('event')
        try:
            if validated_data.get('member') != None:
                member_data = validated_data.pop('member')
        except:
            pass


        badge = super().update(instance=instance, validated_data=validated_data)
        badge.event = Event.objects.get(id=event_data)
        try:
            badge.member = Member.objects.get(pk=member_data)
        except:
            pass

        badge.save()
        return badge
    def create(self, validated_data):

        member_data = None

        event_data = validated_data.pop('event')
        try:
            member_data = validated_data.pop('member')
        except:
            pass
        try:
            if validated_data['active'] == "on":
                validated_data['active'] = True
            else:
                validated_data['active'] = False
        except KeyError:
            pass
        badge = Badge.objects.create(**validated_data)
        badge.event = Event.objects.get(id=event_data)
        try:
            badge.member = Member.objects.get(pk=member_data)
        except:
            pass
        badge.save()
        return badge

    class Meta:
        model = ServiceKiosk
        fields = '__all__'
        depth = 2


class HistorySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        member_data = None
        status_data = None
        duty_data = None
        event_data = validated_data.pop('event')
        try:
            if validated_data.get('member') != None:
                member_data = validated_data.pop('member')
        except:
            pass
        try:
            if validated_data.get('status') != None:
                status_data = validated_data.pop('status')
        except:
            pass
        try:
            if validated_data.get('duty') != None:
                duty_data = validated_data.pop('duty')
        except:
            pass

        print("vaaa", validated_data)

        kiosk = super().update(instance=instance, validated_data=validated_data)
        kiosk.event = Event.objects.get(id=event_data)
        try:
            kiosk.member = Member.objects.get(pk=member_data)
        except:
            pass
        try:
            kiosk.status = Status.objects.get(pk=status_data)
        except:
            pass
        try:
            kiosk.duty = Duty.objects.get(pk=duty_data)
        except:
            pass
        kiosk.save()
        return kiosk
    def create(self, validated_data):

        member_data = None
        status_data = None
        duty_data = None
        event_data = validated_data.pop('event')
        try:
            if validated_data.get('member') != None:
                member_data = validated_data.pop('member')
        except:
            pass
        try:
            if validated_data.get('status') != None:
                status_data = validated_data.pop('status')
        except:
            pass
        try:
            if validated_data.get('duty') != None:
                duty_data = validated_data.pop('duty')
        except:
            pass

        print("vaaa", validated_data)

        kiosk = super().create(validated_data)
        kiosk.event = Event.objects.get(id=event_data)
        try:
            kiosk.member = Member.objects.get(pk=member_data)
        except:
            pass
        try:
            kiosk.status = Status.objects.get(pk=status_data)
        except:
            pass
        try:
            kiosk.duty = Duty.objects.get(pk=duty_data)
        except:
            pass
        kiosk.save()
        return kiosk

    class Meta:
        model = ServiceKiosk
        fields = '__all__'
        depth = 2

class KioskSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        check_in_status_data = None
        check_out_status_data = None
        check_in_duty_data = None
        check_out_duty_data = None
        event_data = validated_data.pop('event')
        try:
            if validated_data.get('check_in_status') != None:
                check_in_status_data = validated_data.pop('check_in_status')
        except:
            pass
        try:
            if validated_data.get('check_out_status') != None:
                check_out_status_data = validated_data.pop('check_out_status')
        except:
            pass
        try:
            if validated_data.get('check_in_duty') != None:
                check_in_duty_data = validated_data.pop('check_in_duty')
        except:
            pass
        try:
            if validated_data.get('check_out_duty') != None:
                check_out_duty_data = validated_data.pop('check_out_duty')
        except:
            pass

        print("vaaa", validated_data)

        kiosk = super().update(instance=instance, validated_data=validated_data)
        kiosk.event = Event.objects.get(id=event_data)
        try:
            kiosk.check_in_status = Status.objects.get(pk=check_in_status_data)
        except:
            pass
        try:
            kiosk.check_out_status = Status.objects.get(pk=check_out_status_data)
        except:
            pass
        try:
            kiosk.check_in_duty = Duty.objects.get(pk=check_in_duty_data)
        except:
            pass
        try:
            kiosk.check_out_duty = Duty.objects.get(pk=check_out_duty_data)
        except:
            pass
        kiosk.save()
        return kiosk
    def create(self, validated_data):

        check_in_status_data = None
        check_out_status_data = None
        check_in_duty_data = None
        check_out_duty_data = None

        event_data = validated_data.pop('event')
        uuid_data = validated_data.pop('initial-uuid')
        try:
            check_in_status_data = validated_data.pop('check_in_status')
        except:
            pass
        try:
            check_out_status_data = validated_data.pop('check_out_status')
        except:
            pass
        try:
            check_in_duty_data = validated_data.pop('check_in_duty')
        except:
            pass
        try:
            check_out_duty_data = validated_data.pop('check_out_duty')
        except:
            pass
        try:
            if validated_data['single_state_only'] == "on":
                validated_data['single_state_only'] = True
            else:
                validated_data['single_state_only'] = False
        except KeyError:
            pass

        try:
            if validated_data['automated_check_in_out'] == "on":
                validated_data['automated_check_in_out'] = True
            else:
                validated_data['automated_check_in_out'] = False
        except KeyError:
            pass

        try:
            if validated_data['allow_status_selection'] == "on":
                validated_data['allow_status_selection'] = True
            else:
                validated_data['allow_status_selection'] = False
        except KeyError:
            pass

        try:
            if validated_data['allow_duty_selection'] == "on":
                validated_data['allow_duty_selection'] = True
            else:
                validated_data['allow_duty_selection'] = False
        except KeyError:
            pass

        kiosk = ServiceKiosk.objects.create(**validated_data)
        kiosk.event = Event.objects.get(id=event_data)
        try:
            kiosk.check_in_status = Status.objects.get(pk=check_in_status_data)
        except:
            pass
        try:
            kiosk.check_out_status = Status.objects.get(pk=check_out_status_data)
        except:
            pass
        try:
            kiosk.check_in_duty = Duty.objects.get(pk=check_in_duty_data)
        except:
            pass
        try:
            kiosk.check_out_duty = Duty.objects.get(pk=check_out_duty_data)
        except:
            pass
        kiosk.save()
        return kiosk

    class Meta:
        model = ServiceKiosk
        fields = '__all__'
        depth = 2

class VolumeRoleSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        event_data = validated_data.pop('event')
        return super().update(instance=instance, validated_data=validated_data)
    def create(self, validated_data):
        event_data = validated_data.pop('event')
        volumerole = VolumeRole.objects.create(**validated_data)
        volumerole.event = Event.objects.get(id=event_data)
        volumerole.save()
        return volumerole

    class Meta:
        model = VolumeRole
        fields = ['id', 'event', 'key', 'color', 'sortOrder', 'stringListOfMembers']
