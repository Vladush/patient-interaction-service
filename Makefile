.PHONY: up down test clean logs shell

up:
	docker compose up --build -d

down:
	docker compose down

test:
	docker compose run --rm api pytest

logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

shell:
	docker compose run --rm api /bin/bash
