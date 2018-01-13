
buildApp: ## build and bundle app
	sh scripts/makeapp.sh

buildDocs: ## build docs
		(cd docs/ && make html)

buildDockerPY2: ## build python2 docker image
	echo "FROM python:2" | cat - Dockerfile.test.template > Dockerfile.py2
	docker build -f Dockerfile.py2 -t testpy2 .

buildDockerPY3: ## build python3 docker image
	echo "FROM python:3" | cat - Dockerfile.test.template > Dockerfile.py3
	docker build -f Dockerfile.py3 -t testpy3 .

test: ## test code
	py.test

lint: ## lint code
	flake8

testPY2: ## test with python2
	docker run testpy2 py.test /app/

testPY3: ## test with python3
	docker run testpy3 py.test /app/


testFunctional: ## run functional_tests
	py.test functional_tests/

deploy-fetch: ## fetch deploy repo
	rm -rf deployment
	git clone https://gist.github.com/befb8025b4fdf52d7db8391a1cbe0c22.git deployment

deploy-authorize: ## authorize gcloud
	echo $$GCLOUD_SERVICE_KEY | base64 --decode > $${HOME}/gcloud-service-key.json
	gcloud auth activate-service-account --key-file $${HOME}/gcloud-service-key.json
	gcloud config set project $$GCLOUD_PROJECT

deploy: export VERSION = $(git describe --always)
deploy: Env = probably.stable.world
deploy: ## deploy version
	echo Development Deployment "$$VERSION"

	echo "Uploading gs://stable-world-downloads/$(Env)/versions/$${VERSION}"
	gsutil  -h "Content-Type:text/plain" \
		cp ./bin/stable.world \
		   gs://stable-world-downloads/$(Env)/versions/$${VERSION}

	echo Uploading gs://stable-world-downloads/$(Env)/latest ...

	gsutil  -h "Content-Type:text/plain" \
		cp gs://stable-world-downloads/$(Env)/versions/$${VERSION} \
			 gs://stable-world-downloads/$(Env)/latest

release: ## upload release
	gsutil  -h "Content-Type:text/plain" cp gs://stable-world-downloads/rc gs://stable-world-downloads/latest

.PHONY: help

help: ## show this help and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
