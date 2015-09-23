###############################################################################
#
# Common Makefile for building Python Debian packages
#
# This script assumes that the current project implements a "setup.py" file
# in the root folder, following the python Standards.
#
# Directories should be defined in ROOT Make file, and then include this file.
#
# Useful Targets:
# - all: (default) Builds the Python project and outputs it to build/output
# - install: Installs the Python project on the current host
# - deb: Builds a DEB file in "dist"
#
###############################################################################
# Project specific Config
###############################################################################

### THIS MUST BE DEFINED IN MAIN MAKE FILE
# The output deb filename
DPKG_DEBFILE := blackflow.deb

# The target location for installation. (if not defined,
# If not defined, the default library path is used.
INSTALL_PATH = /usr/lib/blackflow

###############################################################################
# Generic Config (SHOULD NOT BE EDITED)
###############################################################################

# Root folder for DPKG structure template
DPKG_ROOT    := scripts/debian/dpkg-root
DIST         := dist

# Directories to use for building
SRC_MAIN     := src-main
BUILD        := build
BUILD_OUT    := $(BUILD)/output

# The destination dir for installed package
PKG_TARGET   := $(BUILD)/target

###############################################################################

# Get version from VERSION file
version=$(strip `cat VERSION`)

# Temporary install path for Package Building
installbuildpath:=$(BUILD)/tmp-install

# DEB build file paths
debctrlfile=$(PKG_TARGET)/DEBIAN/control
debfilepath:=$(DIST)

# Install options variable
python_inst_opts:=
python_inst_path:=$(PKG_TARGET)
python_inst_post:=

# If a install path is defined, we need to apply some extra configuration
ifdef INSTALL_PATH
	python_inst_opts:= --install-purelib . --install-script .
	python_inst_path:=$(strip $(python_inst_path))$(strip $(INSTALL_PATH))
	python_inst_post:=rm -rfv $(installbuildpath)/*.egg-info
endif

# START OF MAKE FILE LOGIC

.PHONY: build build-install build-deb install-pkg-setup install deb clean

# Default target is build, which does not do much in this case
all: build

# Main target build. Will create a snapshot of project in out folder
build:
	@echo "BUILDING Python project to: $(BUILD_OUT)"
	python setup.py build_py -d $(BUILD_OUT)
	@echo "BUILD Complete!"

# Pre-configure install target to install without compilation in Package target
install-pkg-setup:
	@echo "CONFIGURING Python Project Packet installation."
	$(eval python_inst_opts+= --no-compile --root $(installbuildpath))

# Installs python project to configured location (default, install on local host)
install:
	@echo "INSTALLING Python Project..."
	python setup.py install $(python_inst_opts)
	@echo "INSTALL Complete!"

# Moves installed package data to packet relative target location
install-pkg-move:
	@echo "PACKAGE INSTALL Cleaning up Rotten eggs..."
	$(python_inst_post)
	@echo "PACKAGE INSTALL Copying installed files to target: $(python_inst_path)"
	mkdir -p $(python_inst_path)
	cp -rv $(installbuildpath)/* $(python_inst_path)

# Builds project and prepares installation snapshot in PKG target
build-install: install-pkg-setup install install-pkg-move
	@echo "PACKAGE INSTALL Completed successfully"

# Builds DEB packet file structure, and substitutes the current version in control file
build-deb:
	@echo "BUILDING Debian Package Structure at: $(PKG_TARGET)"
	mkdir -p $(PKG_TARGET)
	cp -Hrv $(DPKG_ROOT)/* $(PKG_TARGET)
	@echo "SETTING package version: $(version)"
	sed -i "s/###@VERSION@###/$(version)/g" $(debctrlfile)

# Builds DEB packet and places it in dist folder
deb: build-deb build-install
	@echo "BUILDING Debian Package: $(debfilepath)"
	mkdir -p $(DIST)
	dpkg-deb --build $(PKG_TARGET) $(debfilepath)
	@echo "BUILDING Debian Package [$(debfilepath)] Complete!\n---------"
	dpkg-deb -I $(debfilepath)/*.deb

# Deletes all built file structures
clean:
	@echo "Cleaning build and dist..."
	rm -rfv $(BUILD) $(DIST)
	rm -rfv $(SRC_MAIN)/*.egg-info
	@echo "CLEAN Complete!"

###############################################################################

working_dir=$(shell pwd)
pylint_running_from_directory=src-main
nosetests_cmdline_params= -w ./src-test/ -v --config=nosetests.config

delete-existing-virtualenv:
	rm -rf venv
	@echo "..make delete-existing-virtualenv DONE"

create-new-virtualenv:
	virtualenv venv
	@echo "..make create-new-virtualenv DONE"

install-on-virtualenv:
	pip list
	pip install --download-cache=./.cache/pip -r venv.config
	pip list
	@echo "..make install-on-virtualenv DONE"

do-initial-cleanup:
	@echo "..make do-initial-cleanup, does remove files created by using make commands"
	rm VERSION || :
	rm /etc/smartly/* || :
	rm sloccount.sc || :
	rm pylint.log || :
	rm nosetests_xunit.xml || :
	rm nosetests_cover.xml || :
	rm .coverage || :
	@echo "..make do-initial-cleanup DONE"

do-create-version-file:
	git describe --tags | sed 's/-\(alpha\|beta\|rc\)/~\1/' | cut -c2- > VERSION
	@echo "..make do-create-version-file DONE"

do-count-lines-of-code:
	@echo "....count lines of code (sloccount)"
	@echo "....using PYTHONPATH=$(PYTHONPATH)"
	sloccount --duplicates --wide --details $(shell git ls-files) > ./sloccount.sc
	@echo "..make do-count-lines-of-code DONE"

do-check-coding-standard:
	@echo "..make do-check-coding-standard, using PYTHONPATH=$(PYTHONPATH)"
	pylint --output-format=parseable --reports=y --include-ids=y --generate-rcfile >> pylint.config
	pylint --version
	pylint --rcfile=pylint.config $(pylint_running_from_directory) >> pylint.log
	@echo "..make do-check-coding-standard DONE"

do-unittests-and-coverage:
	@echo "..make do-unittests-and-coverage, using PYTHONPATH=$(PYTHONPATH)"
	nosetests --version
	nosetests $(nosetests_cmdline_params)
	@echo "..make do-unittests-and-coverage DONE"

