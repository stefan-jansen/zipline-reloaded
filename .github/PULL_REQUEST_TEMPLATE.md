## Problem and scope

Follow the [contribution requirements](https://github.com/stefan-jansen/zipline-reloaded/blob/main/CONTRIBUTING.rst). Describe one problem
and how this change addresses it. Keep unrelated fixes, refactors and formatting
separate. Zipline Reloaded accepts maintenance fixes and improvements to existing
documentation; direct new feature work to current ML4T libraries.

Link the owning issue with a closing reference such as `Closes #123`. Automated
dependency updates and administrative metadata changes do not require a separate
issue; explain when that exception applies.

## Verification

For a bug fix, provide a regression through the affected public API or user
workflow that fails because of the defect on the relevant base and passes with
the fix. Tests of copied logic or source text do not establish correctness.

| Revision | Command | Result |
| --- | --- | --- |
| Base commit | | |
| Fix commit | | |

Report the commands and results for the relevant native checks in the
[Development Guidelines](https://zipline.ml4trading.io/development-guidelines.html),
including failures and checks not run. Documentation changes need documentation
checks, not an artificial regression; explain when bug-regression evidence does
not apply.

## Numerical behavior and compatibility

Correct verified numerical defects even when outputs change. If this changes an
intended definition, annualization, sign convention or default, link the agreement
in the owning issue and describe compatibility impact. State when not applicable.

## AI assistance and accountability

State whether you used AI tools and which parts they helped produce. Review and
test the submission yourself, and be able to explain its code, evidence and
responses. An automated reply does not replace understanding a review question.
