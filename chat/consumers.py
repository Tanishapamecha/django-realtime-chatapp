import json
import datetime
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer

# Track online users by room
online_users = {}

# Store last seen timestamps for each user
last_seen = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get room name from URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Get username from query string
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        self.username = params.get('username', ['Guest'])[0]

        # Add user to online list for the room
        if self.room_name not in online_users:
            online_users[self.room_name] = set()
        online_users[self.room_name].add(self.username)

        # Join WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify others to update user lists
        await self.send_user_updates()

    async def disconnect(self, close_code):
        # Remove user from online list
        if self.room_name in online_users:
            online_users[self.room_name].discard(self.username)

        # Save last seen time
        last_seen[self.username] = datetime.datetime.now().strftime('%I:%M %p')

        # Leave WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify others to update user lists
        await self.send_user_updates()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'chat_message':
            # Generate message timestamp
            timestamp = datetime.datetime.now().strftime('%I:%M %p')

            # Broadcast the message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': self.username,
                    'message': data['message'],
                    'timestamp': timestamp
                }
            )

    async def chat_message(self, event):
        # Send the message to the current WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'username': event['username'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    async def send_user_updates(self):
        # List of online users in the room
        users_online = list(online_users.get(self.room_name, []))

        # All known users not currently online
        users_offline = {
            user: last_seen[user]
            for user in last_seen
            if user not in users_online
        }

        # Send online/offline user updates to all group members
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_updated_users',
                'users': users_online,
                'offline_users': users_offline
            }
        )

    async def send_updated_users(self, event):
        # Send updated user lists to the frontend
        await self.send(text_data=json.dumps({
            'type': 'online_users_update',
            'users': event['users'],
            'offline_users': event['offline_users']
        }))
