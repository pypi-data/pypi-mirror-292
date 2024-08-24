#!/bin/sh

set -e

if [ -z "$1" ]; then
    echo "usage: $0 HGITALY_VERSION";
    exit 1
fi

HGITALY_VERSION=$1

set -u

DIST_HGITALY=hgitaly-${HGITALY_VERSION}
DIST_RHGITALY=rhgitaly-${HGITALY_VERSION}
TARBALL=${DIST_RHGITALY}.tgz

cd `dirname $0`

mkdir -p ../dist
cd ../dist
DEPS_DIR=../rust/dependencies

rm -rf ${DIST_HGITALY} ${DIST_RHGITALY}

echo "Performing extractions"
hg archive ${DIST_HGITALY}

rm -f ${DIST_HGITALY}/rust/dependencies/hg-core # cp -Lrf cannot do this
cp -Lr ${DEPS_DIR}/hg-core ${DIST_HGITALY}/rust/dependencies
mkdir ${DIST_HGITALY}/rust/mercurial/
# a bit lame for this file not to be under rust/dependencies,
# but that is the result of the relative path in hg-core/src/config/mod.rs,
# we're lucky it does not climb up outside of our package root.
cp ${DEPS_DIR}/mercurial/mercurial/configitems.toml \
   ${DIST_HGITALY}/rust/mercurial/

mkdir -p ${DIST_RHGITALY}/hgitaly
for path in hgitaly/VERSION protos rust; do
    cp -r ${DIST_HGITALY}/${path} ${DIST_RHGITALY}/${path}
done

echo "Creating tarball"
tar czf ${TARBALL} ${DIST_RHGITALY}

echo "Removing temporary directories ${DIST_HGITALY} and ${DIST_RHGITALY}"
rm -rf ${DIST_HGITALY} ${DIST_RHGITALY}

echo "tarball available in `realpath ${TARBALL}`"
