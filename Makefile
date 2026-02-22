OLLAMA_NUM_PARALLEL ?= 4
OLLAMA_FLASH_ATTENTION ?= 1

.PHONY: ollama backend frontend dev

ollama:
	OLLAMA_NUM_PARALLEL=$(OLLAMA_NUM_PARALLEL) \
	OLLAMA_FLASH_ATTENTION=$(OLLAMA_FLASH_ATTENTION) \
	ollama serve

backend:
	cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Start each service in a separate terminal:"
	@echo "  make ollama"
	@echo "  make backend"
	@echo "  make frontend"
