.ONESHELL:
.SILENT:
.phony: setup run

setup:
	uv sync

run:
	uv run python test.py
