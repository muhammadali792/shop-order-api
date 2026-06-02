import redis
import json
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def publish_order_event(event: str, data: dict):
    payload = json.dumps({"event": event, "data": data})
    redis_client.publish("order_events", payload)
