# Makefile targets
.PHONY: help create run clean

# Display help
help:
	@echo "Makefile commands:"
	@echo "  create 	 - Create the environment with required packages"
	@echo "  run    	 - Run the application inside environment"

# Create environment
create:
	pip install -r requirements.txt

# Run application
run:
	uvicorn main:app --reload