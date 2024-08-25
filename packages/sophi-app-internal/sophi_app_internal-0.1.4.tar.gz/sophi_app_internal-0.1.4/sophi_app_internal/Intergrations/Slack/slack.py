import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Slack:
    def __init__(self, token):
        self.client = WebClient(token=token)

    def get_user_name(self, user_id):
        try:
            result = self.client.users_info(user=user_id)
            return result["user"]["real_name"]
        except SlackApiError as e:
            print(f"Error getting user info: {e}")
            return user_id

    def fetch_thread_replies(self, channel_id, thread_ts):
        try:
            result = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
            return result["messages"][1:]
        except SlackApiError as e:
            print(f"Error fetching thread replies: {e}")
            return []

    def process_message(self, msg, is_reply=False, thread_ts=None):
        user_name = self.get_user_name(msg["user"])
        return {
            "type": "reply" if is_reply else "message",
            "user": user_name,
            "user_id": msg["user"],
            "text": msg["text"],
            "timestamp": msg["ts"],
            "thread_ts": thread_ts,
            "reactions": [
                {"name": reaction["name"], "count": reaction["count"]}
                for reaction in msg.get("reactions", [])
            ],
            "attachments": msg.get("attachments", []),
            "files": [
                {
                    "name": file.get("name"),
                    "filetype": file.get("filetype"),
                    "url_private": file.get("url_private")
                }
                for file in msg.get("files", [])
            ]
        }

    def channel_fetch_and_process_chunk(self, channel_id, oldest=None, latest=None, next_cursor=None, limit=1000):
        try:
            params = {
                "channel": channel_id,
                "limit": limit,
            }
            if oldest:
                params["oldest"] = oldest
            if latest:
                params["latest"] = latest
            if next_cursor:
                params["cursor"] = next_cursor

            result = self.client.conversations_history(**params)
            messages = result["messages"]
            processed_messages = []

            for msg in messages:
                processed_msg = self.process_message(msg)
                if "thread_ts" in msg and msg["thread_ts"] == msg["ts"]:
                    replies = self.fetch_thread_replies(channel_id, msg["ts"])
                    processed_msg["replies"] = [
                        self.process_message(reply, is_reply=True, thread_ts=msg["ts"])
                        for reply in replies
                    ]
                processed_messages.append(processed_msg)

            channel_info = self.client.conversations_info(channel=channel_id)["channel"]
            chunk_data = {
                "channel_id": channel_id,
                "channel_name": channel_info["name"],
                "is_private": channel_info["is_private"],
                "messages": processed_messages,
            }

            next_cursor = result["response_metadata"]["next_cursor"] if result["has_more"] else None

            return json.dumps(chunk_data, indent=2), next_cursor

        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return None, None

    def channel_fetch_and_process(self, channel_id, oldest=None, latest=None, limit=1000):
        try:
            all_messages = []
            next_cursor = None

            while True:
                params = {
                    "channel": channel_id,
                    "limit": limit,  # Slack allows up to 1000 messages per request
                }
                if oldest:
                    params["oldest"] = oldest
                if latest:
                    params["latest"] = latest
                if next_cursor:
                    params["cursor"] = next_cursor

                result = self.client.conversations_history(**params)
                messages = result["messages"]

                for msg in messages:
                    processed_msg = self.process_message(msg)

                    if "thread_ts" in msg and msg["thread_ts"] == msg["ts"]:
                        replies = self.fetch_thread_replies(channel_id, msg["ts"])
                        processed_msg["replies"] = [
                            self.process_message(reply, is_reply=True, thread_ts=msg["ts"])
                            for reply in replies
                        ]

                    all_messages.append(processed_msg)

                if not result["has_more"]:
                    break

                next_cursor = result["response_metadata"]["next_cursor"]

            all_messages.reverse()  # Chronological order

            channel_info = self.client.conversations_info(channel=channel_id)["channel"]
            output = {
                "channel_id": channel_id,
                "channel_name": channel_info["name"],
                "is_private": channel_info["is_private"],
                "messages": all_messages,
            }

            return json.dumps(output, indent=2)

        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return json.dumps({"error": str(e)})

    def get_all_channel_ids(self):
        try:
            channel_ids = []
            cursor = None
            while True:
                result = self.client.conversations_list(types="public_channel", cursor=cursor)
                channels = result["channels"]
                channel_ids.extend([channel["id"] for channel in channels])
                cursor = result["response_metadata"].get("next_cursor")
                if not cursor:
                    break
            return channel_ids
        except SlackApiError as e:
            print(f"Error fetching channel IDs: {e}")
            return []

    def get_all_dm_ids(self):
        try:
            dm_ids = []
            cursor = None
            while True:
                result = self.client.conversations_list(types="im", cursor=cursor)
                dms = result["channels"]
                dm_ids.extend([dm["id"] for dm in dms])
                cursor = result["response_metadata"].get("next_cursor")
                if not cursor:
                    break
            return dm_ids
        except SlackApiError as e:
            print(f"Error fetching DM IDs: {e}")
            return []
