# Evidence and calculation register — 2026-11-17

## Why this issue is distinct
ESI's published Optical Intelligence editions cover optical equipment procurement. Its existing technical guides cover battery dispatch and SOC reserve. This proposed manuscript addresses a different EMS/control-integrator question: defining the electrical authority boundary and minimum island power/energy budget. It is evergreen, not a fictitious Week 47 news bulletin. The optical section stays separate.

## Primary source status
- Canada.ca 2026-06-22 Manitoba: https://www.canada.ca/en/natural-resources-canada/news/2026/06/government-of-canada-invests-216-million-in-first-of-its-kind-clean-energy-project-in-manitoba.html. Says the solar, battery and controller project was in an initial phase; future fall 2026 commissioning in that release is NOT verified as achieved today.
- Canada.ca 2026-06-22 Nunavut: https://www.canada.ca/en/natural-resources-canada/news/2026/06/government-of-canada-announces-172-million-to-support-clean-energy-projects-in-nunavut.html. Distinguishes feasibility/FEED from a funded connected/islanded demonstration, not tested operation.
- Canada.ca 2024-01-18 BC: https://www.canada.ca/en/natural-resources-canada/news/2024/01/government-of-canada-contributes-135-million-to-advance-innovative-forest-technologies-and-clean-energy-projects-in-british-columbia.html. Funding and intended integration, no real commissioning evidence.
- Additional technical context (NOT used in machine edition sources because it is outside existing allowed-source hosts): DOE https://www.energy.gov/cmei/femp/articles/islanding-microgrid. No changes to publisher source allowlist.

## Arithmetic independently recomputed
220+120=340 kW; 340-250=90 kW initial deficit; 250-220=30 kW hypothetical post-shed continuous headroom.
220 kW×0.5 h=110 kWh; 500-110=390 kWh; 500/220=2.272727... idealized hours.
These do not imply acceptable power quality, protective settings, physical safety, control sequencing, converter transients or battery warranty.

## Pending promotion boundaries
The current static edition source configuration is historically titled "Optical Intelligence", with `kind: optical`. Source JSON conforms to shared editorial field structure, with existing whitelisted canada.ca hosts, but its **EMS category requires an explicit editorial fit check** before any promotion. No public copy, manifest, canonical, historical issue, HTML or route changed. `published_at` is null and `approval.status` pending deliberately; existing validation must reject this unapproved candidate. Never present a staged JSON as a genuine issued week. A real later publication date/period and Owner SHA-bound approval must be obtained first.