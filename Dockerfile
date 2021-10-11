FROM python:3.9

ENV PIP_DEPENDENCIES wheel pipenv
ENV TICKIT_DIR /tickit

# Install pip dependencies
RUN python3.9 -m pip install --upgrade pip; \
    python3.9 -m pip install ${PIP_DEPENDENCIES}

# Copy tickit code into container
COPY . ${TICKIT_DIR}

# Install using pipenv
WORKDIR ${TICKIT_DIR}
RUN pipenv install --python python3.9 --system --deploy; \
    python3.9 -m pip install .

CMD ["python3.9", "-m", "tickit"]
