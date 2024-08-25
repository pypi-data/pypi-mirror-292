ARG IMAGE_BASE=python:3-alpine
FROM $IMAGE_BASE

# Install dependencies
RUN apk add -q \
      git

# Install requirements
COPY --from='requirements' ./pages.txt /tmp/
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 \
 && pip3 install -q -r /tmp/pages.txt --no-cache-dir --upgrade \
 && rm -f /tmp/pages.txt
