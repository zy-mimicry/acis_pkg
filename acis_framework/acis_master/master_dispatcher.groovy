#! /usr/bin/env groovy

/**/
/**/
/**/
/**/

def toLower(list){
    ArrayList tmp = []
    for (l in list){
        tmp.add(l.toLowerCase())
    }
    return tmp
}

def toUpper(list){
    ArrayList tmp = []
    for (l in list){
        tmp.add(l.toUpperCase())
    }
    return tmp
}

def trim_list(list){
    def i
    for (i = 0; i < list.size(); i++){
        list[i] = list[i].trim()
    }
}

class FilterTypeError extends Exception{
    public FilterTypeError (String msg){
        super("\n\n" + msg + "\n\n")
    }
}

class MapsItemParseException extends Exception{
    public MapsItemParseException (String msg){
        super("\n\n" + msg + "\n\n")
    }
}

def pick_line_types(item, list){

    groups = item.trim().split("!")

    types  = groups[2].split(":")[0].trim()
    types_v  = groups[2].split(":")[1].trim().split(",")

    def k
    if ( types == "types"){
        for (k = 0; k < types_v.size(); k++){
            /* Check the type with LowerCase */
            if (!list.grep(types_v[k].toLowerCase())){
                list.add(types_v[k].toLowerCase())
            }
        }
    }else{
        throw new MapsItemParseException("In ACIS_MAPS file, 'types' is needed, but your configure [" +  types + "]")
    }
}

def make_types_list(lines, list){
    /* input :                                                                                    */
    /*       - lines [] > file.text from ACIS_MAPS.txt                                            */
    /*       - eg. list = [ 'casename: BBB ! labels: spi,mm ! types: system,mmd ! times: 2;',     */
    /*                      'casename: AAA ! labels: spi,dd ! types: system,ssd ! times: 3;' ]    */
    /* output:                                                                                    */
    /*       - list [] > for types                                                                */
    /*       - eg. list = [ 'system', 'mmd', 'ssd' ]',                                            */

    def i
    for (i = 0 ; i < lines.size(); i++){
        pick_line_types(lines[i], list)
    }
}

def deal_line_item(item, maps){
    /* input :                                                                                          */
    /*       - item(line) > eg. casename: BBB ! labels: spi,mm ! types: system,mmd ! times: 2;          */

    /* output:                                                                                          */
    /*       - maps [:] > dict                                                                          */
    /*       - eg. maps = {'BBB' : {'labels' : ['spi', 'mm'], 'types' : ['system', 'mmd'], 'times' : 2}}*/

    groups = item.trim().split("!")

    name   = groups[0].split(":")[0].trim().toLowerCase()
    labels = groups[1].split(":")[0].trim().toLowerCase()
    types  = groups[2].split(":")[0].trim().toLowerCase()
    times  = groups[3].split(":")[0].trim().toLowerCase()

    name_v   = groups[0].split(":")[1].trim()
    ArrayList labels_v = groups[1].split(":")[1].trim().split(",")
    labels_v = toUpper(labels_v)
    types_v  = groups[2].split(":")[1].trim().split(",")
    times_v  = groups[3].split(":")[1].trim()

    if ( name == "casename"){
        maps[name_v] = [:]
    }else{
        throw new MapsItemParseException("In ACIS_MAPS file, 'casename' needed, but your configure [" +  name + "]")
    }
    if ( labels == "labels"){
        maps[name_v]["labels"] = labels_v
    }else{
        throw new MapsItemParseException("In ACIS_MAPS file, 'labels' needed, but your configure [" + labels + "]")
    }
    if ( types == "types"){
        maps[name_v]["types"] = types_v
    }else{
        throw new MapsItemParseException("In ACIS_MAPS file, 'types' needed, but your configure [" +  types + "]")
    }
    if ( times == "times"){
        maps[name_v]["times"] = times_v
    }else{
        throw new MapsItemParseException("In ACIS_MAPS file, 'times' needed, but your configure [" + times + "]")
    }
}


def MAPS_to_list(text){
    /* A list separated by semicolons(;) */
    /* eg...  A;B;C >> ["A", "B", "C"]   */

    if (text){
        return text.trim().split(";")
    }else{
        return []
    }
}

