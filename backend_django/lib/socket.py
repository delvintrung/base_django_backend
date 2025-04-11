import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from ..models import Message  # Giống như mongoose.model

user_sockets = {}
user_activities = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Socket connected")

    async def disconnect(self, close_code):
        user_id = None
        for uid, sid in user_sockets.items():
            if sid == self.channel_name:
                user_id = uid
                break

        if user_id:
            user_sockets.pop(user_id)
            user_activities.pop(user_id)
            await self.broadcast("user_disconnected", user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data.get("event")

        if event == "user_connected":
            user_id = data["userId"]
            user_sockets[user_id] = self.channel_name
            user_activities[user_id] = "Idle"

            await self.send(text_data=json.dumps({
                "event": "users_online",
                "data": list(user_sockets.keys()),
            }))

            await self.broadcast("user_connected", user_id)
            await self.broadcast("activities", list(user_activities.items()))

        elif event == "update_activity":
            user_id = data["userId"]
            activity = data["activity"]
            user_activities[user_id] = activity
            await self.broadcast("activity_updated", {"userId": user_id, "activity": activity})

        elif event == "send_message":
            try:
                sender_id = data["senderId"]
                receiver_id = data["receiverId"]
                content = data["content"]

                message = await sync_to_async(Message.objects.create)(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    content=content
                )

                if receiver_id in user_sockets:
                    await self.channel_layer.send(
                        user_sockets[receiver_id],
                        {
                            "type": "send.message",
                            "message": {
                                "event": "receive_message",
                                "data": {
                                    "id": message.id,
                                    "senderId": sender_id,
                                    "receiverId": receiver_id,
                                    "content": content,
                                }
                            }
                        }
                    )

                await self.send(text_data=json.dumps({
                    "event": "message_sent",
                    "data": {
                        "id": message.id,
                        "senderId": sender_id,
                        "receiverId": receiver_id,
                        "content": content,
                    }
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "event": "message_error",
                    "error": str(e)
                }))

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def broadcast(self, event_name, data):
        for sid in user_sockets.values():
            await self.channel_layer.send(sid, {
                "type": "send.message",
                "message": {
                    "event": event_name,
                    "data": data
                }
            })
