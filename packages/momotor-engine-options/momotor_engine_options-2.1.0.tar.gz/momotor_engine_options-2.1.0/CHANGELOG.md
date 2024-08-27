# CHANGELOG

## v2.1.0 (2024-08-26)

### Feature

* feat: handle step context for options ([`023a3a4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/023a3a4c0d826b4d81dc3f3b5c2f7c71735463b1))

### Fix

* fix: :momotor:option: references do not work ([`732de7d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/732de7de1be4b54899689fd3156eb90d30ab9a99))

* fix: show control (e.g. newline) characters in value strings ([`53f11ba`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/53f11ba03e9176569bb099ed40315cb9d29f77fa))

### Unknown

* doc: remove trailing slash on intersphinx urls ([`4f506a2`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/4f506a220578b65d1cc73518e0a99fed213f16ac))

## v2.0.3 (2024-07-04)

### Fix

* fix: correct separator string ([`5a0be3a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5a0be3a3fada65105303ee9541423058c0d758d8))

* fix: use short option name if it&#39;s in the default domain ([`67294d1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/67294d11ca32b178643b2882304bec8a2c577326))

* fix: os.path.realpath strict argument requires Python 3.10+ ([`68eecdd`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/68eecdd1f22d1cfc701160a8e0f3f53db632c503))

### Unknown

* revert: ci: test: print .git/config to debug auth issue ([`c0461df`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c0461df16d2cdefaf98b855349c49a0f520da857))

* revert: ci: use SEMVER_DEPLOY_KEY to push version changes ([`ce6fe7f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ce6fe7f4f3e67f4678c7254b6dda0b6bb5af5190))

* doc: correct another invalid escape sequence ([`891c7f6`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/891c7f6f2679f726a7aff11885f6978a013e71f4))

* doc: remove invalid escape sequence ([`1a8dbbd`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1a8dbbded78425b55cf1010f1e24574189202b82))

* doc: move preflight and tasks option documentation from docstrings to momotor-engine-options doc ([`91ad101`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/91ad101d6215f014cd52ae4e0aa8add264747ee4))

* doc: update conf.py ([`2941933`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2941933704b4d90a71cf3a263eaf6fe61ec4eb93))

## v2.0.2 (2024-04-25)

### Fix

* fix: do not add an empty or None label property ([`2f887e7`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2f887e750499ccc662b2dd00ad9f89d600f5d0df))

## v2.0.1 (2024-04-16)

### Fix

* fix: update dependencies ([`1b4261a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1b4261a04486ff6174ae9cd1b7f3109b4f2684ed))

## v2.0.0 (2024-04-15)

## v1.2.0 (2023-10-26)

### Chore

* chore: show exact reference used in exception message ([`177fed1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/177fed1379073bab8738a9b3785d1d0be7966ef0))

### Feature

* feat: change `get_scheduler_tools_option` to include results bundle in option resolution, so references to step results can be used ([`39e2183`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/39e218353d7eea2297b992e273bdc4550b3ba14b))

## v1.1.1 (2023-08-29)

### Unknown

* 1.1.1

&#39;chore: bump version number&#39; ([`d37b901`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/d37b9011fe384c6dd84b7848e12477504b662f1e))

* Merge remote-tracking branch &#39;origin/master&#39; ([`5e9d94f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5e9d94f6740b22274b0abac32ef031407cd38309))

## v1.1.0 (2023-08-29)

### Feature

* feat: add json style preflight status ([`a346c6d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a346c6d09905b92f61cbaaae39795e1d2aaddd43))

### Fix

* fix: regression: preflight option selector placeholders are not expanded ([`bdfa8c0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/bdfa8c09ef7544342e4aaa451ce2bed7a834a207))

* fix: emulate LabelOptionMixin&#39;s handling of the label option when preflight causes step to not execute ([`6383900`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/63839005e2e5ea4d401330fbc25c4e3e28ff94e9))

### Test

* test: update to latest Pytest ([`2b2bb42`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2b2bb425e0af16a6151d816933bcb678e010f1a7))

### Unknown

* 1.1.0

&#39;chore: bump version number&#39; ([`7608914`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/7608914796a3de95da1b924724424e0ac14a4f84))

## v1.0.0 (2023-07-06)

### Breaking

* chore: update supported Python versions

BREAKING CHANGE: Dropped Python 3.7 support ([`e1a3d05`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e1a3d05abcfbaaec61b24ad21e94e599e1e869c3))

### Feature

