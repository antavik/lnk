PWD=$(shell pwd)
PORT=8010
USER=app
TOKEN=token

.PHONY all dev build

all: build dev

dev:
	docker run -it -p $(PORT):$(PORT) \
	-e TOKEN=$(TOKEN) \
	--mount type=bind,source=$(PWD)/app,target=/home/$(USER)/app \
	lnk python main.py

build:
	docker build -t lnk .