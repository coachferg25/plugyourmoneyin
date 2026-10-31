# Plug Your Money In (v1)
Static site. Source of truth: `data/apps.json` (apps), `data/changelog.json` (what changed), `data/site.json` (domain, newsletter action).
Rebuild: `python3 build.py` -> writes `site/` (HTML, sitemap.xml, robots.txt). Preview: `cd site && python3 -m http.server 8765`.
Weekly routine: open each app's `sources` URLs, update `platforms.*.status/how/confidence`, set `checked`, add a changelog entry, rebuild.
Statuses: yes / partial / no / unknown. `confidence`: documented, inferred, reported, third-party-claim, absence-of-docs, vendor-staff-statement.
TODOs before launch: set `base_url` + `newsletter_action` + `contact` in data/site.json; affiliate slots are empty placeholders (apps[].affiliate).

## Deploy

Pushes to `main` run `.github/workflows/pages.yml`: `python3 build.py`, then the official Pages actions publish `site/` to https://coachferg25.github.io/plugyourmoneyin.

`actions/configure-pages` is called with `enablement: true`, which tries to turn GitHub Pages on for this repository. That API call needs a token other than the default `GITHUB_TOKEN` (a personal access token with the `repo` scope, or a GitHub App token with `administration:write` and `pages:write`). With the workflow's default token, turn Pages on once by hand: **Settings → Pages → Build and deployment → Source: GitHub Actions**. After that, each push to `main` deploys on its own. You can also re-run the workflow from the Actions tab.
