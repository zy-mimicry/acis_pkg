#! /bin/bash
# coding=utf-8

export CASENAME='ACIS_A_S_Reset_Linux_HW'
export PLATFORM='9X28'
export label='9X28&&QMI&&COMMON&&SYSTEM'
export FW_UPDATE='false'
export FW_VERSION='SWI9X40A_01.22.00.01'
export FW_IMAGE_PATH=/home/jenkins/nfs_acis/Integration_Test/fw_image
export TIMES=2
export TYPES='system'
export REPORT_PATH=/home/jenkins/nfs_acis/Integration_Test/log_and_report
export TESTCASE_PATH=/home/jenkins/nfs_acis/Integration_Test/acis_testcases/testcases
export LOOP_TEST=/home/jenkins/nfs_acis/Integration_Test/loop_test
export ACIS_DIFF=2018_11_29_11_02_51

echo "--------------------- ENVs Beg --------------------------"
echo "CASENAME: " $CASENAME
echo "PLATFORM: " $PLATFORM
echo "label: "    $label
echo "FW_UPDATE: " $FW_UPDATE
echo "FW_VERSION: " $FW_VERSION
echo "FW_IMAGE_PATH: " $FW_IMAGE_PATH
echo "TIMES: " $TIMES
echo "TYPES: " $TYPES
echo "REPORT_PATH: " $REPORT_PATH
echo "TESTCASE_PATH: " $TESTCASE_PATH
echo "ACIS_DIFF: " $ACIS_DIFF
echo "LOOP_TEST: " $LOOP_TEST
echo "--------------------- ENVs End --------------------------"


export PYTHONPATH=/home/jenkins/nfs_acis/acis_framework/acis_base

cd /home/jenkins/nfs_acis/acis_framework/acis_slave

echo "Current Path: "`pwd`

python3 ./acis_slave_main.py