def make_curser_maps(list, curser, maps){
    /* input :                                                                                           */
    /*       - list [] < list                                                                            */
    /*       - eg. list = [ 'casename: BBB ! labels: spi,mm ! types: system,mmd ! times: 2;',            */
    /*                      'casename: AAA ! labels: spi,dd ! types: system,ssd ! times: 3;' ]           */

    /* output:                                                                                           */
    /*       - curser [] > list                                                                          */
    /*       - eg. curser = ['BBB', 'AAA'] (unique)                                                      */

    /*       - maps [:]  > dict                                                                          */
    /*       - eg. maps = {'BBB' : {'labels' : ['spi', 'mm'], 'types' : ['system', 'mmd'], 'times' : 2}, */
    /*                     'AAA' : {'labels' : ['spi', 'dd'], 'types' : ['system', 'ssd'], 'times' : 3}} */

    def i
    for (i = 0; i < list.size(); i++){
        curser.add(list[i].split("!")[0].split(":")[1].trim())
        deal_line_item(list[i], maps)
    }

    println maps
    println curser
}

def make_filter_maps(filter,
                     file,
                     maps,
                     maps_curser,
                     new_maps,
                     new_maps_curser){
    /* input:                                                                                           */
    /*      - filter "" < env.FILTER < eg. system,qmi                                                   */
    /*      - file ""   < ACIS_MAPS.txt text                                                            */
    /*      - maps [:]  <  ACIS_MAPS.txt to dict                                                        */
    /*      - eg. maps = {'BBB' : {'labels' : ['spi', 'mm'], 'types' : ['system', 'mmd'], 'times' : 2}, */
    /*                    'AAA' : {'labels' : ['spi', 'dd'], 'types' : ['system', 'ssd'], 'times' : 3}} */
    /*      - curser [] < list                                                                          */
    /*      - eg. curser = ['BBB', 'AAA'] (unique)                                                      */
    /* output:                                                                                          */
    /*       - new_maps >  just like other maps                                                         */
    /*       - new_maps_curser >  just like other curser                                                */

    def key_words = ['none', 'all', 'default']

    ArrayList filter_types

    if (filter.trim() == ""){
        filter_types = []
    }else{
        filter_types = filter.trim().split(',')
        trim_list(filter_types)
    }
    filter_types = toLower(filter_types)

    if ( filter_types.size() > 1 ){
        def i
        for (i = 0; i < key_words.size(); i++){
            if (filter_types.grep(key_words[i])){
                println "grep:" + key_words[i]
                throw new FilterTypeError("type: [" + key_words[i] + "] can't be used with other types.")
            }
        }
    }

    if (filter_types.size() == 0 || (filter_types.size() == 1 && filter_types[0] == "none")){
        println "Hook >> filter [none] or [empty]"
        new_maps = [:]
        new_maps_curser = []
        return
    }
    else if (filter_types.size() == 1 && (filter_types[0] == "default" || filter_types[0] == "all")){
        println "hook :" + filter_types[0]
        new_maps = maps
        new_maps_curser = maps_curser
        return
    }

    ArrayList types_list = []
    make_types_list(MAPS_to_list(file), types_list)
    types_list = toLower(types_list)  /* Maybe superfluous, but temporarily reserved*/

    println "[env.FILTER] : " + filter_types
    println "[ACIS_MAPS ALL TYPS]: " + types_list

    def i,c
    for(i = 0 ; i < filter_types.size(); i++){
        if (types_list.grep(filter_types[i])){
            for (c = 0 ; c < maps_curser.size(); c++){
                if (maps[maps_curser[c]]["types"].grep(filter_types[i])){
                    new_maps[maps_curser[c]] = maps[maps_curser[c]]
                    new_maps_curser.add(maps_curser[c])
                }
            }
        }else{
            throw new FilterTypeError("Please check your env.FILTER, framework can NOT know that [" + filter_types[i] + "]")
        }
    }
}

def remove_dup_self(maps_curser){ /*curser must be a list or support unique() method.*/
    maps_curser.unique()
}

