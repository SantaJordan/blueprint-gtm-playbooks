# Changelog

All notable changes to Blueprint Turbo.

## [1.1.0] - December 2025

### Added
- **Wave 5: Model Version Check** - Automatic check for outdated Anthropic model IDs at end of each run
- **blueprint-validator skill dependency** - Quality enforcement now invokes standalone validator skill
- **Skill Dependencies documentation** - Architecture section documents skill invocations

### Changed
- **Hard Gate Checkpoint** - Now invokes `Skill(skill: "blueprint-validator")` instead of reading files directly
- **Model upgrades** - All references updated from `claude-sonnet-4-20250514` to `claude-sonnet-4-5-20250929`
- **File Structure section** - Updated to show blueprint-validator and blueprint-pvp-deep as dependencies

### Architecture
- Blueprint Turbo is now "just skills" - all external dependencies are skill invocations:
  - `blueprint-validator` (mandatory) - 5-gate validation, banned patterns, data feasibility
  - `blueprint-pvp-deep` (optional) - Enhanced PVP generation for Gold Standard 8.0+
- Validation methodology files moved from `blueprint-pvp-deep/prompts/` to `blueprint-validator/prompts/`

## [1.0.0] - November 2025

### Initial Release
- 4-wave parallel execution architecture
- Browser MCP + Sequential Thinking MCP integration
- 12-15 minute target execution time
- 2-3 segments, 2 PQS + 2 PVP messages
- Dynamic database discovery (no pre-built catalogs)
- Automatic GitHub Pages publishing
- Live website visit requirement (never cached knowledge)
- 8.0+/10 buyer validation threshold
- HIGH feasibility only segments
- Texada-level specificity standard
