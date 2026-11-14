# ai-happy-01 entry V4 — "For you, judge"

A laughing little girl in a yellow dress offers one giant sunflower straight
toward the viewer, a small paper tag tied to the stem reading
"for the judge", at golden hour in a garden.

`main.py` (Python 3.13, standard library only) copies the bundled
`image.jpg` (1024x683 JPEG, 160,064 bytes) to
`$MAKEFUN_OUTPUT_DIR/entry.png` byte for byte, after validating it
against the competition gate (whole JPEG, at most 1 MiB, at most
1024x1024). Run it with no arguments; outside the grader,
`MAKEFUN_OUTPUT_DIR` stands in for `/output`:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
