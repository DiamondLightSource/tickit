##### Shared Environment stage #########################################################
FROM registry.hub.docker.com/library/python:3.7 AS base

ENV PIP_DEPENDENCIES wheel pipenv
ENV TICKIT_DIR /tickit

# Install pip dependencies
RUN rm -rf /usr/bin/python3.9; \
    python3.7 -m pip install --upgrade pip; \
    python3.7 -m pip install ${PIP_DEPENDENCIES}

# Copy tickit code into container
COPY . ${TICKIT_DIR}
WORKDIR ${TICKIT_DIR}

##### Runtime Stage ####################################################################
FROM base AS runtime

WORKDIR ${TICKIT_DIR}
RUN pipenv install --python python3.7 --system --deploy; \
    python3.7 -m pip install tickit

CMD ["python3.7", "-m", "tickit"]

##### Developer Stage ##################################################################
FROM base AS developer

WORKDIR ${TICKIT_DIR}
RUN pipenv install --python python3.7 --system --deploy --dev; \
    python3.7 -m pip install tickit

CMD ["python3.7", "-m", "tickit"]
