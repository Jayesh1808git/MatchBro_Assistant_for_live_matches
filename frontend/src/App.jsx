
import { useEffect, useRef, useState } from "react";
import "./index.css";

const API = "http://127.0.0.1:8000";

const suggestions = [
  "What happened in the last over?",
  "Who scored the highest ODI score?",
  "Tell me something interesting about cricket.",
  "Why has the scoring slowed down?"
];

function App() {

  const [match, setMatch] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const [error, setError] = useState("");

  const recognitionRef = useRef(null);
  const timerRef = useRef(null);

  async function fetchMatch() {

    try {

      const response = await fetch(
        `${API}/api/match/state`
      );

      if (!response.ok) {
        throw new Error("Could not load match.");
      }

      const data = await response.json();

      setMatch(data);

    } catch (err) {

      setError(
        "Backend unavailable. Start FastAPI first."
      );

    }
  }

  async function fetchTimeline() {

    try {

      const response = await fetch(
        `${API}/api/match/timeline`
      );

      const data = await response.json();

      setTimeline(data.events || []);

    } catch (err) {

      console.error(err);

    }
  }

  useEffect(() => {

    fetchMatch();
    fetchTimeline();

    return () => {

      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      window.speechSynthesis?.cancel();

      recognitionRef.current?.abort();

    };

  }, []);

  async function nextBall() {

    setError("");

    try {

      const response = await fetch(
        `${API}/api/match/next-ball`,
        {
          method: "POST"
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not process ball.");
      }

      await fetchMatch();
      await fetchTimeline();

      if (data.finished) {
        setAutoPlay(false);
      }

    } catch (err) {

      setError(err.message);

    }
  }

  async function resetMatch() {

    stopAutoPlay();

    await fetch(
      `${API}/api/match/reset`,
      {
        method: "POST"
      }
    );

    setAnswer("");
    setSources([]);
    setError("");

    await fetchMatch();
    await fetchTimeline();

  }

  function startAutoPlay() {

    if (match?.finished) {
      setError("Reset the match before playing again.");
      return;
    }

    setAutoPlay(true);

    timerRef.current = setInterval(() => {

      nextBall();

    }, 2500);

  }

  function stopAutoPlay() {

    setAutoPlay(false);

    if (timerRef.current) {

      clearInterval(timerRef.current);

      timerRef.current = null;

    }

  }

  async function askMatchBro(customQuestion) {

    const userQuestion = (
      customQuestion ?? question
    ).trim();

    if (!userQuestion || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {

      const response = await fetch(
        `${API}/api/assistant/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            question: userQuestion
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Assistant failed.");
      }

      setAnswer(data.answer);
      setSources(data.historical_sources || []);

      speak(data.answer);

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }

  function speak(text) {

    if (!window.speechSynthesis) {
      setError("Speech output is not supported in this browser.");
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(
      text
    );

    utterance.lang = "en-IN";
    utterance.rate = 1;
    utterance.pitch = 1;

    utterance.onstart = () => {
      setSpeaking(true);
    };

    utterance.onend = () => {
      setSpeaking(false);
    };

    utterance.onerror = () => {
      setSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);

  }

  function stopSpeaking() {

    window.speechSynthesis.cancel();

    setSpeaking(false);

  }

  function startListening() {

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

      setError(
        "Voice recognition is unavailable. Try Chrome on desktop."
      );

      return;

    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.interimResults = false;

    recognition.continuous = false;

    recognitionRef.current = recognition;

    recognition.onstart = () => {

      setListening(true);

      setError("");

    };

    recognition.onresult = (event) => {

      const transcript =
        event.results[0][0].transcript;

      setQuestion(transcript);

      askMatchBro(transcript);

    };

    recognition.onerror = (event) => {

      setError(
        `Microphone error: ${event.error}`
      );

      setListening(false);

    };

    recognition.onend = () => {

      setListening(false);

    };

    recognition.start();

  }

  function formatTime(seconds) {

    const minutes = Math.floor(seconds / 60);

    const remaining = seconds % 60;

    return (
      `${String(minutes).padStart(2, "0")}:` +
      `${String(remaining).padStart(2, "0")}`
    );

  }

  const latestEvents = [...timeline].reverse().slice(0, 8);

  return (

    <div className="app">

      <header className="topbar">

        <div className="brand">
          <span className="brand-icon">🏏</span>

          <div>
            <h1>MatchBro</h1>
            <p>Your AI cricket companion</p>
          </div>
        </div>

        <span className="demo-badge">
          DEMO MATCH
        </span>

      </header>


      <main className="layout">

        <section className="main-column">

          <div className="match-card">

            <div className="match-heading">
              <span>INDIA vs AUSTRALIA</span>
              <span className="live-label">
                ● SIMULATED LIVE
              </span>
            </div>

            {match && (

              <>
                <div className="score-area">

                  <div className="team-score">

                    <div className="team-name">
                      🇮🇳 INDIA
                    </div>

                    <div className="score">
                      {match.score}/{match.wickets}
                    </div>

                    <div className="overs">
                      {match.overs} overs
                    </div>

                  </div>

                  <div className="vs">VS</div>

                  <div className="team-score opponent">

                    <div className="team-name">
                      🇦🇺 AUSTRALIA
                    </div>

                    <div className="score">
                      —
                    </div>

                    <div className="overs">
                      Batting second
                    </div>

                  </div>

                </div>

                <div className="stats-row">

                  <div>
                    <span>Run rate</span>
                    <strong>{match.run_rate}</strong>
                  </div>

                  <div>
                    <span>Balls bowled</span>
                    <strong>{match.balls_bowled}</strong>
                  </div>

                  <div>
                    <span>Feed progress</span>
                    <strong>
                      {match.feed_progress}/{match.feed_length}
                    </strong>
                  </div>

                </div>

              </>

            )}

            <div className="match-controls">

              <button
                className="primary-button"
                onClick={nextBall}
                disabled={match?.finished}
              >
                Next ball
              </button>

              {!autoPlay ? (

                <button
                  className="secondary-button"
                  onClick={startAutoPlay}
                  disabled={match?.finished}
                >
                  ▶ Auto play
                </button>

              ) : (

                <button
                  className="danger-button"
                  onClick={stopAutoPlay}
                >
                  Stop
                </button>

              )}

              <button
                className="secondary-button"
                onClick={resetMatch}
              >
                Reset
              </button>

            </div>

            {match?.finished && (
              <p className="finished-message">
                Demo feed completed. Reset to play again.
              </p>
            )}

          </div>


          <div className="assistant-card">

            <div className="section-heading">

              <div>
                <h2>Talk to MatchBro</h2>
                <p>Ask about the match or cricket history.</p>
              </div>

              <span className="ai-indicator">
                AI READY
              </span>

            </div>

            <div className="voice-area">

              <button
                className={`mic-button ${
                  listening ? "listening" : ""
                }`}
                onClick={startListening}
                disabled={loading}
                title="Speak to MatchBro"
              >
                {listening ? "🎙️" : "🎤"}
              </button>

              <div>
                <strong>
                  {listening
                    ? "Listening..."
                    : loading
                    ? "Thinking..."
                    : speaking
                    ? "Speaking..."
                    : "Tap the microphone"}
                </strong>

                <p>
                  {listening
                    ? "Ask your cricket question."
                    : "MatchBro will answer using live and historical context."}
                </p>
              </div>

            </div>

            <div className="question-input">

              <input
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={(event) => {

                  if (event.key === "Enter") {
                    askMatchBro();
                  }

                }}
                placeholder="Ask anything about cricket..."
              />

              <button
                onClick={() => askMatchBro()}
                disabled={loading}
              >
                {loading ? "..." : "Ask"}
              </button>

            </div>

            <div className="suggestions">

              <p>Try asking</p>

              {suggestions.map((item) => (

                <button
                  key={item}
                  onClick={() => {

                    setQuestion(item);

                    askMatchBro(item);

                  }}
                >
                  {item}
                </button>

              ))}

            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {answer && (

              <div className="answer-card">

                <div className="answer-heading">

                  <strong>🏏 MatchBro says</strong>

                  <button
                    onClick={() => speak(answer)}
                  >
                    🔊 Replay
                  </button>

                  <button
                    onClick={stopSpeaking}
                  >
                    ■ Stop
                  </button>

                </div>

                <p>{answer}</p>

                {sources.length > 0 && (

                  <div className="source-list">

                    <strong>Historical sources used</strong>

                    {sources.map((source) => (

                      <span key={source.title}>
                        {source.title}
                      </span>

                    ))}

                  </div>

                )}

              </div>

            )}

          </div>

        </section>


        <aside className="timeline-card">

          <div className="section-heading">
            <div>
              <h2>Match timeline</h2>
              <p>Recent ball-by-ball events</p>
            </div>
          </div>

          <div className="timeline-list">

            {latestEvents.length === 0 && (

              <p className="empty-state">
                Start the match to see events here.
              </p>

            )}

            {latestEvents.map((event) => (

              <div className="timeline-event" key={event.id}>

                <div className="event-time">
                  {formatTime(event.elapsed_seconds)}
                </div>

                <div className="event-detail">

                  <strong>
                    {event.over_number + 1}.{event.ball_number}
                    {" · "}
                    {event.outcome.toUpperCase()}
                  </strong>

                  <p>{event.commentary}</p>

                  <span>
                    {event.batter} vs {event.bowler}
                  </span>

                </div>

              </div>

            ))}

          </div>

          <button
            className="secondary-button full-width"
            onClick={fetchTimeline}
          >
            Refresh timeline
          </button>

          <div className="boredom-card">
            <span>💡</span>

            <strong>
              {match?.slow_period
                ? "Slow over detected!"
                : "Explore cricket while watching"}
            </strong>

            <p>
              {match?.slow_period
                ? "The scoring has slowed down. Want an interesting cricket story?"
                : "Discover historical records, famous matches and player stories."}
            </p>

            <button
              className="secondary-button"
              onClick={() =>
                askMatchBro(
                  match?.slow_period
                    ? "Tell me an interesting historical cricket story to make this slow period more entertaining."
                    : "Tell me an interesting cricket fact."
                )
              }
            >
              {match?.slow_period
                ? "Entertain me 🏏"
                : "Discover cricket facts"}
            </button>
          </div>

        </aside>

      </main>

      <footer>
        MatchBro AI · A simulated cricket experience
      </footer>

    </div>

  );

}

export default App;
