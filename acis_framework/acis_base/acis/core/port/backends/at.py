#! /usr/bin/env python
# coding=utf-8

"""

"""

# Encoding Dictionary.
from .encoding_format import (
    ascii2hexstring_printable_revert,
    ascii2hexstring_printable_tempsymbol,
    ascii2hexstring_extended,
    ascii2hexstring_printable,
    ascii2hexstring_symbol,
    ascii_symbol)

import time,re,sys
import platform,fnmatch
import serial
from datetime import datetime
from acis.utils.log import peer
import allure,pytest


class _AT():

    name = '_AT'

    objs = {}

    def __init__(self, conf):

        self.conf = conf
        self.port_link = conf["dev_link"]

        self.reset_mark = False

        # AT Send receive time stamp
        self.SndRcvTimestamp = False
        self.RcvTimespent = False

        #Variable for status
        self.statOfItem = 'OK'

        # Variable for log
        self.numOfSuccessfulResponse = 0.0

        #list of opened COM ports
        self.uartbuffer = {}

        self.open(port = self.port_link)

        peer(self)

    def __repr__(self):
       return "<Class: {name} , dev_link: {conf}>".format(name = _AT.name,conf=self.conf)

    @allure.step
    def open(self,
             port=None,
             baudrate=115200,
             bytesize=8,
             parity='N',
             stopbits=1,
             rtscts=False,
             OpenPortTimeout=2000,
             timeout=1,
             dsrdtr=False,
             xonxoff=False,
             interCharTimeout=None,
             write_timeout=None):

        # validate parameter - rtscts
        flowcontrol = "Hardware"
        if type(rtscts) == type("string"):
            if rtscts not in ["Hardware", "None"]:
                peer("Invalid parameter for AcisOpen() - rtscts")
                peer("Option:")
                peer("\"Hardware\"" + "\"None\"")
                peer("")
                rtscts = 1
                flowcontrol = "Hardware"
            if rtscts == "Hardware":
                rtscts = 1
                flowcontrol = "Hardware"
            if rtscts == "None":
                rtscts = 0
                flowcontrol = "None"
        self.detect_port(port,OpenPortTimeout, "nologmsg")
        try:
            hCom=None
            hCom = serial.Serial(port,
                                 baudrate,
                                 bytesize,
                                 parity,
                                 stopbits,
                                 timeout,
                                 xonxoff,
                                 rtscts,
                                 write_timeout,
                                 dsrdtr,
                                 interCharTimeout)
            peer("{} OPEN: Open the ".format(hCom) + hCom.port + " @"+str(baudrate)+" "+str(bytesize)+str(parity)+str(stopbits)+" "+str(flowcontrol))
            time.sleep(1)

            self.uartbuffer[hCom.port] = ""

            self.hCom = hCom

            _AT.objs[self.conf["serial_id"]] = self.hCom

            return hCom

        except serial.SerialException as val:
            peer(val)
            if ("%s"%val).startswith("could not open port "):
                peer("ERROR Could not open COM%d !"%(port))
                peer("hCom" + str(hCom))
            else:
                peer("ERROR : %s"%val)

        except AttributeError:
            peer("OPEN: Busy for "+hCom.port+"!")

    @allure.step
    def reopen(self, cfun_delay_time=2000):

        self.close()
        self.sleep(cfun_delay_time)

        return self.open(self.hCom.port,
                         self.hCom.baudrate,
                         self.hCom.bytesize,
                         self.hCom.parity,
                         self.hCom.stopbits)

    @allure.step
    def detect_port(self, port, timeout=2000, logmsg="logmsg"):

        start_time = datetime.now()
        flag_linebreak = 0
        while 1:
            try:
                s = serial.Serial(port,
                                  baudrate=115200,
                                  bytesize=8,
                                  parity='N',
                                  stopbits=1,
                                  timeout=1,
                                  xonxoff=False,
                                  rtscts=False,
                                  writeTimeout=None,
                                  dsrdtr=False)
                if logmsg=="logmsg":
                    if flag_linebreak:
                        peer("")
                    peer(port+" - port found")
                # display time spent in receive
                diff_time = datetime.now() - start_time
                diff_time_ms = diff_time.seconds * 1000 + diff_time.microseconds / 1000
                if logmsg=="logmsg":
                    peer(" <"+str(timeout)+" @"+str(diff_time_ms)+"ms")
                s.close()
                break
            except serial.SerialException:
                pass
            time.sleep(1)
            sys.stdout.write("*")
            flag_linebreak = 1
            # Count timeout
            diff_time = datetime.now() - start_time
            diff_time_ms = diff_time.seconds * 1000 + diff_time.microseconds / 1000
            if diff_time_ms > timeout:
                if logmsg=="logmsg":
                    if flag_linebreak:
                        peer("")
                    peer(port+" - port not found"+" <"+str(timeout)+" ms")
                break

    @allure.step
    def sleep(self, millisecond, silent=False):
        try:
            if not(silent):
                peer("SLEEP: Start sleep for %d milliseconds" % millisecond)
            time.sleep(millisecond/1000.0)
            if not(silent):
                peer("SLEEP: End sleep")
        except SystemExit:
            raise SystemExit
        except Exception as e:
            peer(e)

    @allure.step
    def close(self):
        try:
            self.hCom.close()

            peer("CLOSE: Close the "+self.hCom.port)
        except Exception as e:
            peer(e)
            peer("CLOSE: Error for "+self.hCom.port)

    def timeDisplay(self, dt = None):
        "Display the time ; if dt is empty retrun actual date time under format, otherless return dt under format"
        "INPUT  : (optionnal) dt : date Time"
        "OUTPUT : date Time under format hh:mm:ss:???"
        if dt == None:
            dt = datetime.now()
        return "(%0.2d:%0.2d:%0.2d:%0.3d)"%(dt.hour, dt.minute, dt.second, dt.microsecond/1000)

    @allure.step
    def send_cmd(self, cmd, printmode="symbol"):
        "goal of the method : this method sends an AT command on a COM port"
        "INPUT : hCom : COM port object"
        "        cmd : AT command to send"
        "OUTPUT : none"

        if not self.hCom.is_open:
            self.hCom.open()

        self.hCom.write(cmd.encode('utf-8'))

        if re.search('AT!RESET', cmd):
            #self.hCom.close()
            self.reset_mark = True

        time.sleep(0.1)

        timestamp = ""
        if self.SndRcvTimestamp:
            timestamp = self.timeDisplay() + " "
        LogMsg = timestamp+"Snd COM "+ self.hCom.port+" ["+self.ascii2print(cmd,printmode)+"]"
        peer(LogMsg)

    def ascii2print(self, inputstring, mode="symbol"):

        if mode=="symbol":
            # direct convert value to string by Dictionary >> very fast
            string_raw = inputstring
            # convert raw data to <symbol> for \x00 - \x1F
            #                     <0x??>   for \x80 - \xFF
            for key, value in ascii_symbol.items():
                string_raw = string_raw.replace(key,value)
                outputstring = string_raw

        if mode=="hexstring":
            # direct convert value to string by Dictionary >> very fast
            string_raw = inputstring
            for key, value in ascii2hexstring_printable_tempsymbol.items():
                string_raw = string_raw.replace(key,value)
            for key, value in ascii2hexstring_printable_revert.items():
                string_raw = string_raw.replace(key,value)
            for key, value in ascii2hexstring_symbol.items():
                string_raw = string_raw.replace(key,value)
            for key, value in ascii2hexstring_extended.items():
                string_raw = string_raw.replace(key,value)
                outputstring = string_raw

        if mode=="raw":
            string_raw = inputstring
            # convert <symbol> to raw data
            for key, value in ascii_symbol.items():
                string_raw = string_raw.replace(value,key)
                # convert <0x??> to raw data
            for key, value in ascii2hexstring_printable.items():
                string_raw = string_raw.replace(value,key)
            for key, value in ascii2hexstring_symbol.items():
                string_raw = string_raw.replace(value,key)
            for key, value in ascii2hexstring_extended.items():
                string_raw = string_raw.replace(value,key)
                outputstring = string_raw

        return outputstring

    @allure.step
    def clean_buffer(self):
            "goal of the method : this method clears the input buffer of hCom COM port instance"
            "INPUT : hCom, COM port instance"
            "OUTPUT : none"
            try:
                    self.hCom.flushInput()

            except SystemExit:
                    raise SystemExit

            except Exception as e:
                    self.hCom.close()
                    peer("CLEAR_BUFFER: Error!")
                    peer(e)

    @allure.step
    def waitn_match_resp(self, waitpattern, timeout, condition="wildcard", update_result="critical", log_msg="logmsg", printmode="symbol"):
        "goal of the method : combine AcisWaitResp() and AcisMatchResp()"
        "INPUT : hCom : COM port object"
        "        waitpattern : the matching pattern for the received data"
        "        timeout : timeout value in second"
        "OUTPUT : None"

        #myColor = colorLsit[8]

        # validate parameter - condition
        if condition not in ["wildcard"]:
            peer("Invalid parameter for AcisWaitnMatchResp() - condition")
            peer("Option:")
            peer("\"wildcard\"")
            peer("")
            peer("AcisWaitnMatchResp() only support \"wildcard\" in \"condition\"")
            peer("")
            condition = "wildcard"

        AcisWaitResp_response = self.wait_resp( waitpattern, timeout, log_msg, printmode)
        match_result = self.match_resp(AcisWaitResp_response, waitpattern, condition, update_result, log_msg, printmode)
        if self.reset_mark:
            self.hCom.close()
            self.reset_mark = False
        return match_result

    @allure.step
    def match_resp(self, resp, keywords, condition="wildcard", update_result="critical", log_msg="logmsg", printmode="symbol"):
        "goal of the method : this method compares the received command to the expected command and Display the comparison result"
        "INPUT :  resp : Response object or a string"
        "         keywords (list) : expected response"
        "         condition : matching condition, 1.wildcard"
        "                                        2.match_all_order"
        "                                        3.match_all_disorder"
        "                                        4.contain_all_order"
        "                                        5.contain_all_disorder"
        "                                        6.contain_anyone"
        "                                        7.not_contain_anyone"
        "         update_result : 1. critical, update result to global variable statOfItem"
        "                         2. not_critical, do nothing for the result"
        "         log_msg : 1. logmsg, peer with log message"
        "                   2. debug, peer with log and debug message"
        "                   3. nologmsg, peer without any message"
        "OUTPUT : Boolean >> True:response matched, False:repsonse mis-matched"

        #myColor = colorLsit[8]
        if not self.hCom.is_open:
            self.hCom.open()

        # If resp is Response() >> assign .tabData to resp
        if type(resp) != type("string"):
            #peer "This is not a string"
            resp = resp.tabData

        # If keywords is None >> assign empty string
        if keywords == None:
            keywords = [""]

        # validate parameter - condition
        if condition not in ["wildcard", "match_all_order", "match_all_disorder", "contain_all_order", "contain_all_disorder", "contain_anyone", "not_contain_anyone"]:
            peer( "Invalid parameter for AcisMatchResp() - condition")
            peer( "Option:" )
            peer( "\"wildcard\"" + "\"match_all_order\"" + "\"match_all_disorder\"" + "\"contain_all_order\"" + "\"contain_all_disorder\"" + "\"contain_anyone\"" + "\"not_contain_anyone\"" )
            peer( "" )
            condition = "wildcard"

        # validate parameter - update_result
        if update_result not in ["critical", "not_critical"]:
            peer("Invalid parameter for AcisMatchResp() - update_result")
            peer("Option:")
            peer("\"critical\"" + "\"not_critical\"")
            peer("")
            update_result = "critical"

        # validate parameter - log_msg
        if log_msg not in ["logmsg", "nologmsg", "debug"]:
            peer("Invalid parameter for AcisMatchResp() - log_msg")
            peer("Option:")
            peer("\"logmsg\"" + "\"nologmsg\"" + "\"debug\"")
            peer("")
            log_msg = "logmsg"

        # 1
        # Default - matching with wildcard character
        if condition=="wildcard":
            flag_matchstring = False
            matched = False
            for (each_elem) in keywords:
                receivedResp = resp
                expectedResp = each_elem
                if fnmatch.fnmatchcase(receivedResp, expectedResp):
                    flag_matchstring = True
                    matched = True
                    break

            if matched == 0 :
                if log_msg == "logmsg" or log_msg == "debug":
                    if len(keywords)==1:
                        peer("")
                        peer("Expected Response: %s" % self.ascii2print(expectedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                        peer("Received Response: %s" % self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                        peer("")
                    if len(keywords)>1:
                        peer("")
                        peer("Expected Response: %s" % self.ascii2print(keywords[0],printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                        for (i,each_elem) in enumerate(keywords):
                            if i == 0:
                                pass
                            if i >0:
                                SafePrintLog("Expected Response: %s" % self.ascii2print(each_elem,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                        SafePrintLog("Received Response: %s" % self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                        SafePrintLog("")
        # 2
        if condition=="match_all_order":
            if log_msg == "debug":
                peer("Check if response match all keywords in order: ( match without extra char. )")
            receivedResp = resp
            expectedResp = ""
            for (i,each_keyword) in enumerate(keywords) :
                expectedResp += keywords[i]
            matched = fnmatch.fnmatchcase(receivedResp, expectedResp)
            if matched == 0 :
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer("No Match!! (match_all_order)")
                    peer("")
                    peer("Expected Response: %s" % self.ascii2print(expectedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                    peer("Received Response: %s" % self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                    peer("")

        # 3
        if condition=="match_all_disorder":
            debug_msg = ""
            debug_msg += "Check if response contains all keywords ( without extra character, dis-order ): \n"
            # differcuit to code , code later

            itemlist = keywords
            #itemlist = ["A","B","C"]
            permutation_list = list(itertools.permutations(itemlist, len(itemlist)))
            permutation_concat_list = []
            for each_elem in permutation_list:
                tempstring = ""
                for eachchar in each_elem:
                    tempstring += eachchar
                permutation_concat_list.append(tempstring)

            debug_msg += "\nConbination of keywords: \n"

            for (i,each_conbination) in enumerate(permutation_concat_list) :
                # peer i+1, ascii2print(each_conbination,printmode).replace("<CR>","\\r").replace("<LF>","\\n")

                receivedResp = resp
                expectedResp = each_conbination
                matched = fnmatch.fnmatchcase(receivedResp, expectedResp)

                # debug message
                if matched == 0 :
                    debug_msg += str(i+1) + " " + self.ascii2print(each_conbination,printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- no match\n"
                else:
                    debug_msg += str(i+1) + " " + self.ascii2print(each_conbination,printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- matched\n"

                # break in normal mode when result matched
                # normal mode >> matched result and break, debug mode >> list all conbination and result
                if matched == 1 :
                    if log_msg != "debug":
                        break

            # display "No Match" when matching failed
            if matched == 1 :
                if log_msg == "debug":
                    peer( debug_msg)
            else:
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer("No Match!! (match_all_disorder)")
                    peer("")
                    peer( debug_msg)

        # 4
        if condition=="contain_all_order":
            debug_msg = ""
            debug_msg += "Check if response contains all keywords in order:"
            receivedResp = resp
            expectedResp = "*"
            for (i,each_keyword) in enumerate(keywords) :
                if i == 0 :
                    expectedResp += keywords[i]
                else:
                    expectedResp += "*" + keywords[i]
            expectedResp += "*"
            matched = fnmatch.fnmatchcase(receivedResp, expectedResp)
            if matched == 1 :
                if log_msg == "debug":
                    peer("")
                    peer( debug_msg)
                    peer( "Expected Response: %s" % self.ascii2print(expectedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                    peer("")
            else:
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer("No Match!! (contain_all_order)")
                    peer("")
                    peer("Expected Response: %s" % self.ascii2print(expectedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                    peer("Received Response: %s" % self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n"))
                    peer("")

        # 5
        if condition=="contain_all_disorder":
            debug_msg = ""
            debug_msg += "\nCheck if response contains all keywords without order:\n\n"
            #for (i,each_keyword) in enumerate(keywords) :
            #    peer ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n")
            receivedResp = resp
            expectedResp = ""

            debug_msg += "Response: " + self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "\n"
            debug_msg += "Keywords:\n"
            flag_notfound = 0
            matched = 1

            for (i,each_keyword) in enumerate(keywords) :
                if resp.find(keywords[i]) >= 0:
                    debug_msg += self.ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- found\n"
                else:
                    debug_msg += self.ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- not found\n"
                    flag_notfound = 1


            if flag_notfound == 0:
                matched = 1
                if log_msg == "debug":
                    peer( debug_msg)

            if flag_notfound == 1:
                matched = 0
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer( "No Match!! (contain_all_disorder)")
                    peer("")
                    peer(debug_msg)

        # 6
        if condition=="contain_anyone":
            debug_msg = ""
            debug_msg += "\nCheck if response contains anyone of keywords: \n\n"
            #for (i,each_keyword) in enumerate(keywords) :
            #    peer ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n")
            receivedResp = resp
            expectedResp = ""

            debug_msg += "Response: " + self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "\n"
            debug_msg += "Keywords:\n"
            flag_found = 0
            matched = 0
            for (i,each_keyword) in enumerate(keywords) :
                if resp.find(keywords[i]) >= 0:
                    debug_msg += self.ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- found\n"
                    flag_found = 1
                else:
                    debug_msg += self.ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- not found\n"

            if flag_found == 1:
                matched = 1
                if log_msg == "debug":
                    peer(debug_msg)

            if flag_found == 0:
                matched = 0
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer("No Match!! (contain_anyone)")
                    peer("")
                    peer( debug_msg)

        # 7
        if condition=="not_contain_anyone":
            debug_msg = ""
            debug_msg += "\nCheck that response do not contains anyone of keywords: \n\n"
            #for (i,each_keyword) in enumerate(keywords) :
            #    peer ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n")
            receivedResp = resp
            expectedResp = ""

            debug_msg += "Response: " + self.ascii2print(receivedResp,printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "\n"
            debug_msg += "Keywords:\n"
            flag_found = 0
            matched = 1

            for (i,each_keyword) in enumerate(keywords) :
                if resp.find(keywords[i]) >= 0:
                    debug_msg += self.ascii2print(keywords[i],printmode).replace("<CR>","\\r").replace("<LF>","\\n") + "      <-- found\n"
                    flag_found = 1
                else:
                    debug_msg += self.ascii2print(keywords[i],printmode) + "      <-- not found\n"


            if flag_found == 0:
                matched = 1
                if log_msg == "debug":
                    peer( debug_msg)

            if flag_found == 1:
                matched = 0
                if log_msg == "logmsg" or log_msg == "debug":
                    peer("")
                    peer("No Match!! (not_contain_anyone)")
                    peer("")
                    peer( debug_msg)

        # udpate result to statOfItem
        if update_result == "critical":
            if matched == 0:
                self.statOfItem = 'NOK'
                raise Exception("<Critical> Exception: reason is NOT match Response.")
            else:
                self.numOfSuccessfulResponse += 1.0
                pass
        else:
            if log_msg == "logmsg":
                peer("\nNot Critical command\n")

        return matched

    @allure.step
    def wait_resp(self, waitpattern, timeout=60000, log_msg="logmsg", printmode="symbol"):
        "goal of the method : this method waits for the data received from Com port"
        "INPUT : self.hCom : COM port object"
        "        waitpattern : the matching pattern for the received data"
        "        timeout (ms) : timeout between each received packet"
        "        log_msg : option for log message"
        "OUTPUT : Received data (String)"

        if not self.hCom.is_open:
            self.hCom.open()
        start_time = datetime.now()
        com_port_name = self.hCom.port
        if log_msg == "debug":
            peer(start_time)
        flag_matchrsp = False
        flag_matchstring = False
        flag_timeout = False
        flag_wait_until_timeout = False
        flag_printline = False
        LogMsg = ""
        timestamp = ""

        # wait until timeout mode
        if waitpattern == None or waitpattern[0] == "":
            flag_wait_until_timeout = True
            waitpattern = [""]
            peer("")
            peer("Wait responses in %s ms" % str(timeout))
            peer("")

        displaybuffer = ""
        displaypointer = 0
        while 1:
            # Read data from UART Buffer
            if int(self.hCom.in_waiting) > 0:
                self.uartbuffer[self.hCom.port] += self.hCom.read(self.hCom.in_waiting).decode('utf-8','ignore')
                if log_msg == "debug":
                    #myColor = colorLsit[7]
                    #peer "Read data from UART buffer:", self.uartbuffer[self.hCom.port].replace("\r","<CR>").replace("\n","<LF>")
                    #peer "Read data from UART buffer:", self.ascii2print(self.uartbuffer[self.hCom.port],printmode)
                    LogMsg = "Read data from UART buffer: "+ self.ascii2print(self.uartbuffer[self.hCom.port],printmode)
                    peer(LogMsg)
            # Match response
            # Loop for each character
            for (i,each_char) in enumerate(self.uartbuffer[self.hCom.port]) :
                if log_msg == "debug":
                    #myColor = colorLsit[7]
                    #peer i, self.uartbuffer[self.hCom.port][:i+1].replace("\r","<CR>").replace("\n","<LF>").replace("\n","<LF>")
                    #peer i, ascii2print(self.uartbuffer[self.hCom.port][:i+1],printmode)
                    LogMsg = str(i)+" "+self.ascii2print(self.uartbuffer[self.hCom.port][:i+1],printmode)
                    peer(LogMsg)
                # display if matched with a line syntax
                displaybuffer = self.uartbuffer[self.hCom.port][displaypointer:i+1]
                line_syntax1 = "*\r\n*\r\n"
                line_syntax2 = "+*\r\n"
                line_syntax3 = "\r\n> "
                if fnmatch.fnmatchcase(displaybuffer, line_syntax1) or \
                    fnmatch.fnmatchcase(displaybuffer, line_syntax2) or \
                    fnmatch.fnmatchcase(displaybuffer, line_syntax3) :
                    # display timestamp
                    if self.SndRcvTimestamp:
                        timestamp = self.timeDisplay() + " "
                    # display data
                    #myColor = colorLsit[7]
                    #received_data = displaybuffer.replace("\r","<CR>").replace("\n","<LF>").replace("\x15","<NAK>").replace("\x06","<ACK>").replace("\x00","<NULL>")
                    received_data = self.ascii2print(displaybuffer,printmode)
                    #peer timestamp+"Rcv COM", com_port_name, "["+received_data+"]",
                    LogMsg = timestamp+"Rcv COM "+com_port_name+" ["+received_data+"] "
                    displaypointer = i+1
                    flag_printline = True

                # match received response with waitpattern
                for (each_elem) in waitpattern:
                    receivedResp = self.uartbuffer[self.hCom.port][:i+1]
                    expectedResp = each_elem
                    if fnmatch.fnmatchcase(receivedResp, expectedResp):
                        flag_matchstring = True
                        break
                if flag_matchstring:
                    # display the remaining matched response when waitpettern is found
                    displaybuffer = self.uartbuffer[self.hCom.port][displaypointer:i+1]
                    if len(displaybuffer)>0:
                        # display timestamp
                        if self.SndRcvTimestamp:
                            timestamp = self.timeDisplay() + " "
                        # display data
                        #myColor = colorLsit[7]
                        #received_data = displaybuffer.replace("\r","<CR>").replace("\n","<LF>").replace("\x15","<NAK>").replace("\x06","<ACK>").replace("\x00","<NULL>")
                        received_data = self.ascii2print(displaybuffer,printmode)
                        #peer "Rcv COM", com_port_name, "["+received_data+"]",
                        LogMsg = timestamp+"Rcv COM "+str(com_port_name)+" ["+received_data+"] "
                        pass

                    # display time spent in receive
                    if self.RcvTimespent:
                        diff_time = datetime.now() - start_time
                        diff_time_ms = diff_time.seconds * 1000 + diff_time.microseconds / 1000
                        #peer " <"+str(timeout), " @"+str(diff_time_ms), "ms",
                        LogMsg += " <"+str(timeout)+" @"+str(diff_time_ms)+" ms "

                    flag_printline = True

                    # clear matched resposne in UART Buffer
                    self.uartbuffer[self.hCom.port] = self.uartbuffer[self.hCom.port][i+1:]
                    flag_matchrsp = True

                    # break for Match response
                    flag_matchrsp = True

                # peer linebreak for EOL
                if flag_printline:
                    flag_printline = False
                    #peer ""
                    peer(LogMsg)

                # break for Match response
                if flag_matchrsp:
                    break

            # Count timeout
            diff_time = datetime.now() - start_time
            diff_time_ms = diff_time.seconds * 1000 + diff_time.microseconds / 1000
            if diff_time_ms > timeout:
                if log_msg == "debug":
                    #peer "Timeout: ", diff_time, "diff_time_ms:", diff_time_ms
                    LogMsg = "Timeout: "+str(diff_time)+" diff_time_ms: "+str(diff_time_ms)
                    peer(LogMsg)
                # display the remaining response when timeout
                displaybuffer = self.uartbuffer[self.hCom.port][displaypointer:]
                if len(displaybuffer)>0:
                    # display timestamp
                    if self.SndRcvTimestamp:
                        #myColor = colorLsit[7]
                        #peer TimeDisplay(),
                        timestamp = self.timeDisplay() + " "
                    # display data
                    #myColor = colorLsit[7]
                    #received_data = receivedResp.replace("\r","<CR>").replace("\n","<LF>").replace("\x15","<NAK>").replace("\x06","<ACK>").replace("\x00","<NULL>")
                    received_data = self.ascii2print(receivedResp,printmode)
                    #peer "Rcv COM", com_port_name, " ["+received_data+"]"
                    LogMsg = "Rcv COM "+str(com_port_name)+" ["+received_data+"]"
                    peer(LogMsg)
                    pass

                # clear all resposne in UART Buffer
                #myColor = colorLsit[8]
                receivedResp = self.uartbuffer[self.hCom.port]

                if flag_wait_until_timeout != True:
                    if log_msg == "logmsg" or log_msg == "debug":
                        if len(receivedResp) > 0:
                            #peer "\nNo Match! "+"@COM"+com_port_name+ " <"+str(timeout)+" ms\n"
                            LogMsg = "\nNo Match! "+"@COM"+com_port_name+" <"+str(timeout)+" ms\n"
                            peer(LogMsg)
                        if len(receivedResp) == 0:
                            #peer "\nNo Response! "+"@COM"+com_port_name+ " <"+str(timeout)+" ms\n"
                            LogMsg = "\nNo Response! "+"@COM"+com_port_name+ " <"+str(timeout)+" ms\n"
                            peer(LogMsg)
                self.uartbuffer[self.hCom.port] = ""
                flag_timeout = True

            if flag_matchrsp:
                break
            if flag_timeout:
                break

        if log_msg == "debug":
            peer("")
            peer(str(len(self.uartbuffer[self.hCom.port])))
            LogMsg = "The remaining data in uartbuffer " + str((self.hCom.port + 1))  + " : [", self.ascii2print(self.uartbuffer[self.hCom.port],printmode), "]"
            peer(LogMsg)
        return receivedResp

class AT():

    name = "AT"

    def __init__(self, obj, conf):

        self.conf = {}

        self.DUT1 = self.DUT2 = self.any = None

        if obj == "DUT1":
            self.conf["DUT1"] = conf
            self.DUT1 = _AT(conf)
        elif obj == "DUT2":
            self.conf["DUT2"] = conf
            self.DUT2 = _AT(conf)
        elif obj == "any":
            self.conf["any"] = conf
            self.any = _AT(conf)

        self.info()

    def reinit(self, obj, conf):

        if obj == "DUT1":
            self.conf["DUT1"] = conf
            self.DUT1 = _AT(conf)
        else:
            self.conf["DUT2"] = conf
            self.DUT2 = _AT(conf)
        return self

    @allure.step
    def closeall(self):

        if self.DUT1:
            self.DUT1.close()
        if self.DUT2:
            self.DUT2.close()
        if self.any:
            self.any.close()

    def info(self):
        peer("My name is : {name}\n- conf:\n<{conf}>".format(name = AT.name, conf = self.conf))
