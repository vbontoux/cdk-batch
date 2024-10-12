# build it
podman build -t batch-job .
# test it
podman run --rm -it localhost/batch-job