def merge_maps(maps,
               maps_curser,
               maps_filter,
               maps_filter_curser,
               maps_merged,
               maps_merged_curser){
    /* env.MAPS will overwrite items in env.FILTER */

    remove_dup_self(maps_curser)
    remove_dup_self(maps_filter_curser)

    def overwrite = []
    def a,c,d,g

    for (a = 0; a < maps_curser.size(); a++ ){
        for (b = 0; b < maps_filter_curser.size(); b++){
            if (maps_curser[a] == maps_filter_curser[b]){
                overwrite.add(maps_curser[a])
            }
        }
    }

    println "[OverWrite item] : " + overwrite

    for (c = 0; c < maps_filter_curser.size(); c++){
        for (d = 0; d < overwrite.size(); d++){
            if (maps_filter_curser[c] != overwrite[d]){
                maps_merged[maps_filter_curser[c]] = maps_filter[maps_filter_curser[c]]
                maps_merged_curser.add(maps_filter_curser[c])
            }
        }
    }

    for(g = 0; g < maps_curser.size(); g++){
        maps_merged[maps_curser[g]] = maps[maps_curser[g]]
        maps_merged_curser.add(maps_curser[g])
    }
}

/* If you add some envs, please modify here
 * For 'Linux', environments should be Upper, Just like 'PLATFORM'*/
def make_testplan(maps, curser, testplan){
    /**/

    def list = []
    def i


    for(i = 0; i < curser.size(); i++){

        if (env.username == null){
            maps[curser[i]]["labels"].add(env.PLATFORM) /* PLATFORM different 9x or 8x platform */
        }else{
            maps[curser[i]]["labels"] = [env.username.toUpperCase()] /* 'labels' should be username*/
            list.add([$class : "StringParameterValue", "name": "USER_NAME", "value": env.username])
        }

        /* MAPS and FILTER range */
        list.add([$class : "StringParameterValue", "name": "CASENAME", "value": curser[i]])
        /* Please set 'label' to lower case. */
        list.add([$class : "LabelParameterValue",  "name": "label", "label": maps[curser[i]]["labels"].join("&&")])
        list.add([$class : "StringParameterValue", "name": "TIMES", "value": maps[curser[i]]["times"].toString()])
        list.add([$class : "StringParameterValue", "name": "TYPES", "value": maps[curser[i]]["types"].join(",")])

        /* Other userful parameters */
        list.add([$class : "StringParameterValue", "name": "FW_VERSION", "value": env.FW_VERSION])
        list.add([$class : "StringParameterValue", "name": "FW_IMAGE_PATH", "value": env.FW_IMAGE_PATH])
        list.add([$class : "StringParameterValue", "name": "PLATFORM", "value": env.PLATFORM])
        list.add([$class : "StringParameterValue", "name": "FW_UPDATE", "value": env.FW_UPDATE])
        list.add([$class : "StringParameterValue", "name": "TESTCASE_PATH", "value": env.TESTCASE_PATH])
        list.add([$class : "StringParameterValue", "name": "REPORT_PATH", "value": env.REPORT_PATH])
        list.add([$class : "StringParameterValue", "name": "LOOP_TEST", "value": env.LOOP_TEST])

        list.add([$class : "StringParameterValue", "name": "ACIS_DIFF", "value": env.ACIS_DIFF])
        list.add([$class : "StringParameterValue", "name": "JOB_NAME", "value": env.JOB_NAME])

        /* Cookie for parallel */
        testplan[curser[i]] = [ "job": "common_job" ,"parameters": list, "flags" : ""]
        list = []
    }
}

def get_cookie(){

    def maps = [:]
    def maps_curser = []

    def maps_file = [:]            /*From Git repo file -- ACIS_MAPS.txt*/
    def maps_file_curser = []      /*a curser list for maps dict*/

    def maps_filter = [:]
    def maps_filter_curser = []

    def maps_merged = [:]
    def maps_merged_curser = []

    make_curser_maps(MAPS_to_list(env.MAPS),
                     maps_curser,
                     maps)

    def file = readFile("${workspace}/ACIS_MAPS.txt");

    make_curser_maps(MAPS_to_list(file),
                     maps_file_curser,
                     maps_file)

    make_filter_maps(env.FILTER,
                     file,
                     maps_file,
                     maps_file_curser,
                     maps_filter,
                     maps_filter_curser)

    println maps_filter
    println maps_filter_curser

    merge_maps(maps,
               maps_curser,
               maps_filter,
               maps_filter_curser,
               maps_merged,
               maps_merged_curser)
    println maps_merged
    println maps_merged_curser

    def testplan = [:]
    def testplan_curser = maps_merged_curser
    make_testplan(maps_merged,
                  maps_merged_curser,
                  testplan)
    println "testplan: ${testplan}"
    println "testplan cur: ${testplan_curser}"

    return [testplan, testplan_curser]
}

return this
