.PHONY: clean-cache clean-db clean-logs

clean: clean-cache clean-db clean-logs

clean-cache:
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +

clean-db:
	rm -f /private/tmp/test.db

clean-logs:
	rm -f logs/*
