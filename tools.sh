#!/bin/sh

#/ Usage: tools.sh
#/
#/ This script is intended to be run on our build machine in order to identify all available
#/ tools (by checking the dist's console-scripts) and building individual tools
#/ for each of them (in the form of a zipped up pex file). We will then upload all of these
#/ files to our S3 bucket.

set -ex

echo "tools.sh: beginning execution" >&2

usage() {
    grep "^#/" "$0" | cut -c"4-" >&2
    exit "$1"
}

SKIP=""

while [ "$#" -gt 0 ]
do
    case "$1" in
        -s|--skip-upload) SKIP="echo Skipping: "; shift ;;
        -h|--help) usage 0;;
        -*) usage 1;;
        *) break;;
    esac
done

trap "$SKIP rm -rf ./dist; rm -f ./console_scripts.txt; rm -f ./version.txt" EXIT INT QUIT TERM

./bin/bootstrap-python --wipe
. ./.virtualenv/bin/activate

python -c 'from __future__ import print_function; import pkg_resources; [print(ep) for ep in pkg_resources.iter_entry_points(group="console_scripts")]' \
  | grep tools \
  | tr -d ' ' \
  > ./console_scripts.txt

mkdir -p ./dist

set +x
echo "Found these available tools:"
set -x
cat ./console_scripts.txt

git rev-parse HEAD > ./version.txt
$SKIP /usr/local/bin/s3-upload tools-bucket ./version.txt $BUILD_NUMBER

# Create the pex intended to be used as interpreter and repl
pex . -o "./dist/tools.pex"
$SKIP /usr/local/bin/s3-upload tools-bucket "./dist/tools.pex" $BUILD_NUMBER

while read TOOL; do
  bin=$(echo "$TOOL" | cut -d'=' -f1)
  ep=$(echo "$TOOL" | cut -d'=' -f2)
  "$(dirname "$0")/repex.sh" "./dist/tools.pex" "$ep" "./dist/$bin"
  $SKIP /usr/local/bin/s3-upload tools-bucket "./dist/${bin}" $BUILD_NUMBER
  printf '\033[1;32m%s OK\033[0m\n' "${TOOL}"
done < ./console_scripts.txt

ls ./dist

$SKIP /usr/local/bin/environment-upgrade dev tools-bucket $BUILD_NUMBER
$SKIP /usr/local/bin/environment-upgrade prod tools-bucket $BUILD_NUMBER
