# Publisher Resources — Sources Checklist

Aggregates workshops, training, and events for local news organizations and journalists.
No geolocation filtering applied.

## Currently Implemented

### ICS Feeds
- [ ] INN (Institute for Nonprofit News) — `https://inn.org/events/list/?ical=1` (WordPress Tribe Events)
- [ ] SPJ (Society of Professional Journalists) — `webcal://calendar.spjnetwork.org/calendar.php`
- [ ] Poynter Institute — `https://www.poynter.org/events/?ical=1` (WordPress Tribe Events)
- [ ] NAHJ (National Assoc. of Hispanic Journalists) — `https://nahj.org/events/?ical=1` (WordPress Tribe Events)
- [ ] NLGJA (Assoc. of LGBTQ+ Journalists) — `https://www.nlgja.org/events/?ical=1` (WordPress Tribe Events)
- [ ] AHCJ (Assoc. of Health Care Journalists) — `https://healthjournalism.org/events/?ical=1` (WordPress Tribe Events)
- [ ] SABEW (Soc. for Advancing Business Editing & Writing) — `https://sabew.org/?post_type=tribe_events&ical=1&eventDisplay=list` (WordPress Tribe Events)
- [ ] Hacks/Hackers — `https://api2.luma.com/ics/get?entity=calendar&id=cal-09kcgQfLYGyy2JP` (Luma calendar ICS)

### Scrapers
- [ ] SEJ (Society of Environmental Journalists) — `sej_calendar.py` (RSS calendar at `sej.org/rss_calendar`)
- [ ] IRE/NICAR Conference Schedules — `ire_schedule.py` (S3 JSON, updated per conference cycle)
- [ ] SJN (Solutions Journalism Network) — `sjn_events.py` (Drupal HTML scraper at `solutionsjournalism.org/events`)
- [ ] PEN America — `pen_america.py` (WordPress REST API at `pen.org/wp-json/wp/v2/event`)
- [ ] NABJ (National Assoc. of Black Journalists) — `nabj_events.py` (Wild Apricot RSS at `nabj.org/resource/rss/events.rss`)
- [ ] American Press Institute — `eventbrite.py` (Eventbrite organizer `59619554833`; 0 upcoming as of 2026-03)

- [ ] Center for Cooperative Media — `eventbrite.py` (Eventbrite organizer `5988913981`)

## Investigated — Possible with Scraper
- **RJI (Reynolds Journalism Institute)** — ICS feed at `calendar.missouri.edu/live/ical/events/group/Reynolds%20Journalism%20Institute/` works but very low volume (2 events), Columbia MO only

## Investigated — Not Viable

- **LION Publishers** — No calendar feeds; WordPress events page at `https://lionpublishers.com/events/` could be scraped
- **American Journalism Project** — No public events; invitation-only (AJPalooza)
- **Virginia Local News Project** — No events calendar; runs ongoing programs only
- **GIJN** — Site returns 403 to all automated requests; no public feeds
- **East-West Center** — Cloudflare 403 on all automated access
- **The Open Notebook** — Trainings are custom-booked/on-demand, no scheduled events
- **Trusting News** — Events announced via blog posts with Zoom links, no structured data
- **ONA** — No public feeds; Novi AMS platform, EventScribe for conferences
- **Knight Foundation** — Events infrastructure under development, not live
- **RTDNA** — No public feeds; /events/feed returns 500
- **National Press Club** — Custom calendar grid, no feeds
- **EWA** — No feeds; custom WordPress events with AJAX
- **NABJ** — ~~Site returns 403 to automated access~~ Moved to Scrapers (RSS feed at CDN bypasses Cloudflare)
- **AAJA** — No event-specific feeds; RSS has news only
- **Listening Post Collective** — WordPress with The Events Calendar plugin (ICS likely at `/events/?ical=1`), but Cloudflare bot protection blocks all automated access (403)
- **BlueLena** — Client-only roundtables posted as retrospective recaps; no public event feeds (WordPress/Newspack)
- **Blue Engine Collaborative** — No events; Squarespace consulting site with cohort-based accelerator programs only
- **IWMF (Intl Women's Media Foundation)** — WordPress; robots.txt blocks ClaudeBot and all AI crawlers; 403 on all requests
- **CPJ (Committee to Protect Journalists)** — WordPress; events archive dormant since 2018; safety workshops are private
- **RCFP (Reporters Committee)** — WordPress; no events plugin; trainings are request-based, no scheduled public events
- **The IIJ (Institute for Independent Journalists)** — Squarespace; webinars listed as past replays only, no upcoming dates posted
- **Maynard Institute** — WordPress; no events plugin; custom HTML event pages, no feeds
- **Religion News Association** — Squarespace; one annual conference; no feeds or structured data
- **JAWS (Journalism & Women Symposium)** — Squarespace; one annual conference (CAMP); no feeds
- **Indigenous Journalists Assoc. (f/k/a NAJA)** — naja.com dead; new site indigenousjournalists.org (WordPress) has no event feeds; one annual conference (IMC)
- **Local Media Association** — WordPress Events Manager; ICS at `/events/?ical=1` exists but stale (last updated 2024)
- **News Product Alliance** — Squarespace; one annual summit via Eventbrite; no feeds
- **SRCCON / OpenNews** — Static sites; no feeds; SRCCON 2026 Jul 8-9 Minneapolis; manual add only
- **Lenfest Institute** — WordPress; no events plugin; 3 events hand-maintained on static page
- **News Revenue Hub** — WordPress; no events page; RSS feed empty; consulting site only
- **Report for America** — WordPress (Elementor); no events page or feeds
- **Alaska Press Club** — WordPress.com hosted; no events plugin; conference info in blog posts only
- **SembraMedia** — WordPress; no events page or feeds; blog/content-focused
- **Student Press Law Center** — WordPress; no events page; trainings are on-request/private
- **LION Publishers** — No calendar feeds; WordPress events page at `https://lionpublishers.com/events/` could be scraped
- **Branch Four** — GoDaddy static site; no events page, no feeds; training is on-request only
- **Indiegraf** — WordPress; webinars are static pages with no event plugin or feeds
- **NC Local** — WordPress/Newspack; static events page; events hosted on Eventbrite
- **Nieman Foundation** — WordPress; no events section; /calendar/ returns 401 (private)
- **Journalist's Resource** — WordPress; webinars are past-recap blog posts only, no upcoming events
- **Tiny News Collective** — Ghost CMS; events are members-only, no public feeds
