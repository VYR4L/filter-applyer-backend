# Environment name
ENV_NAME ?= venv

# Makefile targets
.PHONY: help create run clean

# Display help
help:
	@echo "Makefile commands:"
	@echo "  create 	 - Create the environment from requirements.txt"
	@echo "  run    	 - Run the application inside environment"
	@echo "  clean  	 - Remove the environment"

# Create Conda environment
create:
	pip install -r requirements.txt

# Run application
run:
	uvicorn main:app --reload

# Remove environment
clean:
	rm -rf $(ENV_NAME)