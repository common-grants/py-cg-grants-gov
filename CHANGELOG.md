# Changelog

## [0.2.0](https://github.com/common-grants/py-cg-grants-gov/compare/v0.1.0...v0.2.0) (2026-06-25)


### ⚠ BREAKING CHANGES

* `cg_grants_gov.generated` module removed — `from cg_grants_gov.generated import schemas` no longer works
* `cg_grants_gov.cg_config` module removed — all imports from `cg_grants_gov.cg_config` no longer work
* `schemas` removed from package public API — `grants_gov.schemas.Opportunity` is no longer accessible
* The `Opportunity` model (which extended `OpportunityBase` with `OpportunityCustomFields`) is replaced by `OpportunityBase[OpportunityFields]`
* Plugin instantiation changed from `Plugin(extensions=..., schemas=...)` to `define_plugin(PluginSchemas(...), meta=PluginMeta(...))`


### Features

* 813 expand transform ([#8](https://github.com/common-grants/py-cg-grants-gov/issues/8)) ([a68a7b3](https://github.com/common-grants/py-cg-grants-gov/commit/a68a7b337796daa1b2c71f4a9908ffd2dbccaf92))

## 0.1.0 (2026-04-08)


### Features

* Building CI/CD pipeline steps ([aedf39f](https://github.com/common-grants/py-cg-grants-gov/commit/aedf39f97f62af45311d25bdeb6e295feb799583))
* Initial setup and first plugin ([#1](https://github.com/common-grants/py-cg-grants-gov/issues/1)) ([cc4d3ed](https://github.com/common-grants/py-cg-grants-gov/commit/cc4d3ed920ab496d77fabcbc0aa6d0f784901160))
* renaming plugin to cg_extension_framework ([4195e51](https://github.com/common-grants/py-cg-grants-gov/commit/4195e51212bc1ac028a4f82e24c49c02a91838aa))
* Updating documentation and adding configs for pipeline steps ([72140ef](https://github.com/common-grants/py-cg-grants-gov/commit/72140ef100281a89319db5df89b5c77aa144f6af))


### Bug Fixes

* Fixing Agency Value  ([#4](https://github.com/common-grants/py-cg-grants-gov/issues/4)) ([f8225e8](https://github.com/common-grants/py-cg-grants-gov/commit/f8225e86404b86f1cd792ff020d2f8ef2eb6373c))
