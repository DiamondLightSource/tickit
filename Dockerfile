
# SORT OUT THIS #

##### Shared Environment stage #########################################################
FROM registry.hub.docker.com/library/python:3.7-slim AS base

ENV PIP_DEPENDENCIES wheel pipenv
ENV TICKIT_DIR /tickit

# Install pip dependencies
RUN rm -rf /usr/bin/python3.9
RUN python3.7 -m pip install --upgrade pip
RUN python3.7 -m pip install ${PIP_DEPENDENCIES}

# Copy tickit code into container
COPY . ${TICKIT_DIR}
WORKDIR ${TICKIT_DIR}

RUN pipenv install --python python3.7 --system --deploy

##### Runtime Stage ####################################################################
FROM registry.hub.docker.com/library/python:3.7-slim AS runtime

ENV TICKIT_DIR /tickit
WORKDIR ${TICKIT_DIR}

ENV PYTHON_SITE_PACKAGES /usr/local/lib/python3.7/site-packages

COPY --from=base ${PYTHON_SITE_PACKAGES} ${PYTHON_SITE_PACKAGES}
COPY . ${TICKIT_DIR}

RUN python3.7 -m pip install tickit

CMD ["python3.7", "-m", "tickit"]

##### Developer Base Stage #############################################################
FROM base AS base_dev

RUN pipenv install --python python3.7 --system --deploy --dev

##### Developer Stage ##################################################################
FROM registry.hub.docker.com/library/python:3.7-slim AS developer

ENV TICKIT_DIR /tickit
WORKDIR ${TICKIT_DIR}

ENV PYTHON_SITE_PACKAGES /usr/local/lib/python3.7/site-packages

COPY --from=base_dev ${PYTHON_SITE_PACKAGES} ${PYTHON_SITE_PACKAGES}
COPY . ${TICKIT_DIR}

RUN python3.7 -m pip install tickit

CMD ["python3.7", "-m", "tickit"]



# the new dockerfile



# This file is for use as a devcontainer and a runtime container
#
# The devcontainer should use the build target and run as root with podman
# or docker with user namespaces.
#
FROM python:3.11 as build

ARG PIP_OPTIONS=.

# Add any system dependencies for the developer/build environment here e.g.
# RUN apt-get update && apt-get upgrade -y && \
#     apt-get install -y --no-install-recommends \
#     desired-packages \
#     && rm -rf /var/lib/apt/lists/*

# set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# Copy any required context for the pip install over
COPY . /context
WORKDIR /context

# install python package into /venv
RUN pip install ${PIP_OPTIONS}

FROM python:3.11-slim as runtime

# Add apt-get system dependecies for runtime here if needed

# copy the virtual environment from the build stage and put it in PATH
COPY --from=build /venv/ /venv/
ENV PATH=/venv/bin:$PATH

# change this entrypoint if it is not the same as the repo
ENTRYPOINT ["python3-pip-skeleton"]
CMD ["--version"]
