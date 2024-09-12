# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.155.1/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version: 2.1.0-latest, 2.2.0-latest
ARG VARIANT="2.2.0-latest"
FROM checkmk/check-mk-cloud:${VARIANT}

ARG USERNAME=cmk
ARG USER_UID=501
ARG WORKSPACE=/workspaces/checkmk_fortigate

RUN /docker-entrypoint.sh /bin/true

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends nodejs gcc mlocate

RUN usermod --uid $USER_UID $USERNAME \
    && mkdir -p ${WORKSPACE} \
    && chown -R ${USERNAME}:${USERNAME} ${WORKSPACE}

USER $USERNAME

ADD requirements.txt /tmp/requirements.txt
RUN PATH="/omd/sites/cmk/bin:${PATH}" \
    OMD_ROOT="/omd/sites/cmk" \
    /omd/sites/cmk/bin/pip3 install -r /tmp/requirements.txt

ENTRYPOINT ["/bin/bash"]
