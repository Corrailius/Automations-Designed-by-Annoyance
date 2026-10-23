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
python main.py --keep-open          # wait for Enter before closing Firefox
```
`run.bat` does the same and forwards its arguments (`run.bat --mode news --limit 5`);
output goes to `build.log\ran.build.md` / `ran.error.md`.

`python main.py --mode business` runs every Business Skills category; the script returns to the category grid between categories.

On any failure a screenshot + HTML dump is saved in `build.log/`.

## Tuning (credentials.env or environment)
| Variable | Default | Meaning |
|---|---|---|
| GOOD_ANSWERS_PER_CYCLE / WRONG_ANSWERS_PER_CYCLE | 2 / 1 | right/wrong mix, shuffled per cycle (wrong=0 -> always right) |
| QUIZ_MINUTES_PER_10 | 5 | minutes spent per 10 announced minutes of quiz |
| MIN_THINK_SECONDS / MAX_THINK_SECONDS | 2 / 25 | clamp for the wait before each answer (max=0 disables waiting) |

## Layout
- `flows.py` – grammar / business / news loops, error recovery
- `quiz/` – `quiz_data` (BiDi capture), `quiz_runner` (loop), handlers, planner, pacing, `selectors.py`
- `navigation/` – menu + one module per skill
- `utils/` – in-page API client, debug snapshots
- `tests/` – `python -m pytest`

If 7Speaking changes its markup, `quiz/selectors.py` is the first place to look.
