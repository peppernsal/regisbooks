<!-- omit in toc -->
# Contributing to RegisBooks

Thanks for your interest! Unfortunately, at this time, external contributions are *not* accepted.

If you have an existing approval to make a contribution, please refer to the guide below.

<!-- omit in toc -->
## Table of Contents

- [I Have a Question](#i-have-a-question)
  - [I Want To Contribute](#i-want-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Improving The Documentation](#improving-the-documentation)
- [Styleguides](#styleguides)
  - [Commit Messages](#commit-messages)
- [Join The Project Team](#join-the-project-team)

## Code of Conduct

This project and everyone participating in it is governed by the
[12 Code of Conduct](12/blob/123/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to <>.

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Help Documentation](https://regisbooks.org/help).

Before you ask a question, it is best to search for existing [Issues](https://github.com/User0332/regisbooks/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/User0332/regisbooks/).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (nodejs, npm, etc), depending on what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

> ### Legal Notice <!-- omit in toc -->
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project licence.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side. If you are looking for support, you might want to check [this section](#i-have-a-question).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/User0332/regisbooks/issues?q=label%3Abug).
- Collect information about the bug:
  - JavaScript Console
  - OS, Browser and Version (e.g. Windows 11/Chrome 149.0.7827.114)
  - Can you reliably reproduce the issue?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](12/issues/new) (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue).
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be added to the backlog, and the issue will be left to be [implemented by someone](#your-first-code-contribution).

You are also welcome to submit bug reports through the feedback form (provided on the site navbar), through issues is the preferred route.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for RegisBooks, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers understand your suggestion and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [Help Documentation](https://regisbooks.org/help) carefully and find out if the functionality is already covered.
- Perform a [search](https://github.com/User0332/regisbooks/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/User0332/regisbooks/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots or screen recordings** which help you demonstrate the steps or point out the part which the suggestion is related to.
- **Explain why this enhancement would be useful** to most RegisBooks users.

### Your First Code Contribution

At the moment, you may not contribute code to issues that are tagged with `requires-db-migration`.

#### Setting Up The Repository

First, create a fork of the repository by clicking the `Fork` button on the main repository page. See the [GitHub Documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) for more help.

Next, clone your fork locally:

```sh
git clone https://github.com/my-user-name/your-fork-name/
```

Next, cd into the repository and create a branch to work in. If you are attempting to close an issue, this would typically be named close-issue-XX or fix-issue-XX, where XX is the issue #.

```sh
cd regisbooks
git switch -c fix-issue-79
```

#### Setting Up The Environment

Now you are ready to setup the environment. Ensure that you have Python >= 3.14, <= 3.15 installed. We use Poetry for dependency management, so ensure that you have [installed Poetry](https://python-poetry.org/docs/).

When you install Poetry, make sure that it is added to PATH, or you will have to run the following commands using (`python -m poetry` instead of `poetry`).

First, setup the poetry env by running `poetry install` in the root directory of the project. Then, activate the environment. You can do this by running `iex (poetry env activate)` on Windows (PowerShell) or `eval $(poetry env activate)` on Linux (Bash). You can also use `poetry env info` to view the location of the virtual environment and add this to your IDE for code completion.

You must also setup [PostgreSQL](https://www.postgresql.org/download/) for the local database. Create a user named `regisbooksuser` and set a password for it. Create a database called `regisbooks` whose owner is `regisbooksuser`.

Next, create two secret keys by running the following:
```
python -c "import secrets;print(secrets.token_hex(16)+'\n'+secrets.token_hex(16))"
```

The first secret key will be the admin API key. This should be placed in `website/admtools/.env` with the name `ADMIN_KEY`.

```sh
website/admtools/.env

ADMIN_KEY=556b3e6e8bdf31cae74f6e09b666eb72
```

Hash the key and place it in `website/instance/.env` for verification:

```sh
python -c "import hashlib;print(hashlib.sha512(b'{ADMIN_KEY_HERE}').hexdigest())"
```

```sh
website/instance/.env
ADMIN_KEY_HASH=f0e60e6f0b520046e16235f8f8919daeebdeb24e9107e02db737b2e1a3ca0437de759f6b37881b3bb390e473e92845da9eb2a4592ab8daf96e3a6afc9512a86b
```

The second key will be the app's secret key. Set this in `website/instance/.env` and name it `REGISBOOKS_SECRET_KEY`.
```sh
website/admtools/.env

REGISBOOKS_SECRET_KEY=cf032604fbdbca19303d2e2a063ac356
```

There are a variety of other variables that need to be set in `website/instance/.env`

```sh
DB_URI=postgresql://regisbooksuser:<POSTGRESQL_USER_PASSWORD>@localhost:5432/regisbooks
EMAIL_WHITELIST= # can be empty, but you may want to add your personal email here to allow you to login locally
REGISBOOKS_AUTH_API_KEY= # this will only be provided to maintainers, leave it empty
REGISBOOKS_AUTH_URL=https://auth.regisbooks.org
TEST_REGISBOOKS_AUTH_API_KEY= # this will be provided to you by a maintainer, please ask them for the information.
TEST_REGISBOOKS_AUTH_URL=https://228794087.propelauthtest.com
REGISBOOKS_SECRET_KEY=cf032604fbdbca19303d2e2a063ac356 # you set this in the previous steps
ADMIN_KEY_HASH=f0e60e6f0b520046e16235f8f8919daeebdeb24e9107e02db737b2e1a3ca0437de759f6b37881b3bb390e473e92845da9eb2a4592ab8daf96e3a6afc9512a86b # you set this in the previous steps
GOOGLE_BOOKS_API_KEY= # this will be provided to you by a maintainer, please ask them for the information.
```

Once you have all of that, you can finally run the development server locally. `cd` into `website` and run `webpy run --force-debug`. The server information should be displayed. Follow the localhost link to access the website. If you run into any problems during setup, please follow the [question reporting procedures above](#i-have-a-question) or talk to a maintainer.

When you have thoroughly tested your changes and pushed all your commits to your fork, you may open up a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to the main repository that closes the intended issue. A maintainer will then review and approve your changes or requeste edits.

## Styleguides

### Code

All code should use tabs for indentation. Each indent should use one tab. Use comments sparingly and only for clarifications on otherwise cryptic code.

Python code should follow PEP 8 naming conventions. Changes in app.py should fall under their respective function (`init_db_api` for any changes to db models, `external_api_routes` for routes not authenticated by PropelAuth, `internal_api_routes` for PropelAuth-authenticated routes, `register_error_handlers` for HTTP error handlers, etc.).

JavaScript code should generally follow the [MDN style guide](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Code_style_guide/JavaScript). All route-specific logic should go in a single JS file with the same base name as the route it represents. See existing code for more clarification.

Class names, ids and other names provided to attributes in HTML should be dash-separated.

### Commit Messages

Commit messages should be styled according to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Join The Project Team

To join the project team, reach out to the maintainer/Club member(s) that gave you approval to contribute.

<!-- omit in toc -->
## Attribution
This guide is based on the [contributing.md](https://contributing.md/generator)!
