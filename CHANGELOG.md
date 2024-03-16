# SuricataLog changelog

## Mar Sat 22 2024 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 1.0
- Match version to stable version
- Added unit tests for TUI

## Mar Sat 16 2024 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1.5
- Better error handling
- Minor bug-fixes on table data presentation
- Code refactoring to allow new components
- eve_json can now search by data present on the table (Press Ctrl + \ and start typing)
- SuricataLog officially no longer beta. Next release will focus on speed improvements on large files.

## Jan Mon 1 2024 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1.3, 0.1.4
- Packaging fixes

## Nov Sun 5 2023 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1.2
- Removed old README file. Nobody will ever look into that
- Added compressed eve_large.zip added to on test directory, for more realistic performance testing.
- Removed the JSON, BRIEF format from event_log. It is too much data to display at the same time. Instead, select a row to get full details.
- UI improvements

## Fri Sep 15 2023 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1.0, 0.1.1
- Packaging refactoring, no more setup.py/ setup.cfg support
- Migrated to the newest version of Textualize, uniform UI code
- Fixed bug that prevented events rendering on eve_log for large files
- Removed Docker support. Functionality not used, will add again if users demand for it.
- Updated documentation

## Fri Sep 1 2023 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.8, 0.0.9
- Fixed packaging bug that prevented eve_log.py from running when installed from PyPi.org
- Documentation fixes

## Sun May 1 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.7
- More responsive UI, specially for large suricata eve files.

## Sun May 1 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.6
- More responsive UI, specially for large suricata eve files.

## Sun May 1 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.5
- Docker container to run all the SuricataLog scripts

## Sun Apr 24 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.4
- Split program demo so it can fit in Asciinema hosting
- New eve_json.py script, mimics queries from [eve JSON examples jq](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html)

## Thu Apr 21 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.3
- Added scrolling to tables, json.
- Added new 'brief' output format
- Added Asciinema demonstration

## Sun Apr 17 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.2
- Fixed broken unit tests

## Sun Apr 17 2022 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.1
- First release.