# A microgrid islanding plan needs a load budget, not just an EMS dashboard

A reproducible island-mode load and battery-energy worksheet separates local grid-forming control, load shedding and EMS scheduling responsibilities.

## Briefing

Grid-connected energy optimization and islanded electrical operation require different evidence. A supervisory EMS can help schedule equipment and optimize available energy, but its dashboard is not proof of power-system protection, grid-forming capability, reliable island transfer or utility permission. Three primary Canadian government releases provide distinct project-stage contexts: a Manitoba development plan naming a microgrid controller, a Nunavut proposal explicitly describing connected and islanded modes, and a British Columbia demonstration aiming to integrate solar and storage with existing diesel supply. None supplies the witnessed acceptance records for the entirely hypothetical case below. The worked power and energy budget illustrates which engineering questions a buyer should ask before relying on an island-mode commitment.

## 1. Separate grid-forming control from supervisory dispatch

**Evidence status:** Engineering mechanism / project-stage evidence

Natural Resources Canada's June 22, 2026 Manitoba release identifies a planned integrated microgrid that combines solar photovoltaic generation, battery storage and a microgrid controller in the Tadoule Lake community. The release anticipated commissioning later in 2026; it does not verify actual commissioning or describe a witnessed transition test. A controller named in a project announcement is not an acceptance record.

**Why it matters.** A fast electrical-control function and an EMS energy schedule act on different time scales. Neither a cloud dashboard nor a simulation proves that a battery inverter can form an electrical island.

**Engineering and procurement implications.** In a constructed facility load list, 220 kW is critical demand and 120 kW is deferrable, totaling 340 kW. The proposed island source has a hypothetical 250 kW continuous steady-state active-power rating. Connected load exceeds this limit by 90 kW. If 120 kW is shed using a separately engineered and validated scheme, the remaining 220 kW sits 30 kW below that nominal steady-state limit. The buyer should require a control-authority matrix naming the protection devices, grid-forming functions, shedding actuator and supervisory EMS, with expected communication-loss behavior and test evidence for each.

**Boundary of evidence.** All load and rating figures are invented teaching values, not the Manitoba site's figures. No transient rating, frequency stability, fault response or physical switching sequence can be inferred from steady-state arithmetic.