* feat: support sub versions (dashed suffixes) in tool versions, to support Anaconda 2023.03-1 ([`aee2c3f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/aee2c3f1d266b78deb2c2a8bb20c756cb382d361))

### Unknown

* 1.0.0

&#39;chore: bump version number&#39; ([`ac3dbca`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ac3dbcacbcccf1277f6df7701ff7a8121151f3d3))

* doc: fix typo ([`dc46cea`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/dc46cea160e2b667bbfd991a709e5c9b3bda0e77))

## v0.10.1 (2023-06-19)

### Fix

* fix: some error messages were incomplete/cryptic ([`3b37a8c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b37a8c1a2998e68b0661ff3999d4ab41a063571))

### Unknown

* 0.10.1

&#39;chore: bump version number&#39; ([`20fe626`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/20fe6260d57f06d0ddecaae8eb36daa893b6258d))

* doc: fix layout issues in doctests ([`51ab28c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/51ab28c36ce504f074de295d785d11087699acb9))

## v0.10.0 (2022-11-15)

### Feature

* feat: add &#39;pass-hidden&#39; and &#39;fail-hidden&#39; preflight actions ([`c749a05`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c749a0560083ee6395ccdb829714626ff1f67796))

### Unknown

* 0.10.0

&#39;chore: bump version number&#39; ([`328d6ed`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/328d6edde51b6899a30837f8686d8d97193de077))

## v0.9.1 (2022-10-27)

### Fix

* fix: strip leading and trailing whitespace from selectors and references ([`929d233`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/929d23349700132234848921ed19de1f16628374))

### Test

* test: update doctest ([`271174c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/271174c31817d30434bc6a1e83e01efa45f99e27))

### Unknown

* 0.9.1

&#39;chore: bump version number&#39; ([`13648de`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/13648de60b78547ca878116fb4c78ba9fb03aa74))

## v0.9.0 (2022-10-21)

### Chore

* chore: clearer error message ([`3b81567`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b81567c15e1c95bda3811a0dc5d617aa6f3e8b8))

### Unknown

* 0.9.0

&#39;chore: bump version number&#39; ([`b4cbb39`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b4cbb39b665e0abf95070d4a19a87c8cfcdd6225))

## v2.0.0-rc.11 (2024-03-19)

### Breaking

* feat: convert to PEP420 namespace packages

requires all other momotor.* packages to be PEP420 too

BREAKING CHANGE: convert to PEP420 namespace packages ([`1b01285`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1b01285620e39f7882e5a68590afdc5e2ee2e1b5))

### Refactor

* refactor: replace all deprecated uses from typing (PEP-0585) ([`00021e8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/00021e8ea1111d2112e611bd93975082678997d1))

## v2.0.0-rc.10 (2024-03-04)

### Feature

* feat: extend `document_option_definition` to document step options ([`83bbd22`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/83bbd22735b19f60c6ee7d2165dd0bc1e3f86876))

### Refactor

* refactor: update type hints for Python 3.9 ([`9705bb8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9705bb832c19673b6fd8f0016ca0fc342bced1cf))

### Unknown

* doc: make production lists consistent ([`cdb8721`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cdb87219a0ad6f965bd2f9e4690f5068d54d7c56))

* doc: correct reference syntax documentation ([`e26f1d7`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e26f1d745bceae8ddf411c14d269008b4ad3bd3e))

* doc: correct reference syntax documentation ([`f4f4fe8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/f4f4fe84a09a035ed8cdbf45ed08ecc27b3bbded))

* doc: documentation update/clarifications ([`c61e8fc`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c61e8fc30cdc40c5821cd152e009ab8285b521d0))

* doc: several documentation fixes/clarifications ([`048016d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/048016d44a3721b58cd9bf5114acdee64ee72beb))

## v2.0.0-rc.9 (2024-01-16)

### Breaking

* feat: add Sphinx extension to handle external references to local package

BREAKING CHANGE: moved `momotor.options.sphinx_ext` to `momotor.options.sphinx.option` ([`297382e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/297382e142841a1211c2452261e12fdbcd1e22c2))

* feat: remove deprecated interface of get_scheduler_tools_option()

BREAKING CHANGE: deprecated interface of get_scheduler_tools_option() removed ([`130078d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/130078d9c1d6d97397918565f71e3a7bbb1b41df))

### Fix

* fix: docutils is an optional dependency ([`1942882`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1942882b2762b9cb14c78ff28e29e94c0b37093e))
