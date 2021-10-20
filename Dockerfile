##### Shared Environment stage #########################################################
FROM python:3.9 AS base

ENV PIP_DEPENDENCIES wheel pipenv
ENV TICKIT_DIR /tickit

# Install pip dependencies
RUN python3.9 -m pip install --upgrade pip; \
    python3.9 -m pip install ${PIP_DEPENDENCIES}

# Copy tickit code into container
COPY . ${TICKIT_DIR}
WORKDIR ${TICKIT_DIR}

##### Runtime Stage ####################################################################
FROM base AS runtime

WORKDIR ${TICKIT_DIR}
RUN pipenv install --python python3.9 --system --deploy; \
    python3.9 -m pip install tickit

CMD ["python3.9", "-m", "tickit"]

##### Developer Stage ##################################################################
FROM base AS developer

WORKDIR ${TICKIT_DIR}
RUN pipenv install --python python3.9 --system --deploy --dev; \
    python3.9 -m pip install tickit

CMD ["python3.9", "-m", "tickit"]
