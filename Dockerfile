FROM python:3.8

ARG DBOT_ARGS
ARG ENVIRONMENT=production
ARG COMMIT=""

RUN useradd --create-home bambleweeny
USER bambleweeny
WORKDIR /home/bambleweeny

ENV GIT_COMMIT_SHA=${COMMIT}

COPY --chown=bambleweeny:bambleweeny requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

COPY --chown=bambleweeny:bambleweeny . .

COPY --chown=bambleweeny:bambleweeny docker/credentials-${ENVIRONMENT}.py credentials.py

# Download AWS pubkey to connect to documentDB
#RUN if [ "$ENVIRONMENT" = "production" ]; then wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem; fi

ENTRYPOINT .local/bin/newrelic-admin run-program python dbot.py $DBOT_ARGS
