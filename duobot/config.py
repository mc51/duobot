"""Configuration"""

import os
from dataclasses import dataclass

import dotenv

dotenv.load_dotenv()


@dataclass
class Config:
    """Config class"""

    USER_ID = os.environ.get("DUO_USERID")
    AUTH = os.environ.get("DUO_AUTH")  # 'Bearer eyJ123xyz'

    if USER_ID is None or AUTH is None:
        raise RuntimeError("Please set DUO_USERID and DUO_AUTH environment variables")

    USER_AGENT = (
        "Duodroid/5.84.3 Dalvik/2.1.0 (Linux; U; Android 13;"
        "sdk_gphone_x86_64 Build/TE1A.220922.034)"
    )
    HEADERS = {
        "User-Agent": USER_AGENT,
        "X-Amzn-Trace-Id": f"User={USER_ID}",
        "Authorization": AUTH,
    }

    API_TIMEOUT = 10
    BASE_HOST = "https://android-api-cf.duolingo.com"
    BASE_VERSION = "/2017-06-30/"
    BASE_URL = f"{BASE_HOST}{BASE_VERSION}"

    DELAY_BETWEEN_ANSWERS = 6000  # in ms

    # POST
    URL_LOGIN = f"{BASE_URL}login?fields=id"
    URL_SESSIONS = (
        f"{BASE_URL}sessions?fields=askPriorProficiency%2Cbeginner%2CchallengeTimeTakenCutoff"
        "%2CcheckpointIndex%2Cexplanation%7Btitle%2Curl%2Cintro%7D%2CfromLanguage%2ChardModeLevelIndex"
        "%2Cid%2CisV2%2ClearningLanguage%2ClevelIndex%2ClevelSessionIndex%2Cmetadata%2CskillId%2C"
        "trackingProperties%2Ctype%2Cchallenges%2CadaptiveChallenges%2CadaptiveInterleavedChallenges"
        "%7Bchallenges%2CspeakOrListenReplacementIndices%7D%2CsessionStartExperiments%2CspeechConfig"
        "%7BauthorizationToken%2Cregion%2CvalidDuration%7D%2CttsAnnotations"
    )
    URL_BATCH = f"{BASE_URL}batch?fields=responses%7Bbody%2Cstatus%2Cheaders%7D"
    URL_BATCH_STORY = (
        f"{BASE_URL}batch-story-complete?fields=responses%7Bbody%2Cstatus%2Cheaders%7D"
    )
    URL_PROGRESS = f"https://goals-api.duolingo.com/users/{USER_ID}/progress/batch"
    # GET
    BASE_USER_URL = f"{BASE_URL}users/{USER_ID}"
    URL_COURSE = (
        f"{BASE_USER_URL}/courses/"
        "{course_id}?fields=authorId%2CfromLanguage"
        "%2Cid%2ChealthEnabled%2ClearningLanguage%2Cxp%2Ccrowns%2CcheckpointTests%2ClessonsDone"
        "%2CplacementTestAvailable%2CpracticesDone%2CprogressQuizHistory%7BstartTime%2CendTime"
        "%2Cscore%7D%2CtrackingProperties%2Csections%7Bname%2CnumRows%2CcheckpointAccessible"
        "%2CcheckpointFinished%2CcheckpointSessionType%2Csummary%2CcefrLevel%7D%2Cskills"
        "%7Baccessible%2Cbonus%2Cdecayed%2Cexplanation%7Btitle%2Curl%2Cintro%7D%2ChasFinalLevel"
        "%2CfinishedLessons%2CfinishedLevels%2Cgrammar%2ChasLevelReview%2CiconId%2Cid"
        "%2ClastLessonPerfect%2Clessons%2Clevels%2Cname%2CshortName%2CskillType%2CindicatingNewContent"
        "%7D%2CsmartTips%7BsmartTipId%2Curl%7D%2CfinalCheckpointSession%2Cstatus%2Cpath"
        "%2CwordsLearned%2CpathDetails%7Bnotifications%7Bid%7D%7D"
    )
    URL_STATUS = f"{BASE_USER_URL}?fields=totalXp%2CcurrentCourseId%2Cstreak%2Ctimezone"
    URL_REWARDS = f"{BASE_USER_URL}?fields=rewardBundles"
    URL_STORY = (
        "https://stories.duolingo.com/api2/stories/{story_id}?illustrationFormat=svg&"
        "supportedElements=HEADER%2CLINE%2CCHALLENGE_PROMPT%2CSELECT_PHRASE%2CMULTIPLE_CHOICE%2C"
        "POINT_TO_PHRASE%2CARRANGE%2CMATCH%2CHINT_ONBOARDING%2CFREEFORM_WRITING%2C"
        "FREEFORM_WRITING_EXAMPLE_RESPONSE%2CFREEFORM_WRITING_PROMPT&masterVersion=false&"
        "debugSkipFinalMatchChallenge=false"
    )
    # PATCH
    URL_CHEST = f"{BASE_USER_URL}" + "/rewards/{chest_id}?fields="

    # Batch urls
    BATCH_URL_STORY_COMPLETE = "/api2/stories/{story_id}/complete"
    BATCH_URL_SESSION_COMPLETE = (
        BASE_VERSION + "sessions/{session_id}?fields=trackingProperties"
    )
    BATCH_URL_STATUS = f"{BASE_VERSION}users/{USER_ID}"

    STORY_PAYLOAD = {
        "awardXp": True,
        "maxScore": None,
        "score": None,
        "numHintsUsed": 0,
        "startTime": None,
        "endTime": None,
        "illustrationFormat": "svg",
        "pathLevelSpecifics": None,
        "pathLevelId": None,
        "learningLanguage": None,
        "fromLanguage": None,
        "isV2Redo": False,
        "happyHourBonusXp": 0,
        "expectedXp": None,
        "offlineTrackingProperties": {
            "offline": False,
            "offlined_session": False,
            "is_zombie_mode": False,
        },
    }

    SESSION_PAYLOAD = {
        "challengeTypes": [
            "assist",
            "characterIntro",
            "characterMatch",
            "characterPuzzle",
            "characterSelect",
            "characterTrace",
            "characterTraceFreehand",
            "characterTraceFreehandIntro",
            "characterTraceFreehandPartialRecall",
            "characterTraceFreehandRecall",
            "completeReverseTranslation",
            "definition",
            "dialogue",
            "dialogueSelectSpeak",
            "drillSpeak",
            "form",
            "freeResponse",
            "gapFill",
            "judge",
            "listen",
            "listenComplete",
            "listenComprehension",
            "listenIsolation",
            "listenMatch",
            "listenSpeak",
            "listenTap",
            "match",
            "name",
            "partialListen",
            "partialReverseTranslate",
            "patternTapComplete",
            "readComprehension",
            "select",
            "selectPronunciation",
            "selectTranscription",
            "selectMinimalPairs",
            "speak",
            "syllableTap",
            "syllableListenTap",
            "tapCloze",
            "tapClozeTable",
            "tapComplete",
            "tapCompleteTable",
            "tapDescribe",
            "translate",
            "typeCloze",
            "typeClozeTable",
            "typeCompleteTable",
            "writeComplete",
            "writeWordBank",
        ],
        "fromLanguage": "en",
        "isV2": True,
        "learningLanguage": "de",
        "forceChallengeTypes": False,
        "isHarderPractice": False,
        "isFirstLesson": False,
        "smartTipsVersion": 2,
        "zhTw": False,
        "isResurrectedShorterLesson": False,
    }
