import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from mongoengine import connect
from ..models.message import Message
from collections import defaultdict

class ChatConsumer(AsyncWebsocketConsumer):
    user_sockets = defaultdict(set)  # {user_id: set(socket_channel_names)}
    user_activities = {}  # {user_id: activity}

    async def connect(self):
        await self.accept()
        self.user_id = None

    async def disconnect(self, close_code):
        if self.user_id:
            # Xóa socket khỏi user_sockets
            self.user_sockets[self.user_id].discard(self.channel_name)
            if not self.user_sockets[self.user_id]:
                del self.user_sockets[self.user_id]
                # Xóa hoạt động
                if self.user_id in self.user_activities:
                    del self.user_activities[self.user_id]
                # Phát thông báo người dùng ngắt kết nối
                await self.channel_layer.group_send(
                    "chat_global",
                    {
                        "type": "user_disconnected",
                        "user_id": self.user_id,
                    }
                )
            # Xóa khỏi nhóm toàn cục
            await self.channel_layer.group_discard("chat_global", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data.get("event")

        if event == "user_connected":
            user_id = data.get("user_id")
            self.user_id = user_id
            # Thêm socket vào user_sockets
            self.user_sockets[user_id].add(self.channel_name)
            # Đặt hoạt động ban đầu
            self.user_activities[user_id] = "Idle"
            # Thêm vào nhóm toàn cục để phát tin
            await self.channel_layer.group_add("chat_global", self.channel_name)
            # Phát thông báo người dùng đã kết nối
            await self.channel_layer.group_send(
                "chat_global",
                {
                    "type": "user_connected",
                    "user_id": user_id,
                }
            )
            # Gửi danh sách người dùng trực tuyến cho client vừa kết nối
            await self.send(text_data=json.dumps({
                "event": "users_online",
                "users": list(self.user_sockets.keys()),
            }))
            # Phát danh sách hoạt động hiện tại
            await self.channel_layer.group_send(
                "chat_global",
                {
                    "type": "activities",
                    "activities": self.user_activities,
                }
            )

        elif event == "update_activity":
            user_id = data.get("user_id")
            activity = data.get("activity")
            print(f"Hoạt động cập nhật: {user_id} -> {activity}")
            self.user_activities[user_id] = activity
            # Phát thông báo cập nhật hoạt động
            await self.channel_layer.group_send(
                "chat_global",
                {
                    "type": "activity_updated",
                    "user_id": user_id,
                    "activity": activity,
                }
            )

        elif event == "send_message":
            sender_id = data.get("sender_id")
            receiver_id = data.get("receiver_id")
            content = data.get("content")
            try:
                # Lưu tin nhắn vào MongoDB
                message = await self.create_message(sender_id, receiver_id, content)
                message_data = {
                    "id": str(message.id),  # MongoEngine ID là ObjectId, cần chuyển sang string
                    "senderId": message.senderId,
                    "receiverId": message.receiverId,
                    "content": message.content,
                    "createdAt": message.createdAt.isoformat(),
                    "updatedAt": message.updatedAt.isoformat(),
                }
                # Gửi tin nhắn đến người nhận nếu họ đang trực tuyến
                if receiver_id in self.user_sockets:
                    for channel_name in self.user_sockets[receiver_id]:
                        await self.channel_layer.send(
                            channel_name,
                            {
                                "type": "receive_message",
                                "message": message_data,
                            }
                        )
                # Xác nhận với người gửi
                await self.send(text_data=json.dumps({
                    "event": "message_sent",
                    "message": message_data,
                }))
            except Exception as e:
                print(f"Lỗi tin nhắn: {e}")
                await self.send(text_data=json.dumps({
                    "event": "message_error",
                    "error": str(e),
                }))

    @database_sync_to_async
    def create_message(self, sender_id, receiver_id, content):
        # Tạo và lưu tin nhắn với MongoEngine
        message = Message(
            senderId=sender_id,
            receiverId=receiver_id,
            content=content,
        )
        message.save()
        return message

    # Xử lý sự kiện user_connected
    async def user_connected(self, event):
        await self.send(text_data=json.dumps({
            "event": "user_connected",
            "user_id": event["user_id"],
        }))

    # Xử lý sự kiện user_disconnected
    async def user_disconnected(self, event):
        await self.send(text_data=json.dumps({
            "event": "user_disconnected",
            "user_id": event["user_id"],
        }))

    # Xử lý sự kiện activities
    async def activities(self, event):
        await self.send(text_data=json.dumps({
            "event": "activities",
            "activities": event["activities"],
        }))

    # Xử lý sự kiện activity_updated
    async def activity_updated(self, event):
        await self.send(text_data=json.dumps({
            "event": "activity_updated",
            "user_id": event["user_id"],
            "activity": event["activity"],
        }))

    # Xử lý sự kiện receive_message
    async def receive_message(self, event):
        await self.send(text_data=json.dumps({
            "event": "receive_message",
            "message": event["message"],
        }))