# syntax=docker/dockerfile:1.7

ARG VICMF6_IMAGE=vic-mf6:manuscript
FROM ${VICMF6_IMAGE}

USER root
COPY requirements-workflow.txt /opt/requirements-workflow.txt
RUN /opt/venv/bin/python -m pip install --no-cache-dir \
        --requirement /opt/requirements-workflow.txt \
    && rm -f /opt/requirements-workflow.txt

COPY manuscript /opt/vic-mf6-workflow/manuscript
COPY examples /opt/vic-mf6-workflow/examples
COPY scripts /opt/vic-mf6-workflow/scripts
RUN chown -R vicmf6 /opt/vic-mf6-workflow

USER vicmf6
WORKDIR /work
