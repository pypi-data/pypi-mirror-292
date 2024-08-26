#					-*- mode: makefile-gmake -*-
# Makefile for greenland projects.
# Copyright (C) 2024  M E Leypold
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

DEVSCRIPTS-SEARCH-PATH = $(CURDIR)/../greenland-devscripts $(HOME)/my/devscripts $(GREENLAND_DEV_BASEPATH)/greenland-devscripts

.ONESHELL:

REQUIRED-FILES = $(sort .devscripts)
EXISTING-FILES = $(sort $(wildcard $(REQUIRED-FILES)))
MISSING-FILES  = $(strip $(filter-out $(EXISTING-FILES), $(REQUIRED-FILES)))

DEVSCRIPTS = $(firstword $(wildcard $(DEVSCRIPTS-SEARCH-PATH)))

ifneq ($(MISSING-FILES),)
  $(info MISSING-FILES (from devscripts):  ($(MISSING-FILES)).)
  $(info EXISTING-FILES (from devscripts): ($(EXISTING-FILES)).)
  DEVSCRIPTS = $(strip $(firstword $(wildcard $(DEVSCRIPTS-SEARCH-PATH))))
  ifeq ($(DEVSCRIPTS),)
    $(error No development scripts found on paths ($(DEVSCRIPTS-SEARCH-PATH)))
  else
    $(info Setting up from: $(DEVSCRIPTS))
    SHELL-OUT = $(shell "$(DEVSCRIPTS)/setup.sh" 2>&1)
    $(info ---)
    ifneq ($(SHELL-OUT),)
      $(info $(SHELL-OUT))
      $(info ---)
    endif
  endif
endif

include .devscripts/Rules.mk
