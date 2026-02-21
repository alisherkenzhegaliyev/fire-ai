from datetime import datetime, timedelta, timezone
import jwt
from config import get_settings

class Token:
    @staticmethod
    def generate_and_sign(user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        payload = {"user_id": user_id, "exp": expire}
        return jwt.encode(payload, get_settings().SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
