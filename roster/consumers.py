import json
import os
import time
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rosterBoardJ.settings')
import django
django.setup()
from roster.models import Member
from roster.serializers import MemberSerializer




class ChatConsumer(WebsocketConsumer):
    __lock_log = []
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        print(text_data_json)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, text_data_json
        )

    def boards_reloadall(self, event):
        self.send(text_data=json.dumps(event))
        return

    def locklog_unlock(self, event):
        # first we have to find the lock in the log.
        for x in self.__lock_log:
            if x['lockedby'] == event['lockedby'] and x['userid'] == event['userid']:
                self.__lock_log.remove(x)
                self.send(text_data=json.dumps({"forClient": event['lockedby'], "type": event['type'], "userdata": MemberSerializer(instance=Member.objects.get(pk=event['userid'])).data, "userid": event['userid'],  "success": True}))
                return

        self.send(text_data=json.dumps(
            {"forClient": event['lockedby'], "type": event['type'], "userid": event['userid'], "userdata": MemberSerializer(instance=Member.objects.get(pk=event['userid'])).data, "success": True}))
        return

    def user_inplacechange(self, event):
        passable = event
        passable['userdata'] = MemberSerializer(instance=Member.objects.get(pk=event['userid'])).data
        self.send(text_data=json.dumps(passable))
    def action_move(self, event):
        passable = event
        passable['userdata'] = MemberSerializer(instance=Member.objects.get(pk=event['userid'])).data
        self.send(text_data=json.dumps(passable))

    def locklog_lock(self, event):
        # first check for active locks in log
        i = 0
        valid_locks = []
        for x in self.__lock_log:
            # x['validuntil'] is a linux timestamp in seconds
            if x['validuntil'] < time.time():
                valid_locks.append(x)
                # then we check if the locked member in the valid lock is the one we're trying to lock
                if x['userid'] == event['userid']:
                    # if so, we deny the lock request from the client
                    self.send(text_data=json.dumps({"forClient": event['lockedby'], "userid": event['userid'], "type": event['type'], "success": True}))
                    return
            else:
                # remove this lock from the log
                self.__lock_log.remove(self.__lock_log[i])
            i += 1
        self.__lock_log = valid_locks
        # we did not find a valid lock in the log, so we lock it
        self.__lock_log.append(event)
        self.send(text_data=json.dumps({"forClient": event['lockedby'], "userid": event['userid'], "type": event['type'], "success": True}))
        return

    def fetch_locklog(self, event):
        client = event['client']
        self.send(text_data=json.dumps({"forClient": client, "type": event['type'], "message": self.__lock_log}))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))