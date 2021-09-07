.PHONY: build
build: ## Build the docker image
	docker build . -t slack_mr_bot

.PHONY: up
up: ## Run the container in detached mode
	docker run --env-file .env -d slack_mr_bot