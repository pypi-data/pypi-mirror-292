import json
import time

import requests
from pydantic import BaseModel


class SaldorClient:
    def __init__(self, api_key: str, base_url="https://api.saldor.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"APIKey {api_key}"}

    def _handle_response(self, response: requests.Response) -> dict:
        # Check if the request was successful
        if response.status_code == 200:
            # Assuming the response contains a JSON array of strings
            return response.json()["data"]
        else:
            # Handle error appropriately
            response.raise_for_status()
            return {}

    def wait_for_crawl(
        self, crawl_id: str, timeout_ms: int = 5000, interval_ms: int = 1000
    ) -> list[str]:
        start_time = time.time()
        while timeout_ms == 0 or time.time() - start_time < timeout_ms:
            response = requests.get(
                f"{self.base_url}/crawl/{crawl_id}", headers=self.headers
            )
            get_result = self._handle_response(response)
            if get_result["state"] == "completed":
                return get_result["result"]
            if get_result["state"] == "failed":
                raise Exception("Scrape failed")
            if get_result["state"] == "cancelled":
                raise Exception("Scrape cancelled")
            time.sleep(interval_ms / 1000)
        raise Exception("Scrape timed out")

    def scrape(self, url: str, goal: str = "") -> list[str]:
        payload = {"url": url, "goal": goal, "max_pages": 1, "max_depth": 0}

        # Use the base_url variable
        response = requests.post(
            f"{self.base_url}/crawl", json=payload, headers=self.headers
        )
        result = self._handle_response(response)

        return self.wait_for_crawl(result["id"])

    def crawl(
        self,
        url: str,
        goal="",
        max_pages="1",
        max_depth="0",
        children_paths: list[str] = [],
        json_schema: BaseModel | None = None,
    ) -> list[str]:
        result = self.crawl_async(
            url, goal, max_pages, max_depth, children_paths, json_schema
        )

        return self.wait_for_crawl(result["id"], timeout_ms=0)

    def crawl_async(
        self,
        url: str,
        goal="",
        max_pages="1",
        max_depth="0",
        children_paths: list[str] = [],
        json_schema: BaseModel | None = None,
    ) -> dict:
        payload = {
            "url": url,
            "goal": goal,
            "max_pages": max_pages,
            "max_depth": max_depth,
            "json_schema": json.dumps(json_schema.model_json_schema())
            if json_schema
            else None,
            "children_paths": children_paths,
        }

        response = requests.post(
            f"{self.base_url}/crawl",
            json=payload,
            headers=self.headers,
        )

        return self._handle_response(response)

    def get_crawl(self, crawl_id: str):
        response = requests.get(
            f"{self.base_url}/crawl/{crawl_id}",
            headers=self.headers,
        )

        return self._handle_response(response)

    def list_crawls(self, state: str = ""):
        response = requests.get(
            f"{self.base_url}/crawl/", json={"state": state}, headers=self.headers
        )
        return self._handle_response(response)
