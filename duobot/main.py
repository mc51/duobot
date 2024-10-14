"""duobot"""

import logging
import sys
import time

import click

from duobot.api import Api
from duobot.sessions import Sessions


log = logging.getLogger("duobot")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@click.command()
@click.option(
    "-l",
    "--lessons",
    required=True,
    help="Number of lessons to solve.",
    type=click.INT,
)
@click.option("-d", "--debug", is_flag=True, help="Show debug messages.")
def cli(lessons: int, debug: bool):
    """Duobot is a complete command line automation for the Duolingo app.
    It travels the learning path of your active language course for you field by field.
    While doing so it solves lessons and stories, and opens chests.
    Moreover, it collects XP and gems, improves your league position, and keeps your streak alive.
    """
    if debug:
        log.setLevel(logging.DEBUG)
    start(lessons)


def start(lessons: int):
    """Start the bot.

    Args:
        lessons (int): number of lessons to solve
    """
    api = Api()
    session = Sessions()
    i = 0
    try:
        while i < lessons:
            i += 1
            log.info("Lesson %s of %s", i, lessons)
            status = api.fetch_user_status()
            log.info(
                "Doing course %s. Streak: %s. XP: %s",
                status["currentCourseId"],
                status["streak"],
                status["totalXp"],
            )
            course = api.fetch_current_course(course_id=status["currentCourseId"])
            lesson = session.get_next_lesson(course)
            session.solve_lesson(course, lesson)
            log.info("Finished lesson\n")
            time.sleep(2)
    except KeyboardInterrupt:
        log.error("\nAborted by user!\n")
        sys.exit(0)
    log.info("Finished all %s lessons.", lessons)
