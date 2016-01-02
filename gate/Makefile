.PHONY: all

DEV_IMAGE := seckilling/gate$(if $(GIT_BRANCH),:$(GIT_BRANCH))

BIND_DIR := "dist"
GATE_MOUNT := -v "$(CURDIR)/$(BIND_DIR):/go/src/github.com/Dataman-Cloud/seckilling/gate/$(BIND_DIR)"
INTEGRATION_OPTS := -v "/var/run/docker.sock:/var/run/docker.sock"

DOCKER_RUN_GATE := docker run --rm $(INTEGRATION_OPTS) -it $(GATE_MOUNT) "$(DEV_IMAGE)"
default: binary


binary: build
	$(DOCKER_RUN_GATE) ./script/make.sh generate binary

shell: build
	$(DOCKER_RUN_GATE) /bin/bash

image:
	docker build -t "$(DEV_IMAGE)" .

dist:
	mkdir dist

build: dist
	docker build -t "$(DEV_IMAGE)" -f build.Dockerfile .

build-no-cache: dist
	docker build --no-cache -t "$(DEV_IMAGE)" -f build.Dockerfile .