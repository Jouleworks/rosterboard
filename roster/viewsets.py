from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from roster.models import (
    AccessRight, VolumeRole, Status, Duty, Rank, 
    Member, Badge, ServiceKiosk, History, Call
)
from roster.serializers import (
    DutySerializer, StatusSerializer, MemberSerializer,
    VolumeRoleSerializer, RankSerializer, EventSerializer,
    KioskSerializer, BadgeSerializer, HistorySerializer,
    CallSerializer, AccessRightSerializer
)


class AccessRightViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AccessRight objects.
    AccessRight links a User to an Event (board).
    """
    queryset = AccessRight.objects.all()
    serializer_class = AccessRightSerializer  # Using EventSerializer as AccessRight doesn't have its own serializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'board']


class VolumeRoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing VolumeRole objects.
    VolumeRole represents a role assigned during High Volume Operations.
    """
    queryset = VolumeRole.objects.all()
    serializer_class = VolumeRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'key']
    ordering_fields = ['sortOrder', 'key']
    ordering = ['sortOrder']


class StatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Status objects.
    Status represents the different states a Member can be in.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'key', 'default', 'hideFromColumns']
    ordering_fields = ['sortOrder', 'key', 'name']
    ordering = ['sortOrder']


class DutyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Duty objects.
    Duty represents a task or assignment for Members.
    """
    queryset = Duty.objects.all()
    serializer_class = DutySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'key', 'default']
    ordering_fields = ['sortOrder', 'key', 'name']
    ordering = ['sortOrder']


class RankViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Rank objects.
    Rank represents the rank or level of a Member.
    """
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'key', 'default', 'displayOnSidebar']
    ordering_fields = ['sortOrder', 'key', 'name']
    ordering = ['sortOrder']


class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Member objects.
    Member represents a person in the roster system.
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'status', 'rank', 'duty', 'volumeRole', 'vaccineStatus']
    ordering_fields = ['name', 'lastUpdate', 'radioNumber']
    ordering = ['name']


class BadgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Badge objects.
    Badge represents an RFID or other identification tag linked to a Member.
    """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'member', 'tag', 'active']
    ordering_fields = ['tag']
    ordering = ['tag']


class ServiceKioskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing ServiceKiosk objects.
    ServiceKiosk represents a self-service station for Members.
    """
    queryset = ServiceKiosk.objects.all()
    serializer_class = KioskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'single_state_only', 'automated_check_in_out']
    ordering_fields = ['uuid']


class HistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing History objects.
    History records the time tracking of Members.
    """
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'member', 'status', 'duty', 'time_in', 'time_out']
    ordering_fields = ['time_in', 'time_out']
    ordering = ['-time_in']


class CallViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Call objects.
    Call represents a dispatch or emergency call.
    """
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'callKey', 'initialCode', 'revisedCode', 'callStart', 'callEnd']
    ordering_fields = ['callStart', 'callEnd', 'callKey']
    ordering = ['-callStart']
