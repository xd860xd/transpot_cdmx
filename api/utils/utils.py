import json
from datetime import timedelta

import jwt
import requests
from django.conf import settings
from django.utils import timezone

from api.utils.exceptions import BadGateWay


def get_district_info_token(district, token_type="data_units"):
    """Create JWT token"""
    exp_date = timezone.now() + timedelta(days=settings.JWT_TOKEN_EXP_DAYS)
    payload = {
        "exp": int(exp_date.timestamp()),
        "token_type": token_type,
        "district": district,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def do_request(url):
    try:
        resp = requests.get(url)
        result = json.loads(resp._content.decode())
        assert resp.status_code == 200
    except Exception:
        raise BadGateWay()
    return result
