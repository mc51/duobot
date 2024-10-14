"""Challenges"""

from datetime import datetime, timezone
import logging
import random
import re
from typing import Any

log = logging.getLogger(__name__)


class Challenges:
    """Challenges class"""

    def __init__(self):
        pass

    def extract_answers_from_challenge(self, challenge: dict) -> tuple:
        """Extract correct and wrong answer from challenge.

        Args:
            challenge (dict): challenge

        Returns:
            tuple: correct and wrong answers
        """
        log.info("Challenge type: %s", challenge_type := challenge.get("type"))
        challenges_without_choices = ["match", "listenMatch", "speak"]
        if challenge_type in challenges_without_choices:
            log.info("Challenge without choices. Skipping answer extraction.")
            return (None, [])

        if wrong := challenge.get("wrongTokens", []):
            correct = challenge.get("correctTokens", [])

        idx = [challenge.get("correctIndex")]
        if idx[0] is None:
            idx = challenge.get("correctIndices", [])

        if choices := challenge["choices"]:
            log.info("idx: %s", idx)
            log.info("choices: %s", choices)
            choices_correct = [choices[i] for i in idx]
            choices_wrong = [c for c in choices if c not in choices_correct]
            log.debug("Correct choices: %s", choices_correct)
            log.debug("Wrong choices: %s", choices_wrong)
            if isinstance(choices[0], str):
                correct = choices_correct
                wrong = choices_wrong
            elif choices[0].get("phrase"):
                correct = [e["phrase"] for e in choices_correct]
                wrong = [e["phrase"] for e in choices_wrong]
            else:
                correct = [e["text"] for e in choices_correct]
                wrong = [e["text"] for e in choices_wrong]
        return (" ".join(correct) + " ", wrong)

    def extract_characters_from_challenge(self, challenge: dict) -> list[str]:
        """Extract characters from challenge.

        Args:
            challenge (dict): challenge

        Returns:
            list[str]: characters
        """
        name = challenge.get("character", {}).get("name")
        if name:
            return [name.lower()]
        return []

    def clean_character(self, session: dict) -> None:
        """Clean character from session.

        Args:
            session (dict): session
        """
        log.debug("Cleaning character")
        keep = ["correctAnimation", "idleAnimation", "incorrectAnimation"]
        for challenge in session["challenges"]:
            if challenge.get("character"):
                for key in list(challenge["character"].keys()):
                    if key not in keep:
                        del challenge["character"][key]

    def get_correct_guess(self, session: dict) -> None:
        """Get correct guess.
        For some challenge types it's the index of the correct solution.
        For others, it's the written solution.
        For others, it's in the metadata.

        Args:
            session (dict): session
        """
        log.debug("Getting correct guess")
        no_guess_types = ["tapComplete"]
        for challenge in session["challenges"]:
            if challenge.get("type") in no_guess_types:
                challenge["guess"] = None
            elif (guess := challenge.get("correctIndex")) is not None:
                challenge["guess"] = guess
            elif (solution := challenge.get("correctSolutions")) is not None:
                solution = self.parse_solution(solution[0])
                challenge["guess"] = solution
            elif (
                solution := challenge.get("metadata")
                .get("challenge_construction_insights", {})
                .get("best_solution")
            ) is not None:
                solution = self.parse_solution(solution)
                challenge["guess"] = solution
            else:
                challenge["guess"] = None

    def parse_solution(self, solution: str) -> str:
        """Parse solution. Remove every non letter and non whitespace char
            and add a whitespace at the end.

        Args:
            solution (str): solution

        Returns:
            str: parsed solution
        """
        return re.sub(r"[^\w|\s]+", "", solution) + " "

    def remove_unneeded_challenge_keys(self, session: dict) -> None:
        """Remove unneeded keys from session challenges.

        Args:
            session (dict): session
        """
        log.debug("Removing unneeded keys")
        remove_root_key = [
            "compactTranslations",
            "correctTokens",
            "grader",
            "isSpeakerUniversal",
            "taggedKcIds",
            "tts",
            "weakWordPromptRanges",
            "wrongTokens",
        ]
        no_new_words = ["listenTap", "assist", "match"]
        for challenge in session["challenges"]:
            for key in remove_root_key:
                if key in challenge:
                    del challenge[key]
            if "pdf" in challenge.get("image", {}):
                del challenge["image"]["pdf"]
            if "choices" in challenge and isinstance(challenge["choices"], list):
                for choice in challenge["choices"]:
                    if "image" in choice:
                        del choice["image"]
            if challenge.get("type") == "assist":
                del challenge["choices"]
            if challenge.get("type") in no_new_words:
                del challenge["newWords"]

    def has_challenge_type(self, session: dict, ctype: str) -> bool:
        """Check if session has challenge type.

        Args:
            session (dict): session
            ctype (str): challenge type

        Returns:
            bool: has challenge type
        """
        for challenge in session["challenges"]:
            if challenge["type"] == ctype:
                return True
        return False

    def count_challenge_type(self, session: dict, ctype: str) -> int:
        """Count challenge type in session.

        Args:
            session (dict): session
            ctype (str): challenge type

        Returns:
            int: number of challenge types
        """
        count = 0
        for challenge in session["challenges"]:
            if challenge["type"] == ctype:
                count += 1
        return count

    def get_num_characters_shown(self, session: dict) -> int:
        """Get number of characters shown in session.

        Args:
            session (dict): session

        Returns:
            int: number of characters shown
        """
        num = 0
        for challenge in session["challenges"]:
            if challenge.get("character"):
                num += 1
        return num

    def create_tracking_properties(self, session: dict) -> dict:
        """Create tracking properties for session.

        Args:
            session (dict): session

        Returns:
            dict: tracking properties
        """
        # it seems that the variables are missing if no such challenge was posed
        properties: dict[str, Any] = {}
        properties["contained_adaptive_challenge"] = False
        properties["contained_listen_challenge"] = False
        properties["contained_listen_speak_challenge"] = False
        properties["contained_speak_challenge"] = False

        if (
            session["trackingProperties"].get("num_adaptive_challenges_generated", 0)
            > 0
        ):
            properties["contained_adaptive_challenge"] = True
        if session["trackingProperties"].get("num_challenges_gt_listen_tap", 0) > 0:
            properties["contained_listen_challenge"] = True
        if self.has_challenge_type(session, "listenSpeak"):
            properties["contained_listen_speak_challenge"] = True
        if self.has_challenge_type(session, "speak"):
            properties["contained_speak_challenge"] = True

        properties["disabled_listen_challenges"] = False
        properties["disabled_listen_speak_challenges"] = False
        properties["disabled_speak_challenges"] = False
        properties["is_zombie_mode"] = False
        properties["num_adaptive_challenges"] = 0
        properties["num_characters_shown"] = self.get_num_characters_shown(session)
        properties["num_explanation_opens"] = 0
        properties["num_mistakes_completed"] = 0
        properties["num_mistakes_generated"] = 0
        properties["num_times_transliteration_toggled"] = 0
        properties["offlined_session"] = False
        properties["speak_count"] = self.count_challenge_type(session, "speak")
        properties["speak_ineligible"] = False
        properties["sum_hints_used"] = 0
        properties["transliteration_setting"] = "null"
        return properties

    def create_session_solution_response(self, session: dict, skill: dict) -> dict:
        """Create session solution response.

        Args:
            session (dict): session
            skill (dict): skill infos

        Returns:
            dict: response
        """
        ts_start = int(datetime.now(tz=timezone.utc).timestamp())
        total_time = 0
        log.info("Creating final responses.")

        for challenge in session["challenges"]:
            challenge.pop("progressUpdates")
            challenge["correct"] = True
            challenge["numHintsTapped"] = 0
            challenge["wasIndicatorShown"] = False
            challenge["timeTaken"] = (time_taken := random.randint(800, 1500))
            challenge["highlights"] = []
            total_time += int(time_taken / 1000)
        ts_end = ts_start + total_time

        self.clean_character(session)
        self.remove_unneeded_challenge_keys(session)
        self.get_correct_guess(session)

        missing_keys = {
            "askPriorProficiency": False,
            "beginner": False,
            "containsPastUserMistakes": False,
            "enableBonusPoints": True,
            "endTime": ts_end,
            "failed": False,
            "happyHourBonusXp": 0,
            "hasBoost": False,
            "isCuratedPlacementTest": False,
            "isHarderPractice": False,
            "isMistakesGlobalPractice": False,
            "isSkillRestoreSession": False,
            "learnerSpeechStoreSessionInfo": [],
            "maxInLessonStreak": 15,
            "offline": False,
            "pathLevelId": skill["id"],
            "pathLevelSpecifics": skill["pathLevelMetadata"],
            "shouldLearnThings": True,
            "startTime": ts_start,
        }
        obsolete = [
            "adaptiveInterleavedChallenges",
            "experiments_with_treatment_contexts",
            "explanations",
            "lessonIndex",
            "mistakesReplacementChallenges",
            "progressUpdates",
            "sessionExperimentRecord",
            "sessionStartExperiments",
            "showBestTranslationInGradingRibbon",
            "ttsAnnotations",
        ]
        for key in obsolete:
            if key in session:
                session.pop(key)
        session.update(missing_keys)
        missing_tracking_properties = self.create_tracking_properties(session)
        session["trackingProperties"].update(missing_tracking_properties)
        return session
