PWD=$(shell pwd)
PORT=8010
USER=app

run-rebuild: build run

run:
	docker run -it -p $(PORT):$(PORT) \
	--mount type=bind,source=$(PWD)/app,target=/home/$(USER)/app \
	lnk python main.py

build:
	docker build -t lnk .