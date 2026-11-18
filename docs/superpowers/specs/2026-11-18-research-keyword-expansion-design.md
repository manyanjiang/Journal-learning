# Research Keyword Expansion Design

## Goal

Expand the article collection vocabulary around the user's research interests while keeping topics filterable in the reading center. Keyword matching remains English title/abstract phrase matching through the existing configuration.

## Topic changes

Add two main topic groups:

- `氢氨醇等新燃料`: green/low-carbon/renewable/clean hydrogen and electrolytic hydrogen; hydrogen production, storage and carriers; green/low-carbon ammonia and ammonia fuel/energy/production; green/e-methanol, renewable methanol and methanol fuel; bioethanol; e-fuels, electrofuels, synthetic fuels, power-to-X/gas/liquid, sustainable aviation fuel, and advanced biofuels. Do not add bare `hydrogen`, `ammonia`, or `methanol` terms to limit unrelated chemistry matches.
- `地热与其他可再生能源`: geothermal energy/power, resource assessment/potential, enhanced geothermal systems (including EGS), deep geothermal, geothermal reservoirs/heating/heat pumps, tidal, wave and marine energy, and hydropower. Generic bioenergy is not duplicated here because targeted biofuel terms are included in the new-fuels group and BECCS belongs to CDR.

Expand existing groups with the agreed candidate terms:

- `CO2减排与碳排放`: `greenhouse gas emissions`, `carbon emissions`, `sectoral emissions`.
- `CCUS与地质封存`: geologic sequestration, underground/subsurface CO2 storage, CO2 injection, deep saline aquifer/saline formation storage, CO2-EOR and CO2-EGR, storage in depleted oil/gas reservoirs, depleted reservoir storage, and carbon mineralization/mineral storage. Do not add unqualified enhanced oil/gas recovery terms.
- `CDR碳移除与负排放`: biochar, ocean/marine carbon dioxide removal, and carbon dioxide removal technologies. Keep BECCS and its variants only in this group, not duplicated in CCUS.
- `电力系统与风光资源`: electricity system modeling/modelling, power system planning, renewable energy integration, and solar photovoltaic.
- `能源地理与全球空间布局`: facility siting, infrastructure planning, spatially resolved, and geospatial optimization/optimisation.
- `气候变化与极端天气`: heat stress, precipitation extremes, compound extreme events, and climate attribution.
- `城市与环境空间建模`: urban decarbonization pathways, urban energy planning, urban climate change, and city-level emissions.
- `生命周期与技术经济评价`: life-cycle greenhouse gas emissions, levelized/levelised cost of energy, and social cost of carbon.
- `减排政策与能源战略`: just transition(s), climate justice/equity/fairness, energy justice, equitable/fair transition, distributional impacts/effects, procedural/recognitional justice, intergenerational equity, loss and damage, climate finance, carbon neutrality, and net-zero emissions. Existing carbon-neutrality/net-zero coverage in energy transition remains.

Existing topic labels and unrelated terms remain unchanged. `BECCS` / `bioenergy with carbon capture and storage` remain classified under `CDR碳移除与负排放` only, where the net-removal pathway is the primary research interest. Do not add generic `hydrogen`, `ammonia`, `methanol`, `enhanced oil recovery`, or `enhanced gas recovery` because they are likely to increase unrelated matches.

## Boundaries

Only edit `config.json` keyword groups and regenerate `docs/index.html` from the configured reports after implementation. Do not change journals, ranking thresholds, fetching sources, scoring logic, or historical reports. New terms may broaden matches; review a preview before publishing.

## Verification

Validate JSON parsing and unique topic labels/terms. Use representative scorer checks to confirm new topics match relevant title/abstract phrases, BECCS is assigned only to CDR, and unqualified hydrogen/ammonia/methanol/EOR/EGR articles do not match through the new terms. Run relevant tests and regenerate/inspect the card page after the keyword update.