**Sources:** [manitoba](#source-manitoba) · [nunavut](#source-nunavut).

## 2. Check energy endurance separately from instantaneous power

**Evidence status:** Independent calculation / illustrative conditions only

Canada's June 22, 2026 Nunavut funding announcement distinguishes several preliminary microgrid engineering studies from a proposed solar-plus-battery demonstration designed to operate both connected to the local microgrid and in islanded mode. This is an announced demonstration objective, not a report of guaranteed runtime, validated protection settings or achieved island transfer. A planned operating mode is not necessarily a delivered capability.

**Why it matters.** Enough inverter kW for the load does not establish enough usable battery kWh for the necessary period. Dispatch commands cannot make up a shortfall in either physical resource.

**Engineering and procurement implications.** Continue the hypothetical case: after the illustrative shed, 220 kW of critical load remains. Assume 500 kWh of usable energy at a specified AC boundary and a 30-minute uninterrupted interval. Energy required is 220 kW multiplied by 0.5 hour, or 110 kWh; the simple residual is 390 kWh before reserve and other losses. At 220 kW constant demand the idealized ratio 500 kWh divided by 220 kW equals 2.27 hours. A buyer should demand a minimum-SOC limit, peak demand trace, required start-up energy, auxiliary-load account and safety reserve before converting this paper estimate into a service commitment.

**Boundary of evidence.** The example omits reactive power, voltage behavior, losses, battery temperature, degradation, minimum SOC, transient load steps and overload constraints. The 2.27-hour quotient is not a tested capability or dispatch instruction.

**Sources:** [nunavut](#source-nunavut) · [manitoba](#source-manitoba).

## 3. Ask for the site's own commissioning boundary, not an announcement

**Evidence status:** Historical original source / procurement inference

The Government of Canada's January 18, 2024 British Columbia release lists support for the Nemiah Valley Renewable Microgrid Project, intended to demonstrate solar and battery storage integration with an existing diesel microgrid. The same release identifies a separate related hydro front-end engineering and design study. Public funding, design work and demonstration scope are different kinds of evidence from a site-specific commissioning, protection or operational acceptance report.

**Why it matters.** A supplier's EMS scope often stops at monitoring and scheduling, while another party owns the utility switchgear, inverter controls, protection, diesel coordination and safety validation.

**Engineering and procurement implications.** The acceptance register should include, at minimum, utility/interconnection permission, the approved one-line diagram, switching and protection responsibility, inverter grid-forming capability, frequency/voltage limits, critical-load classification, load-shed verification, energy meter location, battery reserve, control-network failure response, operational handover and a witnessed reconnection test. Each row needs a responsible engineer or company, an acceptance document and an observable criterion. Qualify hardware and field performance independently; the announcement alone cannot settle a contract's complete deliverable.

**Boundary of evidence.** The release does not identify the exact installed EMS vendor, performed safety tests, project completion date, site acceptance result or authorization for any particular switching operation.

**Sources:** [british-columbia](#source-british-columbia) · [manitoba](#source-manitoba).

## Reproducible island-load budget

All values below are **constructed**. No switching sequence, safety acceptance or site measurement is implied.

| Quantity | Hypothetical value | Calculation |
| --- | ---: | --- |
| Critical active load | 220 kW | Retained after permitted shedding |
| Deferrable active load | 120 kW | To be verified by qualified controls engineering |
| Before shedding | 340 kW | 220 + 120 |
| Grid-forming source steady-state rating | 250 kW | Does not establish fault or transient rating |
| Pre-shed active-power deficit | 90 kW | 340 − 250 |
| After shedding | 220 kW | Critical load only |
| Post-shed steady-state margin | 30 kW | 250 − 220 |
| Assumed usable AC battery energy | 500 kWh | Explicit boundary, no reserve modeled |
| Thirty-minute energy requirement | 110 kWh | 220 kW × 0.5 h |
| Illustrative residual | 390 kWh | 500 − 110 |
| Idealized energy-only endurance | 2.27 h | 500 / 220 |

The 30 kW margin is a steady-state active-power calculation, **not** a guarantee of frequency or voltage stability, reactive capability, load-step survival or fault-clearing behavior. The 2.27-hour result assumes constant load without SOC reserve, losses or degradation and is not an operational recommendation.

## Takeaways

- Assign grid-forming, protection, load shedding and energy-scheduling authority to separately verified systems; an EMS user interface cannot certify the electrical transition.
- In the constructed case, shedding 120 kW reduces the continuous load from 340 kW to 220 kW below a hypothetical 250 kW steady-state source rating.
- The constructed half-hour 220 kW critical-load duty needs 110 kWh at the stated energy boundary, but it does not certify any battery's operating endurance.

## Remaining uncertainty

- No public project announcement is represented as evidence of actual commissioning, a tested island transition or the capabilities of a product sold by a named vendor.
- Illustrative steady-state kW and idealized AC kWh do not establish converter dynamics, reactive-power supply, protection coordination or safe site switching.
- A qualified site-specific protection and controls authority must review local operating procedures and contractual guarantees.

## Engineering questions to follow

- Require a signed control-authority matrix mapping local protection, grid-forming inverter controls, shed actuators and supervisory EMS.
- Validate the actual measured critical-load trace, energy-meter boundary, minimum SOC and weather-sensitive performance instead of copying the illustrative numbers.
- Document utility permission and independently witnessed island-transfer and resynchronization acceptance before claiming a deliverable operating mode.

## Original primary sources

<a id="source-manitoba"></a>
- **Natural Resources Canada**, [Government of Canada invests $21.6 million in first-of-its-kind clean energy project in Manitoba](https://www.canada.ca/en/natural-resources-canada/news/2026/06/government-of-canada-invests-216-million-in-first-of-its-kind-clean-energy-project-in-manitoba.html); released 2026-06-22, checked 2026-11-17. The June 22 Manitoba release describes a planned PV-plus-battery microgrid with a microgrid controller at Tadoule Lake; the release's expected commissioning was prospective.
<a id="source-nunavut"></a>
- **Natural Resources Canada**, [Government of Canada announces $17.2 million to support clean energy projects in Nunavut](https://www.canada.ca/en/natural-resources-canada/news/2026/06/government-of-canada-announces-172-million-to-support-clean-energy-projects-in-nunavut.html); released 2026-06-22, checked 2026-11-17. The release differentiates feasibility and front-end design from a proposed demonstration that could operate on the local microgrid and independently in islanded mode.
<a id="source-british-columbia"></a>
- **Natural Resources Canada**, [Government of Canada Contributes $13.5 Million to Advance Innovative Forest Technologies and Clean Energy Projects in British Columbia](https://www.canada.ca/en/natural-resources-canada/news/2024/01/government-of-canada-contributes-135-million-to-advance-innovative-forest-technologies-and-clean-energy-projects-in-british-columbia.html); released 2024-01-18, checked 2026-11-17. The January 18 release includes a Nemiah Valley solar-plus-battery project intended for integration with an existing diesel microgrid; it does not report witnessed site acceptance.

This is an analytical worksheet, not a safe-switching manual, site engineering approval or operational certification.