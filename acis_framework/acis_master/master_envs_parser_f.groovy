#! /usr/bin/env groovy


/* Show all ACIS framework environments : visible and invisible */
def show(){
    println("""
    === [Beg] All Envs Provided by User ===

[MAPS]
${env.MAPS}

[FILTER]
${env.FILTER}

[PLATFORM]
${env.PLATFORM}

[FW_UPDATE]
${env.FW_UPDATE}

[FW_VERSION]
${env.FW_VERSION}

[FW_IMAGE_PATH]
${env.FW_IMAGE_PATH}

[ACIS_DIFF]
${env.ACIS_DIFF}

[REPORT_PATH]
${env.REPORT_PATH}

[TESTCASE_PATH]
${env.TESTCASE_PATH}

[LOOP_TEST]
${env.LOOP_TEST}

[JOB_NAME]
${env.JOB_NAME}

[USERNAME]
${env.username}

    === [End] All Envs Provided by User ===
    """)
}

def strip_and_export(){

    /*User can provide, in other words, those are visible*/
    env.PLATFORM      = env.PLATFORM.trim()
    env.MAPS          = env.MAPS.trim()
    env.FILTER        = env.FILTER.trim()
    env.FW_UPDATE     = env.FW_UPDATE.trim()
    env.FW_VERSION    = env.FW_VERSION.trim()
    env.FW_IMAGE_PATH = env.FW_IMAGE_PATH.trim().replaceAll('_username_', "${env.username}")
    env.TESTCASE_PATH = env.TESTCASE_PATH.trim().replaceAll('_username_', "${env.username}")
    env.REPORT_PATH   = env.REPORT_PATH.trim().replaceAll('_username_', "${env.username}")
    env.LOOP_TEST     = env.LOOP_TEST.trim().replaceAll('_username_', "${env.username}")

    /*ACIS framework specially own, invisible*/
    env.ACIS_DIFF = new Date().format('yyyy_MM_dd_HH_mm_ss').toString()
}

return this
