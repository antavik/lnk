PWD=$(shell pwd)
PORT=8010
USER=app
TOKEN=token
CLIPPER_URL=
CLIPPER_TOKEN=

.PHONY: all dev build

all: build dev

dev:
	docker run -it -p $(PORT):$(PORT) \
	-e TOKEN=$(TOKEN) \
	-e CLIPPER_URL=$(CLIPPER_URL) \
	-e CLIPPER_TOKEN=$(CLIPPER_TOKEN) \
	--mount type=bind,source=$(PWD)/app,target=/home/$(USER)/app \
	lnk python main.py

build:
	docker build -t lnk .