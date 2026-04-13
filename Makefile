.PHONY: help run run-full run-annotation clean-runs show-config

CONFIG=config/config.yaml

help:
	@echo "Available targets:"
	@echo "  make run             - Run pipeline using current config.yaml mode"
	@echo "  make run-full        - Set mode to full_pipeline and run"
	@echo "  make run-annotation  - Set mode to annotation_only and run"
	@echo "  make clean-runs      - Remove generated run directories"
	@echo "  make show-config     - Print current execution mode from config"

run:
	python run_pipeline.py --config $(CONFIG)

run-full:
	sed -i 's/execution_mode: annotation_only/execution_mode: full_pipeline/' $(CONFIG)
	python run_pipeline.py --config $(CONFIG)

run-annotation:
	sed -i 's/execution_mode: full_pipeline/execution_mode: annotation_only/' $(CONFIG)
	python run_pipeline.py --config $(CONFIG)

clean-runs:
	rm -rf results/runs/*

show-config:
	grep -n "execution_mode:" $(CONFIG)