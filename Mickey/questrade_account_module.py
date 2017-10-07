from datetime import datetime, timezone
import json


def time():
    value = datetime.now(timezone.utc).isoformat()
    json_resp = json.dumps({'time': value}, sort_keys=True, indent=4)
    return json_resp


def account():
    data = {"type": "Cash",
            "number": "12345678",
            "status": "Active",
            "isPrimary": True,
            "isBilling": True,
            "clientAccountType": "Individual"}
    json_resp = json.dumps(data, indent=4)
    return json_resp
