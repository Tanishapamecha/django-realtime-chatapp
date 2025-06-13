import json
import datetime
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer

from collections import defaultdict
from django.utils.timezone import now

# Dictionary to track online users by room
online_users = defaultdict(set)

# Dictionary to store last seen time per user
last_seen = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Get username from WebSocket query string
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        self.username = params.get('username', ['Guest'])[0]

        # Add user to online list
        online_users[self.room_name].add(self.username)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Notify all clients with updated user lists
        await self.send_user_updates()

    async def disconnect(self, close_code):
        # Remove user from online list
        online_users[self.room_name].discard(self.username)

        # Save current time as last seen
        last_seen[self.username] = now().strftime('%I:%M %p')

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Notify others about updated user lists
        await self.send_user_updates()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'chat_message':
            timestamp = datetime.datetime.now().strftime('%I:%M %p')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'username': self.username,
                    'timestamp': timestamp
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def send_user_updates(self):
        # Online users in current room
        online = list(online_users[self.room_name])

        # Offline users are everyone we’ve seen before who are not online now
        offline = {
            user: last_seen[user]
            for user in last_seen
            if user not in online
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_updated_users',
                'users': online,
                'offline_users': offline
            }
        )

    async def send_updated_users(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_users_update',
            'users': event['users'],
            'offline_users': event['offline_users']
        }))
