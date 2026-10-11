.PHONY: up down logs licences keys

up:
	docker compose --profile dev up -d --wait

down:
	docker compose --profile dev down

logs:
	docker compose --profile dev logs -f

licences:
	python -m pip_audit --version
	python -m piplicenses --version

keys:
	python scripts/gen_keys.py
