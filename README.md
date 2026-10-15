# Quick Quiz Generator

Open **index.html** in your browser, choose your inputs, and click **Generate
quizzes**. Everything runs in that single file, including the embedded music
artwork. It works offline with no server, installation, account, or external
libraries. Copy or share the HTML file on its own.

Choose addition, subtraction, multiplication, division, or music notes. Math
quizzes let you choose 1–4 digits separately for each operand. Subtraction may
produce negative answers. Division produces exact whole-number answers; the
second operand cannot have more digits than the first. Music supports treble,
bass, or mixed clefs and practices C, D, E, F, and G in two registers.

Each generated sheet contains four independently randomized quizzes with ten
questions each. Click **Print sheet** (or use your browser's print command) to
print the current sheet or save it as PDF. The controls are excluded from print.
The layout targets Letter paper; use your browser's fit-to-page setting for other
paper sizes, and disable browser headers/footers if needed.

## Archive

The previous Python version, README, image assets, and completed AWS teardown
configuration are preserved in `archive/python-version/`. The workflow is archived
there rather than active under `.github/workflows/`. AWS teardown completed on
October 15, 2026; the project resources and artifact/state bucket were deleted.
The shared hosted zone and domain registration were preserved. The archived
teardown cannot be rerun after the state bucket's deletion; never substitute
empty Terraform state.

The archived Python scripts can still be run from `archive/python-version/`
using the instructions in its README.

## Development check

Run `node --test tests/quiz.test.cjs` to verify arithmetic generation and music
staff placement. Node is only needed for this development check, not to use the
quiz generator.
