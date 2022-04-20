# This Dockerfile is used to build an image in CI that's uploaded to Beaker.
# It's used only to test the `Beaker.image` functionality of creating and uploading images.

FROM python:3.10-alpine

# We use the commit SHA to ensure this image has unique layers to upload.
ARG COMMIT_SHA

# Install some random stuff so that we have a layer to upload.
RUN pip install requests PyYAML pydantic
