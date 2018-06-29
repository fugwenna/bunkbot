from discord import Message

"""
Wrapper to alert users to streamers
"""
class StreamAlert:
    def __init__(self, stream_name: str, message: Message = None):
        self.stream_name = stream_name
        self.message = message


class StreamAlertCollection:
    def __init__(self):
        self.stream_alerts: list = []


    def get(self, stream: str) -> StreamAlert:
        try:
            return [s for s in self.stream_alerts if s.stream_name == stream][0]
        except Exception:
            return StreamAlert(stream)


    def add(self, alert: StreamAlert):
        msg = [s for s in self.stream_alerts if s.stream_name == alert.stream_name]
        if len(msg) == 0:
            self.stream_alerts.append(alert)