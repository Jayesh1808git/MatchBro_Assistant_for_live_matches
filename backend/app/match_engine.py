
from app.database import (
    save_event,
    get_all_events,
    get_recent_events,
    clear_events
)


MATCH_ID = "matchbro_demo_001"

BALL_FEED = [

    ("Rohit Sharma", "Mitchell Starc", "dot", 0, 0,
     "Starc beats Rohit with a good delivery."),

    ("Rohit Sharma", "Mitchell Starc", "single", 1, 0,
     "Rohit rotates the strike with a single."),

    ("Shubman Gill", "Mitchell Starc", "four", 4, 0,
     "Gill drives beautifully through the covers."),

    ("Shubman Gill", "Mitchell Starc", "dot", 0, 0,
     "Gill defends the next delivery."),

    ("Shubman Gill", "Mitchell Starc", "two", 2, 0,
     "Good running between the wickets."),

    ("Shubman Gill", "Mitchell Starc", "single", 1, 0,
     "Gill takes a single to end the over."),

    ("Rohit Sharma", "Pat Cummins", "dot", 0, 0,
     "Cummins starts with a dot ball."),

    ("Rohit Sharma", "Pat Cummins", "dot", 0, 0,
     "Another dot ball. Pressure building."),

    ("Rohit Sharma", "Pat Cummins", "single", 1, 0,
     "Rohit gets off strike."),

    ("Shubman Gill", "Pat Cummins", "four", 4, 0,
     "Gill finds the boundary."),

    ("Shubman Gill", "Pat Cummins", "dot", 0, 0,
     "A dot ball after the boundary."),

    ("Shubman Gill", "Pat Cummins", "wicket", 0, 1,
     "Gill is dismissed. A big breakthrough."),

    ("Virat Kohli", "Adam Zampa", "single", 1, 0,
     "Kohli gets off the mark."),

    ("Virat Kohli", "Adam Zampa", "dot", 0, 0,
     "Zampa beats Kohli's attempted sweep."),

    ("Virat Kohli", "Adam Zampa", "dot", 0, 0,
     "Another dot ball. Zampa building pressure."),

    ("Virat Kohli", "Adam Zampa", "two", 2, 0,
     "Kohli places the ball into the gap."),

    ("Virat Kohli", "Adam Zampa", "four", 4, 0,
     "Kohli finds the boundary."),

    ("Virat Kohli", "Adam Zampa", "dot", 0, 0,
     "A dot ball to finish the over.")
    
]


class MatchEngine:

    def __init__(self):

        self.reset()

    def reset(self):

        clear_events()

        self.feed_index = 0

        self.total_runs = 0

        self.total_wickets = 0

        self.legal_balls = 0

    def next_ball(self):

        if self.feed_index >= len(BALL_FEED):

            return {
                "finished": True,
                "message": "Demo match feed completed."
            }

        batter, bowler, outcome, runs, wicket, commentary = (
            BALL_FEED[self.feed_index]
        )

        self.legal_balls += 1

        self.total_runs += runs

        self.total_wickets += wicket

        over_number = (
            (self.legal_balls - 1) // 6
        )

        ball_number = (
            (self.legal_balls - 1) % 6
        ) + 1

        elapsed_seconds = self.legal_balls * 35

        event = {

            "match_id": MATCH_ID,

            "over_number": over_number,

            "ball_number": ball_number,

            "elapsed_seconds": elapsed_seconds,

            "timestamp": (
                f"{elapsed_seconds // 60:02d}:"
                f"{elapsed_seconds % 60:02d}"
            ),

            "batter": batter,

            "bowler": bowler,

            "outcome": outcome,

            "runs": runs,

            "wicket": wicket,

            "commentary": commentary

        }

        save_event(event)

        self.feed_index += 1

        return {
            "finished": False,
            "event": event,
            "state": self.get_state()
        }

    def get_state(self):

        events = get_all_events()

        run_rate = (
            self.total_runs / (self.legal_balls / 6)
            if self.legal_balls
            else 0
        )

        recent = get_recent_events(6)

        return {

            "match_id": MATCH_ID,

            "team1": "India",

            "team2": "Australia",

            "score": self.total_runs,

            "wickets": self.total_wickets,

            "overs": (
                f"{self.legal_balls // 6}."
                f"{self.legal_balls % 6}"
            ),

            "run_rate": round(run_rate, 2),

            "balls_bowled": self.legal_balls,

            "feed_progress": self.feed_index,

            "feed_length": len(BALL_FEED),

            "recent_events": recent,

            "total_events": len(events),

            "finished": (
                self.feed_index >= len(BALL_FEED)
            )

        }
