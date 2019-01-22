"""
Contains all exceptions about mail-core.
"""

class MailException(Exception): pass

class MailTypeErr(MailException): pass

class UnvaildEmailErr(MailException): pass

class BadEmailFormatErr(MailException): pass

class MailMatchTypeErr(MailException): pass

class UnvaildPortOfMailServer(MailException): pass

