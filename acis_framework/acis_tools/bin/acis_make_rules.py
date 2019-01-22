#! /usr/bin/env python3
#coding = utf-8

"""
"""

import subprocess
import os,sys,re

rule_template = """\
# ACIS udev conf

# Now, ACIS support 'TWO' DUTs : DUT1 and DUT2
{rule_DUT1_part_01}
{rule_DUT2_part_01}
GOTO="acis_end"

{rule_DUT1_part_02}

{rule_DUT2_part_02}

# End of Conf.
LABEL=="acis_end"
"""

rule_DUT1_part_01 = """\
ATTRS{{serial}}=="{DUT1_dev}", GOTO="acis_DUT1"\
"""

rule_DUT1_part_02 = """
LABEL=="acis_DUT1"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT1/AT", ATTRS{bInterfaceNumber}=="03"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT1/DM", ATTRS{bInterfaceNumber}=="00"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT1/NMEA", ATTRS{bInterfaceNumber}=="02"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT1/RAW_DATA", ATTRS{bInterfaceNumber}=="05"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT1/OSA", ATTRS{bInterfaceNumber}=="06"
GOTO="acis_end"\
"""

rule_DUT2_part_01 = """\
ATTRS{{serial}}=="{DUT2_dev}", GOTO="acis_DUT2"\
"""

rule_DUT2_part_02 = """\
LABEL=="acis_DUT2"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT2/AT", ATTRS{bInterfaceNumber}=="03"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT2/DM", ATTRS{bInterfaceNumber}=="00"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT2/NMEA", ATTRS{bInterfaceNumber}=="02"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT2/RAW_DATA", ATTRS{bInterfaceNumber}=="05"
SUBSYSTEMS=="usb", DRIVERS=="GobiSerial", SYMLINK+="acis/DUT2/OSA", ATTRS{bInterfaceNumber}=="06"
GOTO="acis_end"\
"""

def get_devices():
    """
    devices : ['serial_id', 'serial_id_2'...]
    """
    try:
        output = subprocess.check_output('adb devices',
                                        shell = True).decode('utf-8').strip()
    except subprocess.CalledProcessError as err:
        print("ERROR: ", err)
        sys.exit(-1)
    else:
        devices = []
        for line in output.split('\n'):
            print(line)
            g = re.match('\s*?(.*)\s*device$', line)
            if g:
                devices.append(g.group(1).strip())
        print(devices)
        return devices


def interactions(devices):
    """
    picks : {'DUT1' : 'serial_id', 'DUT2' : 'serial_id'}
    """

    total_nums = 0
    picks = {}

    print("""             \
    >acis.make.rules<\nNote, acis.make.rules tool only support 'DUT1' and 'DUT2' devices.\n""")
    print("Which would you like to link to </dev/acis/DUT1> ?")

    for n,d in enumerate(devices):
        print("{n}. <{d}>".format(n = n + 1, d = d))
        total_nums += 1
    print("Total devices: [{nums}]\n".format(nums = total_nums))
    if total_nums == 0 or total_nums > 2:
        print("ACIS only support 1-2 devices, but scan [{}] . Please check your USB connection.".format(total_nums))
        sys.exit(-1)

    while True:
        try:
            which = int(input("Your choice:(number) "))
            if which > total_nums or which <= 0:
                raise ValueError("Outof Range")
        except ValueError:
            print("Please type INT NUMBER(in range 1-2) to pick."); continue
        else:
            print(which)
            picks["DUT1"] = devices[which-1]

            if total_nums < 2:
                print("Now only one device [{}], and that be added to 'DUT1', so there is NO 'DUT2'".format(devices[which-1]))
            else:
                print("Due to your choice [{}] as 'DUT1', ".format(
                    devices[which-1]), end = '')
                if which == 1:
                    print("so 'DUT2' auto-confirmed to [{}]".format(devices[1]))
                    picks["DUT2"] = devices[1]
                else:
                    print("so 'DUT2' auto-confirmed to [{}]".format(devices[0]))
                    picks["DUT2"] = devices[0]
            break
    return picks


def make_rules(_file, devices):

    template = ""

    if len(devices) == 2:
        template = rule_template.format( rule_DUT1_part_01 = rule_DUT1_part_01.format(DUT1_dev = devices["DUT1"]),
                                         rule_DUT1_part_02 = rule_DUT1_part_02,
                                         rule_DUT2_part_01  = rule_DUT2_part_01.format(DUT2_dev = devices["DUT2"]),
                                         rule_DUT2_part_02  = rule_DUT2_part_02)
    elif len(devices) == 1:
        template = rule_template.format( rule_DUT1_part_01 = rule_DUT1_part_01.format(DUT1_dev = devices["DUT1"]),
                                         rule_DUT1_part_02 = rule_DUT1_part_02,
                                         rule_DUT2_part_01  = "",
                                         rule_DUT2_part_02  = "")
    #print("======== output template ========\n",template)
    with open(_file, 'w') as f:
        f.write(template)
        f.flush()
    print("\n[Next Step] >> Hey, Guy! \n >> Now please unplug all USB DEVICEs and Sysmte will auto-enable the NEW rules for udev.")


def check_rules(_file, devices):

    if os.path.exists(_file):
        print("\n\n=============== [show file contents ]===============")
        for l in open(_file, 'r'):
            print(l,end = '')
        print("=============== [ end of show ]===============")
        while True:
            choice = str(input("Do you want to overwrite it? (y/n)")).lower()
            if choice not in ("y", "n"):
                print("Please type (y or n) for your choice."); continue
            if choice == "n":
                print("Your choice is [NOT overwrite rules], so do nothing...")
                break
            else:
                make_rules(_file, devices)
                break
    else:
        print("File:<{}> not exists, Now new a file to make a rule.".format(_file))
        make_rules(_file, devices)

def main():
    check_rules('/etc/udev/rules.d/11-acis.rules', interactions(get_devices()))

if __name__ == "__main__":
    main()

