.PHONY: samples tests clean

clean:
	@echo "Cleaning up..."
	rm -f samples/sample*

samples:
	@echo "Generating samples..."
	for spec in samples/spec-*; do \
			echo "Generating sample for $$spec"; \
			PYTHONPATH=../../.. python -m app.reports.portfolio.make --spec $$spec --org spyderdemo --api_key $$PROD_API_KEY --api_url https://api.spyderbat.com --output samples/sample --formats md,mdx ;  \
		done

