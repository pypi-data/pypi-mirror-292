import time
import requests
from typing import Dict, List, Union

class AuthKit:
    def __init__(self, secret: str, configs: Dict = None):
        self.secret = secret
        self.configs = configs or {}
        self.environment = "live" if "sk_live_" in secret else "test"

    def _get_url(self, type: str) -> str:
        services_url = self.configs.get("base_url", "https://api.integrationos.com")

        urls = {
            "get_settings": f"{services_url}/internal/v1/settings/get",
            "create_event_link": f"{services_url}/internal/v1/event-links/create",
            "get_connection_definitions": f"{services_url}/v1/public/connection-definitions?limit=100",
            "create_embed_token": f"{services_url}/internal/v1/embed-tokens/create",
            "get_session_id": f"{services_url}/v1/public/generate-id/session_id",
        }
        return urls[type]

    def _get_headers(self, type: str = "buildable") -> Dict[str, str]:
        if type == "buildable":
            return {
                "X-Buildable-Secret": self.secret,
                "Content-Type": "application/json",
            }
        elif type == "ios_secret":
            return {
                "x-integrationos-secret": self.secret
            }

    def _api_call(self, method_type: str, url: str, payload: Dict = None, headers: Dict = None) -> Dict:
        kwargs = {}
        if payload:
            kwargs['json'] = payload
        if headers:
            kwargs['headers'] = headers

        response = requests.request(method_type, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def _get_settings(self) -> Dict:
        return self._api_call("POST", self._get_url("get_settings"), headers=self._get_headers())

    def _create_event_link(self, payload: Dict) -> Dict:
        payload["environment"] = "test" if self.secret.startswith("sk_test") else "live"
        payload["usageSource"] = "sdk"
        return self._api_call("POST", self._get_url("create_event_link"), payload, self._get_headers())

    def _get_connection_definitions(self) -> Dict:
        return self._api_call("GET", self._get_url("get_connection_definitions"), headers=self._get_headers("ios_secret"))

    def _get_session_id(self) -> Dict:
        return self._api_call("GET", self._get_url("get_session_id"))

    def _create_embed_token(self, connected_platforms: List, event_links: Dict, settings: Dict) -> Dict:
        token_payload = {
            "linkSettings": {
                "connectedPlatforms": connected_platforms,
                "eventIncToken": event_links["token"]
            },
            "group": event_links["group"],
            "label": event_links["label"],
            "environment": "test" if self.secret.startswith("sk_test") else "live",
            "expiresAt": int(time.time() * 1000) + (5 * 1000 * 60),
            "sessionId": self._get_session_id()['id'],
            "features": settings["features"]
        }
        return self._api_call("POST", self._get_url("create_embed_token"), token_payload, self._get_headers())

    def create(self, payload: Dict) -> Union[Dict, str]:
        try:
            settings = self._get_settings()
            event_link = self._create_event_link(payload)
            connection_definitions = self._get_connection_definitions()

            active_connection_definitions = [cd for cd in connection_definitions.get("rows", []) if cd.get("active")]
            connected_platforms = [
                platform for platform in settings.get("connectedPlatforms", [])
                if platform.get("connectionDefinitionId") in [cd.get("_id") for cd in active_connection_definitions]
                and platform.get("active")
                and (
                    self.environment == "live"
                    and platform.get("environment") == "live"
                    or self.environment == "test"
                    and (platform.get("environment") == "test" or "environment" not in platform)
                )
            ]

            return self._create_embed_token(connected_platforms, event_link, settings)
        except requests.RequestException as e:
            return {"message": str(e)}