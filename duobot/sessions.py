"""Sessions"""

import json
import logging
import random
from datetime import datetime, timezone
import time
from typing import Any, cast

from duobot.api import Api
from duobot.challenges import Challenges
from duobot.config import Config

log = logging.getLogger(__name__)


BATCH_URL_SESSION_COMPLETE = Config.BATCH_URL_SESSION_COMPLETE
URL_CHEST = Config.URL_CHEST
HEADERS = Config.HEADERS
API_TIMEOUT = Config.API_TIMEOUT
STORY_PAYLOAD = Config.STORY_PAYLOAD
BATCH_URL_STORY_COMPLETE = Config.BATCH_URL_STORY_COMPLETE
BATCH_URL_STATUS = Config.BATCH_URL_STATUS
URL_BATCH = Config.URL_BATCH
URL_BATCH_STORY = Config.URL_BATCH_STORY


class Sessions:
    """Sessions class"""

    api = Api()
    challenges = Challenges()

    def __init__(self):
        pass

    def create_batch_session_response(
        self, response: dict, session_id: str
    ) -> dict[str, Any]:
        """Create batch response for session.

        Args:
            response (dict): challenges
            session_id (str): session id

        Returns:
            dict[str, Any]: request
        """
        log.info("Creating batch session response")
        url = BATCH_URL_SESSION_COMPLETE.format(session_id=session_id)
        request = {"body": json.dumps(response), "method": "PUT", "url": url}
        return request

    def get_next_lesson(self, course: dict) -> dict:
        """Get next lesson for current course.

        Args:
            course (dict): current courses

        Returns:
            dict: next level
        """
        log.info("Getting next lesson")
        for unit in course["path"]:
            for i, level in enumerate(unit["levels"]):
                if level["state"] == "active":
                    level["levelIndex"] = i
                    level["levelSessionIndex"] = level["finishedSessions"]
                    log.info("Lesson name: %s", level["debugName"])
                    log.debug("Lesson: %s", level)
                    return level
        raise RuntimeError("No active levels found")

    def open_chest(self, course: dict, lesson: dict) -> None:
        """Open chest on path.

        Args:
            course (dict): lesson
            lesson (dict): lesson
        """
        log.info("Opening chest")
        rewards = self.api.fetch_rewards()
        chest_id = self.get_next_path_chest_id(rewards)
        payload = {}
        payload["consumed"] = True
        payload["pathLevelSpecifics"] = lesson["pathLevelMetadata"]
        payload["fromLanguage"] = course["fromLanguage"]
        payload["learningLanguage"] = course["learningLanguage"]
        url = URL_CHEST.format(chest_id=chest_id)
        self.api.fetch_chest(url, payload)

    def get_next_path_chest_id(self, rewards: dict) -> dict:
        """Get path chest from rewards.

        Args:
            rewards (dict): rewards

        Returns:
            dict: path chest
        """
        for reward in rewards["rewardBundles"]:
            if reward["rewardBundleType"] == "PATH_CHEST":
                return reward["rewards"][-1]["id"]
        raise RuntimeError("No path chest found")

    def create_fetch_session_payload(self, lesson: dict) -> dict:
        """Create session payload for given lesson.

        Args:
            lesson (dict): lesson

        Returns:
            dict: session
        """
        payload = Config.SESSION_PAYLOAD.copy()
        if lesson["type"] == "skill":
            payload["skillId"] = lesson["pathLevelMetadata"]["skillId"]
            payload["levelIndex"] = lesson["levelIndex"]
            if lesson["hasLevelReview"] and (
                lesson["totalSessions"] - lesson["finishedSessions"] == 1
            ):
                log.info("Doing level review lesson")
                payload["generatorIdentifiersOfRecentMistakes"] = []
                payload["type"] = "LEVEL_REVIEW"
            else:
                log.info("Doing normal lesson")
                payload["levelSessionIndex"] = lesson["levelSessionIndex"]
                payload["type"] = "LESSON"
        elif lesson["type"] == "practice":
            log.info("Doing practice session")
            payload["skillIds"] = lesson["pathLevelClientData"]["skillIds"]
            payload["levelSessionIndex"] = lesson["levelSessionIndex"]
            payload["lexemePracticeType"] = "practice_level"
            payload["type"] = "LEXEME_PRACTICE"
        elif lesson["type"] == "unit_review":
            log.info("Doing unit review lesson")
            payload["skillIds"] = [lesson["pathLevelMetadata"]["anchorSkillId"]]
            payload["type"] = lesson["type"].upper()
        return payload

    def solve_skill(self, lesson: dict) -> None:
        """Solve skill session.

        Args:
            lesson (dict): lesson
        """
        payload = self.create_fetch_session_payload(lesson=lesson)
        session = self.api.fetch_session(payload)
        response = self.challenges.create_session_solution_response(
            session=session, skill=lesson
        )
        batch_request = self.create_batch_session_response(response, session["id"])
        now = int(datetime.now(tz=timezone.utc).timestamp())
        endtime = response["endTime"]
        if now < endtime:
            waittime = endtime - now
            log.info("Waiting %s seconds before sending", waittime)
            time.sleep(waittime)
        self.api.send_batch_requests([batch_request], url=URL_BATCH)

    def solve_story(self, lesson: dict) -> None:
        """Solve story.

        Args:
            lesson (dict): story lesson
        """
        log.info("Solving story")
        story_id = lesson["pathLevelMetadata"]["storyId"]
        story = self.api.fetch_story(story_id)
        responses = self.create_batch_story_response(lesson, story)
        now = int(datetime.now(tz=timezone.utc).timestamp())
        endtime = json.loads(responses[0]["body"])["endTime"]
        if now < endtime:
            waittime = endtime - now
            log.info("Need to wait for %s seconds before sending", waittime)
            time.sleep(waittime)
        self.api.send_batch_requests(responses, url=URL_BATCH_STORY)

    def create_batch_story_response(self, lesson: dict, story: dict) -> list[dict]:
        """Create story response for batch request.

        Args:
            lesson (dict): lesson
            story (dict): story

        Returns:
            list[dict]: batch story response payload
        """
        log.info("Creating batch story response")
        payload = STORY_PAYLOAD.copy()
        # count number of challenges in story
        challenges = [
            e for e in story["elements"] if e["type"] not in ["HEADER", "LINE"]
        ]
        score = len(challenges) - 1
        payload["score"] = score
        payload["maxScore"] = score
        payload["pathLevelId"] = lesson["id"]
        payload["fromLanguage"] = story["fromLanguage"]
        payload["learningLanguage"] = story["learningLanguage"]
        payload["expectedXp"] = story["baseXp"]
        payload["startTime"] = story["startTime"]
        payload["endTime"] = cast(int, payload["startTime"]) + random.randint(3, 7)
        payload["pathLevelSpecifics"] = lesson["pathLevelMetadata"]
        log.info("Creating batch session response")
        url = BATCH_URL_STORY_COMPLETE.format(
            story_id=lesson["pathLevelMetadata"]["storyId"]
        )
        # we need at least two requests here, otherwise we get 500 response
        reqs = [
            {"body": json.dumps(payload), "method": "POST", "url": url},
            {"body": "", "method": "GET", "url": BATCH_URL_STATUS},
        ]
        log.debug("Batch story response: %s", reqs)
        return reqs

    def update_progress(self) -> None:
        """Update progress."""
        log.info("Updating progress")
        status = self.api.fetch_user_status()
        payload = {
            "metric_updates": [
                {"metric": "LESSONS", "quantity": 1},
                {"metric": "PERFECT_LESSONS", "quantity": 1},
                {"metric": "NINETY_ACCURACY_LESSONS", "quantity": 1},
                {"metric": "SPEAK_CHALLENGES", "quantity": 2},
                {"metric": "LISTEN_CHALLENGES", "quantity": 2},
                {"metric": "BEA", "quantity": 1},
                {"metric": "OSCAR", "quantity": 1},
                {"metric": "FALSTAFF", "quantity": 1},
                {"metric": "EDDY", "quantity": 1},
                {"metric": "LUCY", "quantity": 1},
                {"metric": "LILY", "quantity": 1},
                {"metric": "JUNIOR", "quantity": 1},
                {"metric": "LIN", "quantity": 1},
                # todo theres some more here we might need
            ],
            "timestamp": datetime.now(tz=timezone.utc).strftime(
                r"%Y-%m-%dT%H:%M:%S.%f"
            )[:-3]
            + "Z",  #  format: "2024-10-12T10:11:54.829Z",
            "timezone": status["timezone"],
        }
        self.api.post_progress_update(payload=payload)

    def solve_lesson(self, course: dict, lesson: dict) -> None:
        """Solve lesson.

        Args:
            course (dict): course
            lesson (dict): lesson

        """
        log.debug("Lesson type: %s", lesson["type"])
        if lesson["type"] in ["unit_review", "skill", "practice"]:
            log.info("Found a skill session on the path.")
            self.solve_skill(lesson)
            self.update_progress()
        elif lesson["type"] == "story":
            log.info("Found a story on the path.")
            self.solve_story(lesson)
        elif lesson["type"] == "chest":
            log.info("Found a chest on the path.")
            self.open_chest(course, lesson)
        else:
            raise RuntimeError("Unknown lesson type")
