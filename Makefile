.PHONY: build
build: ## Build the docker image
	docker build . -t slack_mr_bot

.PHONY: up
up: ## Run the container
	docker run --env-file .env slack_mr_bot