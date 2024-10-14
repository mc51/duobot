"""API"""

import json
import logging

import requests

from duobot.config import Config

log = logging.getLogger(__name__)

URL_COURSE = Config.URL_COURSE
HEADERS = Config.HEADERS
API_TIMEOUT = Config.API_TIMEOUT
URL_REWARDS = Config.URL_REWARDS
SESSION_PAYLOAD = Config.SESSION_PAYLOAD
URL_SESSIONS = Config.URL_SESSIONS
URL_STATUS = Config.URL_STATUS
URL_BATCH = Config.URL_BATCH
URL_BATCH_STORY = Config.URL_BATCH_STORY
URL_STORY = Config.URL_STORY
URL_PROGRESS = Config.URL_PROGRESS


class Api:
    """Api class."""

    def __init__(self):
        pass

    def send_request(self, method: str, url: str, payload: dict | None = None) -> dict:
        """Send request to api.

        Args:
            method (str): method
            url (str): url
            payload (dict | None): payload

        Returns:
            dict: response
        """
        log.debug("Sending request to %s", url)
        log.debug("Payload: %s", payload)
        try:
            response = requests.request(
                method, url, json=payload, headers=HEADERS, timeout=API_TIMEOUT
            )
            response.raise_for_status()
        except (requests.exceptions.HTTPError, json.JSONDecodeError):
            log.exception("Error sending request. Response: %s", response.text)
            raise
        log.debug("Response: %s", response.text)
        return response.json()

    def fetch_current_course(self, course_id: str) -> dict:
        """Fetch current course.

        Args:
            course_id (str): course_id

        Returns:
            dict: courses
        """
        log.info("Getting current courses")
        return self.send_request(
            method="get", url=URL_COURSE.format(course_id=course_id)
        )

    def fetch_rewards(self) -> dict:
        """Fetch rewards.

        Returns:
            dict: rewards
        """
        log.info("Getting rewards")
        return self.send_request(method="get", url=URL_REWARDS)

    def fetch_session(self, payload: dict) -> dict:
        """Fetch session.

        Args:
            payload (dict): payload

        Returns:
            dict: session
        """
        return self.send_request(method="post", url=URL_SESSIONS, payload=payload)

    def fetch_user_status(self) -> dict:
        """Fetch user status."

        Returns:
            dict: user status
        """
        log.info("Getting user status")
        return self.send_request(method="get", url=URL_STATUS)

    def send_batch_requests(self, reqs: list[dict], url: str) -> dict:
        """Send requests as batch.

        Args:
            reqs (list[dict]): requests
            url (str): url

        Returns:
            dict: response
        """
        payload = {
            "requests": reqs,
            "includeHeaders": False,
        }
        return self.send_request(method="post", url=url, payload=payload)

    def fetch_story(self, story_id: str) -> dict:
        """Fetch story.

        Args:
            story_id (str): story_id

        Returns:
            dict: story
        """
        log.info("Fetching story")
        url = URL_STORY.format(story_id=story_id)
        return self.send_request(method="get", url=url)

    def fetch_chest(self, url: str, payload: dict) -> dict:
        """Fetch chest.

        Args:
            url (str): url
            payload (dict): payload

        Returns:
            dict: response
        """
        log.info("Fetching chest")
        return self.send_request(method="patch", url=url, payload=payload)

    def post_progress_update(self, payload: dict) -> dict:
        """Post progress update.

        Args:
            payload (dict): payload

        Returns:
            dict: response
        """
        return self.send_request(method="post", url=URL_PROGRESS, payload=payload)
