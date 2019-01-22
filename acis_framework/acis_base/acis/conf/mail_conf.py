# -*- coding: utf-8 -*-

"""
Mail Configuration

CMD: python3 -m smtpd -n -c DebuggingServer localhost:1025 qpmoiyqxdpuwhdbb
"""

mail_server_conf = {
    "hostname" : "localhost",
    "ip"       : "127.0.0.1", # Now don't care
    "auto-load": False,
    "mark-port": "1025",
    "password" : "", # special code
    "ports"    : [
        "8000",
        "1025",
    ]
}

mail_server_conf_D2 = {
    "hostname" : "smtp.qq.com",
    "ip"       : "127.0.0.1", # Now don't care
    "auto-load": False,
    "mark-port": "465",
    "password" : "xqpmoiyqxdpuwhdbbx", # special code
    "ports"    : [
        "465",
        "587",
    ]
}

mail_group_conf = {
    "group-name" : "SWI",
    "auto-load"  : False,
    "mails" : [
        "rzheng@sierrawireless.com",
    ]
}

mail_group_conf_D2 = {
    "group-name" : "PPP",
    "auto-load"  : False,
    "mails" : {
        "1274928mmm@qq.com",
        "helloworxd@sina.com",
    }
}
# For Example
mail_default_conf = {
    "name"         : "awesome", # You can modify it during registered.
    "subject"      : "Darling Module Init",
    "from-addr"    : "1274928808@qq.com",
    "to-addrs"     : [
        "1274928808@qq.com",
    ],
    "groups" : [
        "SWI",
    ],
    "server-name": "smtp.qq.com",
    "headers"      : {
        "first-stage" : "first stage",
        "second-stage" : "second stage",
    },
    "message"      :\
    """
    Dear everyone,

    The Darling Module Test package is very useful.

    If you want to test some case for yourself,
    you can try it.

    You will enjoy it I think.

    Thx.
    Rex Z
    """
}

conf_groups  = [mail_group_conf, mail_group_conf_D2]
conf_servers = [mail_server_conf, mail_server_conf_D2] # Now only one.
def get_autoload_conf():
    match_groups = []
    match_servers = []

    [match_groups.append(g) for g in conf_groups if g['auto-load'] == True]
    [match_servers.append(s) for s in conf_servers if s['auto-load'] == True]

    return (match_groups, match_servers)
