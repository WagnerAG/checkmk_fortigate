# 📜 Changelog

> **Notice:**  
> All notable changes to this project are recorded in this document. This project uses [SemVer](https://semver.org/lang/de/) for version management.
> The format is based on [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

---
## [2.0.1] - 2026-01-12
### 🔄 Changed
- License Check
  - Treat `no_license` antivirus state as `OK` during inventory
- HA Peer check refactored
  - only one service will be created (run service discovery!)
  - if no secondary information is found, state will become `WARN`
- Readme updated

### 🚀 Added
- Switch port discovery
 - add option to inventorize only interfaces with a matching description
- New `IPSec Client VPN <name>` check. The service is inventoried only when users are connected. Its state is always reported as `OK` and displays the currently connected users.
 - can be disabled &rarr; create discovery rule `FortiOS IPSec Client VPN discovery`

### 🐛 Fixed
- WiFi AP Check
  - fix crash if WiFi AP has no IP address
- Added dedicated rule for memory check (issue [#17](https://github.com/WagnerAG/checkmk_fortigate/issues/17))

## [2.0.0] - 2025-08-25
This marks the first release with official support for CheckMK 2.4.x.
### 🔄 Changed
- 🛠️ **Breaking Changes**<br>
This update introduces changes that are not compatible with existing configurations.<br>
Important: All breaking changes will require a reconfiguration of your existing rules.<br>
Make sure to document your current setup before updating the plugin, as previous configurations may no longer be supported or interpreted correctly after the update.
  - Special agent configuration:
    - SSL verification is now boolean
    - API keys are now stored in encrypted form
    - Specifying the IP address is no longer required
  - Fortigate interfaces:
    - new discovery rule:
      - include or exclude interfaces from monitoring based on their description, name or alias
  - Switch interfaces
    - new discovery rule:
      - include or exclude interfaces from monitoring based on their description
      - option to discover only switchports with a description
        - the rule to exclude interfaces by description still applies

- All WATO rules have been migrated to use the new API, polished help text
- Adjusted all pytests
- Fortigate interfaces are only discovered if their state is "up"
- Renamed parameter in DHCP scope usage levels rule to `FortiOS DHCP scope name`
- NTP default paramters for stratum changed to 8 (`WARN`) and 12 (`CRIT`)
- Forti AP check now uses built-in metrics for CPU and memory
- Migrated all Pydantic models to Pydantic V2

### 🚀 Added
- The view under "Inventory → FortiOS devices"
  - now supports searching by serial number
  - contains an EOS column for FortiSwitches and FortiAPs

### 🐛 Fixed
- NTP check is more reliable
- License check is more reliable
- Various small improvements

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