# CHANGELOG



## v4.1.3 (2024-08-26)

### Fix

* fix: Channel ID and Name in display settings metadata (#37)

This PR inlcudes the latest version ov libczirw to fix #13 
Fixes #13 ([`04316fe`](https://github.com/ZEISS/pylibczirw/commit/04316fe5861f4e3a5f7a5cb6797903cf75c770e6))


## v4.1.2 (2024-08-06)

### Chore

* chore: remove temporary debugging logic to push to PyPI (#30)

[x] I followed the [How to structure your
PR](https://github.com/ZEISS/pylibczirw/blob/main/CONTRIBUTING.md#creating-a-pr).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **major** release will be created (because the body or
footer begins with &#39;BREAKING CHANGE:&#39;), I created a new [Jupyter
notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **minor/patch** release will be created (because PR title
begins with &#39;feat&#39;/(&#39;fix&#39; or &#39;perf&#39;)), I optionally created a new
[Jupyter notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] In case of API changes, I updated
[API.md](https://github.com/ZEISS/pylibczirw/blob/main/API.md).

Remove debugging code for temporaily pushing to testpypi until
infrastructure properly set up. ([`3b2ea06`](https://github.com/ZEISS/pylibczirw/commit/3b2ea0610baaa0608156426e5c7d781ca7bcdfcb))

### Fix

* fix: consider only dimensions with size &gt;1 for plane-coordinate (#28)

[x] I followed the [How to structure your
PR](https://github.com/ZEISS/pylibczirw/blob/main/CONTRIBUTING.md#creating-a-pr).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **major** release will be created (because the body or
footer begins with &#39;BREAKING CHANGE:&#39;), I created a new [Jupyter
notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **minor/patch** release will be created (because PR title
begins with &#39;feat&#39;/(&#39;fix&#39; or &#39;perf&#39;)), I optionally created a new
[Jupyter notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] In case of API changes, I updated
[API.md](https://github.com/ZEISS/pylibczirw/blob/main/API.md).

Re-write of #16 due to changes in infrastructure.

Fixes #10

---------

Co-authored-by: Soyer, Sebastian &lt;sebastian.soyer@zeiss.com&gt;
Co-authored-by: soyers &lt;soyer.sebastian@gmail.com&gt; ([`264fcb4`](https://github.com/ZEISS/pylibczirw/commit/264fcb4ab95274e54433a0054d69f07c402582f4))


## v4.1.1 (2024-07-26)

### Chore

* chore: Add codeowners (#27)

Add CODEOWNERS file ([`dc1717b`](https://github.com/ZEISS/pylibczirw/commit/dc1717b88e4141546f4e9c29d4c3fa91a2c9ea95))

### Deps

* deps: bump codecov/codecov-action from 3 to 4 (#2)

Bumps
[codecov/codecov-action](https://github.com/codecov/codecov-action) from
3 to 4.
---------

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt;
Co-authored-by: Felix Scheffler &lt;felix.scheffler@zeiss.com&gt; ([`dab7b18`](https://github.com/ZEISS/pylibczirw/commit/dab7b1807486f8eee57c9a565912d1337621cddd))

### Refactor

* refactor: Megalinter and infrastructure (#19)

[x] I followed the [How to structure your
PR](https://github.com/ZEISS/pylibczirw/blob/main/CONTRIBUTING.md#creating-a-pr).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **major** release will be created (because the body or
footer begins with &#39;BREAKING CHANGE:&#39;), I created a new [Jupyter
notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] Based on [Commit
Parsing](https://python-semantic-release.readthedocs.io/en/latest/commit-parsing.html):
In case a new **minor/patch** release will be created (because PR title
begins with &#39;feat&#39;/(&#39;fix&#39; or &#39;perf&#39;)), I optionally created a new
[Jupyter notebook with a matching
version](https://github.com/ZEISS/pylibczirw/tree/main/doc/jupyter_notebooks).
[ ] In case of API changes, I updated
[API.md](https://github.com/ZEISS/pylibczirw/blob/main/API.md).

Infrastructure related changes, linting ([`2e60a2b`](https://github.com/ZEISS/pylibczirw/commit/2e60a2bc15933e92e75d96dce34171de07d109b7))

### Unknown
