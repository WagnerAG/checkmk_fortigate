# Checkmk special agent Fortinet

<div align="center">
<br />

![build](https://github.com/WagnerAG/checkmk_fortigate/workflows/build/badge.svg)
![Lint](https://github.com/WagnerAG/checkmk_fortigate/workflows/Lint/badge.svg)
![pytest](https://github.com/WagnerAG/checkmk_fortigate/workflows/pytest/badge.svg)

</div>

<div align="center">
  CheckMK special agent extension for Fortigate Firewalls and Switches
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

* To [ELLR](https://github.com/ellr/) he supported us and carried out code reviews
* To [yogibaer75](https://github.com/yogibaer75) he answered many of our questions at the CheckMK conference.

## Plugin download

See [GitHub build action](https://github.com/WagnerAG/checkmk_fortigate/actions/workflows/build.yml), where you can download the latest .mkp file.

* Click on the latest run
* Download the artifact at the bottom of the site

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
2. Search for FortiOS special angent and configure a rule
3. Confirgure the rule for your needs:
    - API Token: `TOKEN YOUR CREATED ABOVE`
    - Port: 8443 is default
    - SSL certificate checking: it's recommended to trust the certificate via CheckMK and not to deactivate the checks!
    - Timeout: you may leave at default value, please increase in case of slow WAN

### DCD Configuration for Network Switches

To have the piggyback data delivered, the DCD must be set up.

Go to `Setup` &rarr; `DCD` (dynamic configuration daemon)
- Title: `local`
- SIte: `cmk`
- Connector type: `Piggyback data`
- Sync interval: `1min`
- Create hosts in: `Main`
- Discovery services during creation: `Selected`

### Configure Inventory Rule

To use the inventory, you have to create a rule.\
Go to `Setup` &rarr; `HW/SW inventory rules` &rarr; `Do hardware/software inventory`\
Specify the settings to fit your needs.


### Switchport Monitoring

To monitor switch ports, the following should be noted:

 - If the `FortiOS Switch Interface Discovery` rule is not configured, all interfaces will be discovered.
 - If the rule is configured, a pattern must be specified for the description.
 - Currently, the description is visible in the service summary output. This should be changed later.
 - Currently, all interface data is output in 'Service Details'. This makes debugging easier.


# Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

## Contribution

See CONTRIBUTING.md

## Special Agent Call

To call the special agent manually, please use this command.
```
 /opt/omd/sites/cmk/bin/python3 agent_fortios.py --api-token <TOKEN> --port 8443 --no-cert-check <HOST_IP>
```

## Directories

The following directories in this repo are getting mapped into the Checkmk site.

* `agents`, `checkman`, `checks`, `doc`, `inventory`, `notifications`, `pnp-templates`, `web` are mapped into `local/share/check_mk/`
* `agent_based` is mapped to `local/lib/check_mk/base/plugins/agent_based`
* `nagios_plugins` is mapped to `local/lib/nagios/plugins`
* `bakery` is mapped to `local/lib/check_mk/base/cee/plugins/bakery`
* `temp` is mapped to `local/tmp` for storing static agent output

## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

### Github Workflow

The provided Github Workflows run `pytest` and `ruff` in the same checkmk docker container as vscode.
