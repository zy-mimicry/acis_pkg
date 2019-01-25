#! /bin/bash

if [ "x$WORKSPACE" == "x" ]; then
	echo "> &_& Please execute 'envs_setup.sh' firstly"
	exit 0
fi

function usage(){
	echo -e "\nOFFLINE HELP"
	echo -e "- Usage   :  $0 --name [or -n] \"testcase_name_01 testcase_name_02 ...\" [--times num.]  (NOT end with .py)"
	echo -e "- Example :  $0 --name \"ACIS_A_D_LSBUS_I2C_TEST\" --times 1\n"
}

if [ "$#" -eq "0" ];then
	usage
	exit -1
fi

ARGS=`getopt -o n:t: --long name:,times:, -n "$0" -- "$@"`

if [ $? != 0 ]; then
    echo "> &_& getopt cmds parse error."
	usage
    exit -1
fi

eval set -- "${ARGS}"

case_list=""
test_times=""

while true
do
    case "$1" in
        -n|--name)
            echo "* Test Case List: [$2]";
            case_list=$2
            shift 2
            ;;
		-t|--times)
            echo "* Each Case Test Times: [$2]";
            test_times=$2
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "> &_& Interal parse ERROR!"
            exit 1
            ;;
    esac
done

for arg in $@
do
    echo "* Useless parameters, throw away. [$arg]"
done

if [ "x$case_list" == "x" ]; then
    echo "> &_& Test Case List is [empty], please follow the command line format as below:"
	usage
    exit -1
fi

if [ "$test_times" == "" ]; then
    echo "> &_& Test Times is [empty], default pass 1,"
	test_times="1"
fi

py_case_list=""

# make sure unique for test case file.
for casename in ${case_list[@]};do

	count=`find -L $WORKSPACE/cases -name "$casename.py" | wc -l`
	if [ "$count" -gt "1" ]; then
		echo -e "\n> &_& Multiple testcases were found [$casename], please delete the unwanted test case files."
		echo -e "$casename\n"
		exit -1

	elif [ "$count" -eq "0" ]; then
		echo -e "\n> &_& NOT found the test case [$casename], maybe you should develop a new test case."
		exit -1
	fi
	testcase=`find -L $WORKSPACE/cases -name "$casename.py"`
	py_case_list=$py_case_list" $testcase"
done


echo "* clean $WORKSPACE/cases python cache."
py3clean $WORKSPACE/cases

echo "* clean $WORKSPACE/Dresults/* cache."
rm -f $WORKSPACE/Dresults/*

echo "* Current Test Case List : [$case_list]"
pytest -s $py_case_list --alluredir ./Dresults --count $test_times

OK="$?"
if [ "$OK" -ne "0" ]; then
	echo "> &_& ACIS OFFLINE TEST - [FAIL]."
	exit -1
fi

echo -e "\n* Generate report ...."
allure generate ./Dresults -o ./Dreport --clean
echo -e "* Allure report generated.\n"

