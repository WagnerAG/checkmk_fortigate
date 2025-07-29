# 📜 Changelog

> **Notice:**  
> All notable changes to this project are recorded in this document. This project uses [SemVer](https://semver.org/lang/de/) for version management.
> The format is based on [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

---

## [1.2.0] - 2025-07-29

### 🚀 Added
- Boilerplate for newer CheckMK versions
- Special agent contribution from Checkmk Forum https://forum.checkmk.com/t/fortigate-special-agent/47573/19 user 'bitwiz' many thanks!
- Merged all changes from CheckMK 2.2 FortiOS release `1.0.3`

### 🔄 Changed
- Removed temporary predictive session monitoring
- Migrated all Pydantic models to Pydantic V2

### 🐛 Fixed
- Various small improvements
- Improved and fixed Pytests for new pydantic models and CheckMK 2.3
- From https://github.com/sva-mh/checkmk_fortigate/tree/23_fixes GitHub Repo to improve the compatibility and stability many thanks!

## [1.1.0] - 2024-11-11

### 🚀 Added
- Introduction of predictive session monitoring

### 🔄 Changed
- Use builtin ruleset for cpu check
- Use builtin ruleset for memory check

### 🐛 Fixed
- Improved special agent if switches are not connected, ignore them
- Ignore trunk ports, because they have no counters as normal interfaces
- Added fortios_interface_cmdb to the package
- Various small improvements

---


## [1.0.4] - 2025-07-28

### 🔄 Changed
- Better error handling for special agent crontributed by `bitwiz`
- Improved GitHub Actions

---

## [1.0.3] - 2025-07-21

### 🐛 Fixed
- Improved special agent for Fortigate 7.2 and 7.4 (Switch interfaces)
- Compatibility for CMK 2.2.x
- Wrong imports at `FortiOS devices` view
- Fortigate:
    - interface discovery should work even if a non-existent interface pattern is given in the exclusion list
    - interfaces display `CRIT` state if they go down
- FortiSwitches:
    - interfaces display `CRIT` state if they go down
    - added option to inventorize only active interfaces
        - __Note:__ if a interface description matches, the interface will be added even the state is `down`
- License check is more stable now

---

=======

## [1.0.0] - 2024-09-12

### 🚀 Added
- Initial commit and first version of FortiOS special agent
- Set maximum checkmk version, actually this special agent does not support CheckMK 2.3

---

# 💡 Frequently asked questions (FAQ)

**How are versions determined in this project?**
This project uses Semantic Versioning (MAJOR.MINOR.PATCH), where each change increments one of the three components:
> - **MAJOR** versions contain significant changes that are not backwards compatible.
> - **MINOR** versions add new features that are backwards compatible.
> - **PATCH** versions contain bug fixes and minor changes.

**What does a 'breaking change' mean?**
A “breaking change” is a change that breaks existing features or is incompatible with previous versions. In such cases, the MAJOR version is increased and users should be aware of potential customizations.

**Why is there an 'Unreleased' section?**
The “Unreleased” section shows changes that are already in development but have not yet been published in an official release.

**What do the symbols mean?**

> **Legend of the symbols:**  
> - 🚀 **Added:** New features and functions  
> - 🔄 **Changed:** Improvements and customizations  
> - 🐛 **Fixed:** Bug fixes  
> - 🎉 **First release:** Initial launch of the project
> - 🛠️ **Breaking Changes**: Changes that affect existing functions and are incompatible
> - 🎉 **First publication**: The start of the project
> - 🔒 **Security**: Safety-related changes
---

> **Tip:**  
> Use the issue tracking on GitHub for questions or suggestions for improvements to the project, and always keep the changelog up to date for the best possible transparency!