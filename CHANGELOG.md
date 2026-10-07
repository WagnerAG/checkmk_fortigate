# 📜 Changelog

> **Notice:**  
> All notable changes to this project are recorded in this document. This project uses [SemVer](https://semver.org/lang/de/) for version management.
> The format is based on [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

---

## [2.4.1] - 2026-10-06
This release is a backport of the latest CheckMK 2.5 release. It includes all the features and bug fixes for CheckMK 2.3+. 

## [2.4.0] - 2026-06-26
### 🚀 Added
- FortiSwitches: added Health Summary check evaluating component ratings (CPU, Memory, Temperature, PoE, Fan, PSU) from the new API endpoint; requires FortiOS 7.4+

### 🔄 Changed
- Due to compatibility issues, this project maintains two separate release tracks:
    - CheckMK 2.4.x → main branch → FortiOS Plugin name: v2.4.x
    - CheckMK 2.5.x → dedicated 2.5.x branch → FortiOS Plugin name: v2.5.x
- Declare Checkmk 2.4 release-line compatibility (`version.usable_until` set to `2.4.99`)
- Improved error handling in special agent for switches and authentication errors (issue [#24](https://github.com/WagnerAG/checkmk_fortigate/issues/24))

### 🐛 Fixed
- FortiSwitches:
  - adopted CPU, Memory, PoE, Health and Uptime checks for new API endpoint (health-status)
  - maintains backward compatibility with FortiOS 7.2
- Improved error handling in dhcp check (issue [#](https://github.com/WagnerAG/checkmk_fortigate/issues/15))
- Fix wrong import for fortios_inventory (issue [#](https://github.com/WagnerAG/checkmk_fortigate/issues/33))
  - Note: Due to API changes introduced by Fortinet between versions 7.4 and 7.6, the Inventory view is fully supported only on FortiOS 7.6. On FortiOS 7.4, some information may be unavailable
- prevent crashes on unlicensed hardware and improve license check robustness

## [2.0.4] - 2026-05-06
### 🚀 Added
- New check to monitor certificate expiration

### 🔄 Changed
- Declare Checkmk 2.5 release-line compatibility (`version.usable_until` set to `2.5.99`).
- Update development and CI container images to Checkmk 2.5 image names.

### 🐛 Fixed
- Fix FortiOS inventory GUI view loading on Checkmk 2.5 by importing `UserId` from `cmk.ccc.user`.
- Fix FortiOS inventory view metadata for Checkmk 2.5 by using `main_menu_search_terms`.

## [2.0.3] - 2026-03-31
### 🚀 Added
- Implemented firmware checks (separate services for Model and Serial Number) from @realarna
 https://github.com/realarna/CheckMK_Fortigate_API_Monitoring

### 🐛 Fixed
- Issue with managed switch checks: The check crashes when switches are disconnected
- Fix DHCP scope check issue with datatype

## [2.0.2] - 2026-03-14
### 🐛 Fixed
- Fix DHCP scope check issue with datatype

### 🔄 Changed
- Breaking Change: Add VDOM functionality to IPSec Check, the service name changes and contains now the VDOM name.

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
