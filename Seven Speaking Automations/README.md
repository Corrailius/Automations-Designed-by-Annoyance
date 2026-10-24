# Seven Speaking Automations (Selenium)

## Setup
```
pip install -r requirements.txt
copy credentials.env.example credentials.env   # then fill in email + password
```

## Run
```
python main.py                      # grammar -> business -> news lessons
python main.py --mode grammar       # one section only (grammar | business | news)
python main.py --mode news --limit 3
python main.py --duration 60       # run for 1 hour total, then stop cleanly
python main.py --perfect            # never answer wrong on purpose
python main.py --completed-weight 0 # do not replay completed lessons this run
python main.py --keep-open          # wait for Enter before closing Firefox
```
`run.bat` does the same and forwards its arguments (`run.bat --mode news --limit 5`);
output goes to `build.log\ran.build.md` / `ran.error.md`.

`python main.py --mode business` runs every Business Skills category; the script returns to the category grid between categories.

On any failure a screenshot + HTML dump is saved in `build.log/`.

## Tuning
Everything is tuned from `credentials.env` (a plain `.env` or real environment
variables work too). The values in effect are printed when the script starts.
`credentials.env.example` lists every variable with a comment.

| Variable | Default | Meaning |
|---|---|---|
| GOOD_ANSWERS_PER_CYCLE / WRONG_ANSWERS_PER_CYCLE | 2 / 0 | right/wrong mix, shuffled per cycle (wrong=0 -> always right) |
| COMPLETED_WEIGHT | 0.2 | how likely an already completed lesson is picked vs 1.0 for a new one (1 = no preference, 0 = never replay) |
| QUIZ_MINUTES_PER_10 | 5 | minutes spent per 10 announced minutes of quiz |
| MIN_THINK_SECONDS / MAX_THINK_SECONDS | 2 / 25 | clamp for the wait before each answer (max=0 disables waiting) |
| THINK_JITTER | 0.3 | random variation of each wait (0.3 = +/-30%) |
| PAUSE_MIN_SECONDS / PAUSE_MAX_SECONDS | 3 / 8 | pause between two news activities |
| API_DELAY_MIN_SECONDS / API_DELAY_MAX_SECONDS | 0.8 / 1.6 | delay between API calls when listing news topics |
| QUIZ_PAYLOAD_TIMEOUT | 5 | seconds to wait for the page's own quiz request before calling the API |
| MAX_CONSECUTIVE_FAILURES | 3 | stop a section after this many failures in a row |

### Completed lessons
Completed lessons are no longer skipped. They are replayed (all answers are given
again), but picked with weight `COMPLETED_WEIGHT` against 1.0 for new ones:
- Grammar: the play order is a weighted shuffle, new lessons tend to come first.
- News: each next activity is a weighted random pick from all activities.
- Business Skills: the cards show no completion marker, so every activity is
  played in page order, completed ones included.

`--completed-weight 0` on the command line overrides the variable for one run.

## Layout
- `flows.py` – grammar / business / news loops, error recovery
- `quiz/` – `quiz_data` (BiDi capture), `quiz_runner` (loop), handlers, planner, pacing, `selectors.py`
- `navigation/` – menu + one module per skill
- `utils/` – in-page API client, weighted ordering, debug snapshots
- `tests/` – `python -m pytest`

If 7Speaking changes its markup, `quiz/selectors.py` is the first place to look.
