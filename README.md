# Checkmk special agent Fortinet

<div align="center">
<br />

![build](https://github.com/WagnerAG/checkmk_fortigate/workflows/build/badge.svg)
![Lint](https://github.com/WagnerAG/checkmk_fortigate/workflows/Lint/badge.svg)
![pytest](https://github.com/WagnerAG/checkmk_fortigate/workflows/pytest/badge.svg)

</div>

<div align="center">
  CheckMK special agent extension for Fortigate Firewalls, Switches and AccessPoints
  <br />
  <br />
  <a href="https://github.com/WagnerAG/checkmk_fortigate/issues/new?assignees=&labels=type+bug&template=bug_report.yaml&title=bug%3A+">Report a Bug</a>
  ·
  <a href="https://github.com/WagnerAG/checkmk_fortigate/issues/new?assignees=&labels=type+enhancement&template=feature_request.yaml&title=feat%3A+">Request a Feature</a>
</div>

<div align="center">
<br />

[![license](https://img.shields.io/badge/License-GPLv2-green?style=flat-square)](LICENSE)

[![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg?style=flat-square)](https://github.com/WagnerAG/checkmk_fortigate/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![made with hearth by WAGNER AG](https://img.shields.io/badge/made_with%20_%E2%99%A5-_by_WAGNER_AG-_?style=flat-square
)](https://github.com/WagnerAG)

</div>


## Special thanks

* To [dampfhamm3r](https://github.com/dampfhamm3r) he had the idea for the project and needed a lot of perseverance to work on it. 
* To [ELLR](https://github.com/ellr/) he supported us and carried out code reviews
* To [yogibaer75](https://github.com/yogibaer75) he answered many of our questions at the CheckMK conference.
* To thl-cmk who took the time to do a review.
* To [sva-mh](https://github.com/sva-mh) he contributed the first bugfixes for CheckMK 2.3.
* To bitwiz for helping to improve the special agent.


## Plugin download

See [GitHub Releases](https://github.com/WagnerAG/checkmk_fortigate/releases), where you can download the latest .mkp file.


## Description

This is the repository for the Fortinet Firewall Special Agent. Due to conflicts with the built-in CheckMK checks, the rules are renamed to FortiOS.


### CheckMK Permission Config for API

To create an API token for Checkmk, follow these steps:

1. Create an administrator profile:\
Go to `System` &rarr; `Admin Profiles` &rarr; `Create New`
    - Name: `checkmk-readonly`
    - Permissions: Set all to `Read`
    - Permit usage of CLI diagnostic commands: `False`

2. Create REST API Administrator:\
Go to `System` &rarr; `Administrators` &rarr; `Create New` &rarr; `REST API Administrator`
    - Username: `checkmk`
    - Administrator Profile: `checkmk-readonly` (or how you named it)
    - Virtual Domains: select all VDOMs
    - PKI Group: `False`
    - CORS Allow Origin: `False`
    - Trusted Hosts: `True` &rarr; enter the `IP OF YOUR CHECKMK INSTANCE`


### Configure the special agent

1. Install the plugin via Extensions
2. Create a password under `Setup` &rarr; `General` &rarr; `Passwords`
3. Search for FortiOS special angent and configure a rule
4. Adjust the rule according to your requirements:
    - API Token: choose `From password store`; select the password you just created
    - Port: `8443` is default
    - Certificate Verification: Specify if the certificate should be validated
    - Number of retries: retry attempts made by the special agent
    - Timeout for connection: you may leave at default value, please increase in case of slow WAN


### DCD Configuration for Network Switches

To have the piggyback data delivered, the DCD must be set up.

Go to `Setup` &rarr; `DCD` (dynamic configuration daemon)
- Title: `<DCD configuration name>`
- Site: `<CheckMK site>`
- Connector type: `Piggyback data`
- Sync interval: `1min`
- Create hosts in: `<Folder for piggyback hosts>`
- Discovery services during creation: `Selected`

### Configure Inventory Rule

To use the inventory, you have to create a rule.\
Go to `Setup` &rarr; `HW/SW inventory rules` &rarr; `Do hardware/software inventory`\
Specify the settings to fit your needs.


### Switch port Monitoring

To monitor switch ports, the following should be noted:

 - If no `FortiOS switch interface discovery` rule is configured, all interfaces will be discovered regardless of their state
 - When a rule is configured, a pattern can be specified; all switch ports whose description contains this pattern will be monitored.
 - Or, conversely, you can exclude interfaces from discovery if their description contains a specific string
 - You may choose to discover only interfaces with a switch port description


# Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.


## Contribution

See CONTRIBUTING.md


## Special Agent Call

First, create a password named <forti_api_token> in the CheckMK password store. Note the password ID.

To call the special agent manually, please use this command:
```
/opt/omd/sites/$USER/bin/python3 local/lib/python3/cmk_addons/plugins/fortios/special_agents/agent_fortios.py --api-token <forti_api_token_id>:var/check_mk/stored_passwords --port 8443 --no-cert-check <HOST_IP>
```


## Directories

The following directories in this repo are getting mapped into the Checkmk site.

* `cmk_addons/plugins/<package-name>` is being mapped into `<$OMD_ROOT>/local/lib/python3/cmk_addons/plugins/<package-name>`
* `lib` is being mapped into `<$OMD_ROOT>/local/lib/python3/cmk`
* `plugins_legacy` is being mapped into `<$OMD_ROOT>/local/share/check_mk`


## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.


### Github Workflow

The provided Github Workflows run `pytest` and `ruff` in the same checkmk docker container as vscode.
