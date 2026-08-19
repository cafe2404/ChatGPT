from curl_cffi  import requests
from ..logger   import Log
from ..runtime  import Utils


class IP_Info:
    @staticmethod
    def fetch_info(session: requests.session.Session) -> list:
        response = session.get(
            "https://ipinfo.io/json",
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        loc = data.get("loc", "0,0").split(",")
        return [
            data.get("ip"),
            data.get("city"),
            data.get("region"),
            float(loc[0]),
            float(loc[1]),
            data.get("timezone"),
        ]