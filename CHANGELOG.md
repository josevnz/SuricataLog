# SuricataLog changelog

## Fri Sep 15 2023 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.1.0
- Major packaging refactoring, no more setup.py/ setup.cfg support
- Dropped support of Rich and migrated to the newest version of Textualize, uniform UI code
- Fixed bug that prevented events rendering on eve_log.py for large files
- Updated documentation

## Fri Sep 1 2023 Jose Vicente Nunez <kodegeek.com@protonmail.com> - 0.0.8
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