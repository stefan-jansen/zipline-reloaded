Contributing to Zipline
=======================

.. contribution-policy-start

Zipline Reloaded accepts bug, security and compatibility fixes and improvements
to its existing documentation. Direct new feature work to current ML4T libraries,
including `Backtest <https://github.com/ml4t/backtest>`_. Existing Zipline workflows
remain in maintenance scope.

Start with one issue
--------------------

Search the `issue tracker
<https://github.com/stefan-jansen/zipline-reloaded/issues>`_ before opening an issue.
Each issue should describe one problem or coherent change. Report unrelated
problems separately, and discuss substantial changes in the owning issue before
implementing them.

For a bug, include the package version, environment, expected behavior, observed
behavior and the smallest complete reproduction. Report suspected vulnerabilities
privately to the maintainer at pm@ml4trading.io, rather than in a public issue.

Submit one focused pull request
-------------------------------

Each pull request should address one issue and include a closing reference such
as ``Closes #123``. Related code, tests and documentation can belong together;
keep unrelated fixes, refactors and formatting changes separate. Automated
dependency updates and administrative metadata changes do not require a separate
issue.

For a bug fix, add a regression that exercises the affected public API or user
workflow. Run it against the relevant base revision and the proposed fix, and
record both revisions, commands and results. It must fail because of the defect
on the base and pass with the fix. Tests of copied logic or source text do not
establish that the behavior is corrected.

Run the relevant checks in the Development Guidelines and report the commands and
results. Documentation changes need documentation checks, not an artificial
regression test. Disclose failures or checks you could not run.

Correct verified defects even when they affect numerical results. If a change
alters an intended definition, annualization, sign convention or default, agree
on the expected behavior in the owning issue and document the compatibility
impact. Existing output alone does not establish correctness.

AI assistance and accountability
--------------------------------

You may use AI tools for code and prose. State whether you used them and which
parts they helped produce. Review and test the submission yourself, and be able
to explain its code, evidence and responses. An automated reply does not replace
understanding a review question.

Wait for feedback on your first focused contribution before opening a large
series of similar pull requests. Maintainers may ask you to split or complete a
submission, or close it without detailed review when it does not meet these
requirements. Useful fixes in bundled submissions can be resubmitted separately.

.. contribution-policy-end

See the `Development Guidelines
<https://zipline.ml4trading.io/development-guidelines.html>`_ for environment setup,
tests, style and documentation builds. Ask usage questions in the `community
forum <https://exchange.ml4trading.io/>`_.
