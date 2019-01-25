#! /bin/bash

export WORKSPACE=$(cd $(dirname $0); pwd)
export ROOT_PATH=$(cd $WORKSPACE/../../; pwd)

# sometimes, hope slim self.

echo "* CLEAN ALL Python3 cache."
py3clean $ROOT_PATH/

echo "* CLEAN [$WORKSPACE/]"
echo "** clean Dresults"
rm $WORKSPACE/Dresults -rf
echo "** clean Dreport"
rm $WORKSPACE/Dreport  -rf
echo "** clean logs"
rm $WORKSPACE/logs     -rf
echo "** clean .pytest_cache"
rm $WORKSPACE/.pytest_cache -rf
echo "** clean cases directory"
rm $WORKSPACE/cases -rf
echo "** clean pytest.ini"
rm $WORKSPACE/pytest.ini -f
