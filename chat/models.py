from django.db import models
from django.contrib.auth.models import User

# This model stores chat messages per room
class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} in {self.room_name}: {self.message[:30]}"


# This model stores the user's last seen time
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


# This model saves chat messages by user for each room
class Message(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} in {self.room_name}: {self.content[:30]}"


# This model keeps track of how many messages are unread
class UnreadMessageCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    unread_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} in {self.room_name} - {self.unread_count} unread"
