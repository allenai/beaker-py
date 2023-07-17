# This Dockerfile is used to build an image in CI that's uploaded to Beaker.
# It's used only to test the `Beaker.image` functionality of creating and uploading images.

FROM python:3.9-alpine

# We use the commit SHA to ensure this image has unique layers to upload.
ARG COMMIT_SHA

# Now do some other some other random stuff so that we have more layers to upload.
RUN echo ${COMMIT_SHA} > /out.log
RUN pip install --upgrade pip wheel build
RUN pip install requests pydantic
