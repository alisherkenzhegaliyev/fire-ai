IMAGE = fastapi-backend
CONTAINER = fastapi-backend
PORT = 8000

include .envrc
export

.PHONY: build run stop restart logs shell clean

build:
	docker build -t $(IMAGE) .

run:
	docker run -d \
		--name $(CONTAINER) \
		-p $(PORT):8000 \
		-e DATABASE_URL=$(DATABASE_URL) \
		-e DATABASE_NAME=$(DATABASE_NAME) \
		$(IMAGE)
	@echo "Running at http://localhost:$(PORT)"
	@echo "API docs at http://localhost:$(PORT)/docs"

stop:
	docker stop $(CONTAINER) && docker rm $(CONTAINER)

restart: stop run

logs:
	docker logs -f $(CONTAINER)

shell:
	docker exec -it $(CONTAINER) /bin/bash

clean:
	docker stop $(CONTAINER) 2>/dev/null || true
	docker rm $(CONTAINER) 2>/dev/null || true
	docker rmi $(IMAGE) 2>/dev/null || true