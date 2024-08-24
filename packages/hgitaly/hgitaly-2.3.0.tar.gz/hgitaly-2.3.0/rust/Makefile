all: help

HGITALY_VERSION := $(shell cat ../hgitaly/VERSION)
MERCURIAL_SOURCE_REPO = dependencies/mercurial
MERCURIAL_SOURCE_REV := $(shell cat mercurial.rev)
MERCURIAL_SOURCE_REMOTE ?= https://foss.heptapod.net/mercurial/mercurial-devel

.PHONY: help
help:
	@echo "Makefile for RHGitaly development setup and packaging"
	@echo ""
	@echo "Available commands: "
	@echo "  make dev-dependencies:  prepare development dependencies"
	@echo "                          (hg-core, various resources)"
	@echo "  make src-tarball:       package the workspace as a tarball,"
	@echo "                          including all dependencies that "
	@echo "                          cannot be obtained from crates.io"
	@echo "  make ci-cd-src-tarball: make src-tarball and upload it"
	@echo
	@echo "Interesting variables: "
	@echo "  MERCURIAL_SHARE_FROM: if set, Mercurial sources repository"
	@echo "                        will be created (if needed) with"
	@echo "                        'hg share' from this given path."
	@echo "  MERCURIAL_SHARE_POOL: if set, Mercurial sources repository"
	@echo "                        will be cloned using the given path"
	@echo "                        as a share pool."

.PHONY: dev-dependencies
dev-dependencies: dependencies/mercurial/.hg
	hg -R $(MERCURIAL_SOURCE_REPO) pull -r $(MERCURIAL_SOURCE_REV) $(MERCURIAL_SOURCE_REMOTE)
	hg -R $(MERCURIAL_SOURCE_REPO) update --config commands.update.check=abort $(MERCURIAL_SOURCE_REV) --clean
	(cd $(MERCURIAL_SOURCE_REPO) && patch -p1 < ../mercurial.patch)

dependencies/mercurial/.hg:
ifdef MERCURIAL_SHARE_FROM
	hg share --noupdate $(MERCURIAL_SHARE_FROM) $(MERCURIAL_SOURCE_REPO)
else ifdef MERCURIAL_SHARE_POOL
	hg --config extensions.share= --config share.pool=${MERCURIAL_SHARE_POOL} clone --noupdate $(MERCURIAL_SOURCE_REMOTE) $(MERCURIAL_SOURCE_REPO)
else
	hg clone --noupdate $(MERCURIAL_SOURCE_REMOTE) $(MERCURIAL_SOURCE_REPO)
endif

.PHONY: src-tarball
src-tarball: dev-dependencies
	./src-tarball.sh ${HGITALY_VERSION}

.PHONY: tarball-compile
tarball-compile: src-tarball
	./build-from-tarball.sh ${HGITALY_VERSION}

.PHONY: ci-cd-upload
ci-cd-upload: tarball-compile
	../ci/upload-rhgitaly ${HGITALY_VERSION}
