VENV_DIR = mongo_script


all: install

$(VENV_DIR)/bin/activate: 
	python3 -m mongo_script $(VENV_DIR)

install: $(VENV_DIR)/bin/activate
	. $(VENV_DIR)/bin/activate
	pip install pre-commit-hooks
	pip install wheel
	pip install setuptools
	pip install twine

precommit: $(VENV_DIR)/bin/activate
	. $(VENV_DIR)/bin/activate
	pre-commit install
	pre-commit run --all-files 	

build_packages: $(VENV_DIR)/bin/activate
	source $(VENV_DIR)/bin/activate
	python3 setup.py bdist_wheel sdist 

test_packages: $(VENV_DIR)/bin/activate
	. $(VENV_DIR)/bin/activate
	twine check dist/*

upload_packages: $(VENV_DIR)/bin/activate
	. $(VENV_DIR)/bin/activate
	twine upload -r testpypi dist/*
	twine upload dist/*

build_export_docker_image:
	docker build -f dockerfile-exporter . 

build_import_docker_image:
	docker build -f dockerfile-importer . 

clean:
	rm -rf $(VENV_DIR)

.PHONY: all install precommit package_test package_upload  clean
