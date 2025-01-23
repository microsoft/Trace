.PHONY: help doc doc-deploy

help:
	@echo "Makefile for managing Jupyter Book documentation and deployment"
	@echo ""
	@echo "Usage:"
	@echo "  make doc            - Build the documentation"
	@echo "  make doc-deploy     - Deploy the documentation to GitHub Pages"
	@echo "  make help           - Display this help message"
	@echo ""
	@echo "For more information, refer to the README or script documentation."

doc:
	@echo "Building documentation..."
	@bash ./docs/jupyter_build.sh

doc-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	@ghp-import -n -p -f docs/_build/html