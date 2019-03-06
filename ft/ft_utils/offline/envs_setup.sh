#! /bin/bash

export WORKSPACE=$(cd $(dirname $0); pwd)
export ROOT_PATH=$(cd $WORKSPACE/../../; pwd)

export PYTHONPATH=$ROOT_PATH
export ACIS_DIFF=$(date "+%Y_%m_%d_%H_%M_%S")
export DESCRIPTION="OFFLINE TEST"
export PLATFORM=offline
export REPORT_PATH=$WORKSPACE/logs
#Just Debug one by one
export TIMES=1

echo -e "\n=== Setup Environments for ACIS-OFFLINE-TEST ==="
echo "> WORKSAPCE:    $WORKSPACE"
echo "> ROOT_PATH:    $ROOT_PATH"
echo "> PYTHONPATH:   $PYTHONPATH"
echo "> ACIS_DIFF:    $ACIS_DIFF"
echo "> PLATFORM:     $PLATFORM"
echo "> REPORT_PATH:  $REPORT_PATH"
echo "> DESCRIPTION:  $DESCRIPTION"
echo "> TIMES:        $TIMES"
echo ""

if [ ! -d "$WORKSPACE/cases" ]; then
	echo -e "* cases directory NOT exists in $WORKSPACE, make it."
	mkdir -p $WORKSPACE/cases
else
	echo -e "* case directory already exists in $WORKSPACE, remove it and new one."
	rm -rf $WORKSPACE/cases/*
fi

echo -e "* duplicate test case files to [$WORKSPACE/cases]"
rsync -av \
	--exclude=ft_utils \
	--exclude=ft_template \
	--exclude=PEP-0008.txt \
	--exclude=acis_dispatch_map.txt \
	--exclude=slave_label_description.txt \
	$ROOT_PATH/ $WORKSPACE/cases

if [ ! -d "$WORKSPACE/logs" ]; then
	echo -e "* $WORKSPACE/logs NOT exists, make it. "
	mkdir -p $WORKSPACE/logs
fi

if [ ! -d "$WORKSPACE/Dresults" ]; then
	echo -e "* $WORKSPACE/Dresults NOT exists, make it."
	mkdir -p $WORKSPACE/Dresults
fi

if [ ! -d "$WORKSPACE/Dreport" ]; then
	echo -e "* $WORKSPACE/Dreport NOT exists, make it."
	mkdir -p $WORKSPACE/Dreport
fi

echo -e "* $WORKSPACE/pytest.ini file is forced to update from [$ROOT_PATH/ft_utils/pytest_injection/pytest.ini]"
cp -ar $ROOT_PATH/ft_utils/pytest_injection/pytest.ini $WORKSPACE

echo -e "* $WORKSPACE/cases/conftest.py file is forced to update from [$ROOT_PATH/ft_utils/pytest_injection/conftest.py]"
cp -ar $ROOT_PATH/ft_utils/pytest_injection/conftest.py $WORKSPACE/cases/conftest.py

rule_file='/etc/udev/rules.d/11-acis.rules'
if [ ! -e "$rule_file" ]; then
	echo -e "\n* The rule file[$rule_file] is not found, enter command 'sudo acis_make_rules.py' and follow the prompts to complete the port configuration."
else
	echo -e "\n* Maybe you should double-check your rule-file[$rule_file] of udev, and make sure the configuration is correct."
fi


echo ""
PS1="(ACIS OFFLINE TEST) \u@\h \w \$ " $SHELL --login --noprofile
echo "Bye~ ^_^"

