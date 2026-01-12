.PHONY: test test-cov docker-test

test:
	pytest app/tests/ -v

test-cov:
	pytest --cov=app --cov-report=term

docker-test:
	docker build -f Dockerfile.tests -t javer-tests .
	docker run --rm javer-tests
``
