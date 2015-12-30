#!/usr/bin/env bash
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-12-22 23:39:33 +0000 (Tue, 22 Dec 2015)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon
#

set -euo pipefail
srcdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "
# ======================== #
# Testing validate_json.py
# ======================== #
"

cd "$srcdir/..";

. ./tests/utils.sh

until [ $# -lt 1 ]; do
    case $1 in
        -*) shift
    esac
done

rm broken.json single_quote.json missing_end_quote.json no_extension_testfile &>/dev/null || :
./validate_json.py -vvv $(
find "${1:-.}" -iname '*.json' |
grep -v '/spark-.*-bin-hadoop.*/' |
grep -v 'broken'
)
echo

echo "checking json file without an extension"
cp -iv "$(find "${1:-.}" -iname '*.json' | grep -v '/spark-.*-bin-hadoop.*/' | head -n1)" no_extension_testfile
./validate_json.py -vvv -t 1 no_extension_testfile
rm no_extension_testfile
echo

echo "testing stdin"
./validate_json.py - < tests/test.json
./validate_json.py < tests/test.json
./validate_json.py tests/test.json - < tests/test.json
./validate_json.py -m - < tests/multirecord.json
echo

echo "Now trying broken / non-json files to test failure detection:"
check_broken(){
    filename="$1"
    set +e
    ./validate_json.py "$filename" ${@:2}
    result=$?
    set -e
    if [ $result = 2 ]; then
        echo "successfully detected broken json in '$filename', returned exit code $result"
        echo
    #elif [ $result != 0 ]; then
    #    echo "returned unexpected non-zero exit code $result for broken json in '$filename'"
    #    exit 1
    else
        echo "FAILED, returned unexpected exit code $result for broken json in '$filename'"
        exit 1
    fi
}

set +e
./validate_json.py - -m < tests/test.json
result=$?
set -e
if [ $result = 2 ]; then
    echo "successfully detected breakage for --multi-line stdin vs normal json"
    echo
else
    echo "FAILED to detect --multi-line std vs normal json"
    exit 1
fi

echo blah > broken.json
check_broken broken.json
rm broken.json

echo "{ 'name': 'hari' }" > single_quote.json
check_broken single_quote.json

echo "checking specifically single quote detection"
set +o pipefail
./validate_json.py single_quote.json 2>&1 | grep --color 'JSON INVALID.*found single quotes not double quotes' || { echo "Failed to find single quote message in output"; exit 1; }
set -o pipefail
rm single_quote.json
echo

echo '{ "name": "hari" ' > missing_end_quote.json
check_broken missing_end_quote.json
rm missing_end_quote.json

check_broken README.md

cat tests/test.json >> tests/multi-broken.json
cat tests/test.json >> tests/multi-broken.json
check_broken tests/multi-broken.json
rm tests/multi-broken.json
echo "======="
echo "SUCCESS"
echo "======="

echo
echo