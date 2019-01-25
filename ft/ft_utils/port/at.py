#! /usr/bin/env python
# coding=utf-8

"""
"""

import time,re,sys,serial
import platform,fnmatch
import allure,pytest
from datetime import datetime

try:
    from ft_utils.log import peer
except ImportError:
    peer = print

# Encoding Dictionary.
ascii_symbol = {
    '\x00' : "<NULL>",
    '\x01' : "<SOH>",
    '\x02' : "<STX>",
    '\x03' : "<ETX>",
    '\x04' : "<EOT>",
    '\x05' : "<ENQ>",
    '\x06' : "<ACK>",
    '\x07' : "<BEL>",
    '\x08' : "<BS>",
    '\x09' : "<TAB>",
    '\x0a' : "<LF>",
    '\x0b' : "<VT>",
    '\x0c' : "<FF>",
    '\x0d' : "<CR>",
    '\x0e' : "<SO>",
    '\x0f' : "<SI>",
    '\x10' : "<DLE>",
    '\x11' : "<DC1>",
    '\x12' : "<DC2>",
    '\x13' : "<DC3>",
    '\x14' : "<DC4>",
    '\x15' : "<NAK>",
    '\x16' : "<SYN>",
    '\x17' : "<ETB>",
    '\x18' : "<CAN>",
    '\x19' : "<EM>",
    '\x1a' : "<SUB>",
    '\x1b' : "<ESC>",
    '\x1c' : "<FS>",
    '\x1d' : "<GS>",
    '\x1e' : "<RS>",
    '\x1f' : "<US>",

    '\x7f' : "<DEL>",

    '\x80' :  "<0x80>",
    '\x81' :  "<0x81>",
    '\x82' :  "<0x82>",
    '\x83' :  "<0x83>",
    '\x84' :  "<0x84>",
    '\x85' :  "<0x85>",
    '\x86' :  "<0x86>",
    '\x87' :  "<0x87>",
    '\x88' :  "<0x88>",
    '\x89' :  "<0x89>",
    '\x8A' :  "<0x8A>",
    '\x8B' :  "<0x8B>",
    '\x8C' :  "<0x8C>",
    '\x8D' :  "<0x8D>",
    '\x8E' :  "<0x8E>",
    '\x8F' :  "<0x8F>",
    '\x90' :  "<0x90>",
    '\x91' :  "<0x91>",
    '\x92' :  "<0x92>",
    '\x93' :  "<0x93>",
    '\x94' :  "<0x94>",
    '\x95' :  "<0x95>",
    '\x96' :  "<0x96>",
    '\x97' :  "<0x97>",
    '\x98' :  "<0x98>",
    '\x99' :  "<0x99>",
    '\x9A' :  "<0x9A>",
    '\x9B' :  "<0x9B>",
    '\x9C' :  "<0x9C>",
    '\x9D' :  "<0x9D>",
    '\x9E' :  "<0x9E>",
    '\x9F' :  "<0x9F>",
    '\xA0' :  "<0xA0>",
    '\xA1' :  "<0xA1>",
    '\xA2' :  "<0xA2>",
    '\xA3' :  "<0xA3>",
    '\xA4' :  "<0xA4>",
    '\xA5' :  "<0xA5>",
    '\xA6' :  "<0xA6>",
    '\xA7' :  "<0xA7>",
    '\xA8' :  "<0xA8>",
    '\xA9' :  "<0xA9>",
    '\xAA' :  "<0xAA>",
    '\xAB' :  "<0xAB>",
    '\xAC' :  "<0xAC>",
    '\xAD' :  "<0xAD>",
    '\xAE' :  "<0xAE>",
    '\xAF' :  "<0xAF>",
    '\xB0' :  "<0xB0>",
    '\xB1' :  "<0xB1>",
    '\xB2' :  "<0xB2>",
    '\xB3' :  "<0xB3>",
    '\xB4' :  "<0xB4>",
    '\xB5' :  "<0xB5>",
    '\xB6' :  "<0xB6>",
    '\xB7' :  "<0xB7>",
    '\xB8' :  "<0xB8>",
    '\xB9' :  "<0xB9>",
    '\xBA' :  "<0xBA>",
    '\xBB' :  "<0xBB>",
    '\xBC' :  "<0xBC>",
    '\xBD' :  "<0xBD>",
    '\xBE' :  "<0xBE>",
    '\xBF' :  "<0xBF>",
    '\xC0' :  "<0xC0>",
    '\xC1' :  "<0xC1>",
    '\xC2' :  "<0xC2>",
    '\xC3' :  "<0xC3>",
    '\xC4' :  "<0xC4>",
    '\xC5' :  "<0xC5>",
    '\xC6' :  "<0xC6>",
    '\xC7' :  "<0xC7>",
    '\xC8' :  "<0xC8>",
    '\xC9' :  "<0xC9>",
    '\xCA' :  "<0xCA>",
    '\xCB' :  "<0xCB>",
    '\xCC' :  "<0xCC>",
    '\xCD' :  "<0xCD>",
    '\xCE' :  "<0xCE>",
    '\xCF' :  "<0xCF>",
    '\xD0' :  "<0xD0>",
    '\xD1' :  "<0xD1>",
    '\xD2' :  "<0xD2>",
    '\xD3' :  "<0xD3>",
    '\xD4' :  "<0xD4>",
    '\xD5' :  "<0xD5>",
    '\xD6' :  "<0xD6>",
    '\xD7' :  "<0xD7>",
    '\xD8' :  "<0xD8>",
    '\xD9' :  "<0xD9>",
    '\xDA' :  "<0xDA>",
    '\xDB' :  "<0xDB>",
    '\xDC' :  "<0xDC>",
    '\xDD' :  "<0xDD>",
    '\xDE' :  "<0xDE>",
    '\xDF' :  "<0xDF>",
    '\xE0' :  "<0xE0>",
    '\xE1' :  "<0xE1>",
    '\xE2' :  "<0xE2>",
    '\xE3' :  "<0xE3>",
    '\xE4' :  "<0xE4>",
    '\xE5' :  "<0xE5>",
    '\xE6' :  "<0xE6>",
    '\xE7' :  "<0xE7>",
    '\xE8' :  "<0xE8>",
    '\xE9' :  "<0xE9>",
    '\xEA' :  "<0xEA>",
    '\xEB' :  "<0xEB>",
    '\xEC' :  "<0xEC>",
    '\xED' :  "<0xED>",
    '\xEE' :  "<0xEE>",
    '\xEF' :  "<0xEF>",
    '\xF0' :  "<0xF0>",
    '\xF1' :  "<0xF1>",
    '\xF2' :  "<0xF2>",
    '\xF3' :  "<0xF3>",
    '\xF4' :  "<0xF4>",
    '\xF5' :  "<0xF5>",
    '\xF6' :  "<0xF6>",
    '\xF7' :  "<0xF7>",
    '\xF8' :  "<0xF8>",
    '\xF9' :  "<0xF9>",
    '\xFA' :  "<0xFA>",
    '\xFB' :  "<0xFB>",
    '\xFC' :  "<0xFC>",
    '\xFD' :  "<0xFD>",
    '\xFE' :  "<0xFE>",
    '\xFF' :  "<0xFF>",
    }


# for ascii2print(), mode="hexstring"

# hardcode for ascii2hexstring  >> very fast
# symbol
ascii2hexstring_symbol = {
    '\x00' :  "<0x00>",
    '\x01' :  "<0x01>",
    '\x02' :  "<0x02>",
    '\x03' :  "<0x03>",
    '\x04' :  "<0x04>",
    '\x05' :  "<0x05>",
    '\x06' :  "<0x06>",
    '\x07' :  "<0x07>",
    '\x08' :  "<0x08>",
    '\x09' :  "<0x09>",
    '\x0A' :  "<0x0A>",
    '\x0B' :  "<0x0B>",
    '\x0C' :  "<0x0C>",
    '\x0D' :  "<0x0D>",
    '\x0E' :  "<0x0E>",
    '\x0F' :  "<0x0F>",
    '\x10' :  "<0x10>",
    '\x11' :  "<0x11>",
    '\x12' :  "<0x12>",
    '\x13' :  "<0x13>",
    '\x14' :  "<0x14>",
    '\x15' :  "<0x15>",
    '\x16' :  "<0x16>",
    '\x17' :  "<0x17>",
    '\x18' :  "<0x18>",
    '\x19' :  "<0x19>",
    '\x1A' :  "<0x1A>",
    '\x1B' :  "<0x1B>",
    '\x1C' :  "<0x1C>",
    '\x1D' :  "<0x1D>",
    '\x1E' :  "<0x1E>",
    '\x1F' :  "<0x1F>",
    }

#printable
ascii2hexstring_printable = {
    '\x20' : "<0x20>",
    '\x21' : "<0x21>",
    '\x22' : "<0x22>",
    '\x23' : "<0x23>",
    '\x24' : "<0x24>",
    '\x25' : "<0x25>",
    '\x26' : "<0x26>",
    '\x27' : "<0x27>",
    '\x28' : "<0x28>",
    '\x29' : "<0x29>",
    '\x2A' : "<0x2A>",
    '\x2B' : "<0x2B>",
    '\x2C' : "<0x2C>",
    '\x2D' : "<0x2D>",
    '\x2E' : "<0x2E>",
    '\x2F' : "<0x2F>",
    '\x30' : "<0x30>",
    '\x31' : "<0x31>",
    '\x32' : "<0x32>",
    '\x33' : "<0x33>",
    '\x34' : "<0x34>",
    '\x35' : "<0x35>",
    '\x36' : "<0x36>",
    '\x37' : "<0x37>",
    '\x38' : "<0x38>",
    '\x39' : "<0x39>",
    '\x3A' : "<0x3A>",
    '\x3B' : "<0x3B>",
    '\x3C' : "<0x3C>",
    '\x3D' : "<0x3D>",
    '\x3E' : "<0x3E>",
    '\x3F' : "<0x3F>",
    '\x40' : "<0x40>",
    '\x41' : "<0x41>",
    '\x42' : "<0x42>",
    '\x43' : "<0x43>",
    '\x44' : "<0x44>",
    '\x45' : "<0x45>",
    '\x46' : "<0x46>",
    '\x47' : "<0x47>",
    '\x48' : "<0x48>",
    '\x49' : "<0x49>",
    '\x4A' : "<0x4A>",
    '\x4B' : "<0x4B>",
    '\x4C' : "<0x4C>",
    '\x4D' : "<0x4D>",
    '\x4E' : "<0x4E>",
    '\x4F' : "<0x4F>",
    '\x50' : "<0x50>",
    '\x51' : "<0x51>",
    '\x52' : "<0x52>",
    '\x53' : "<0x53>",
    '\x54' : "<0x54>",
    '\x55' : "<0x55>",
    '\x56' : "<0x56>",
    '\x57' : "<0x57>",
    '\x58' : "<0x58>",
    '\x59' : "<0x59>",
    '\x5A' : "<0x5A>",
    '\x5B' : "<0x5B>",
    '\x5C' : "<0x5C>",
    '\x5D' : "<0x5D>",
    '\x5E' : "<0x5E>",
    '\x5F' : "<0x5F>",
    '\x60' : "<0x60>",
    '\x61' : "<0x61>",
    '\x62' : "<0x62>",
    '\x63' : "<0x63>",
    '\x64' : "<0x64>",
    '\x65' : "<0x65>",
    '\x66' : "<0x66>",
    '\x67' : "<0x67>",
    '\x68' : "<0x68>",
    '\x69' : "<0x69>",
    '\x6A' : "<0x6A>",
    '\x6B' : "<0x6B>",
    '\x6C' : "<0x6C>",
    '\x6D' : "<0x6D>",
    '\x6E' : "<0x6E>",
    '\x6F' : "<0x6F>",
    '\x70' : "<0x70>",
    '\x71' : "<0x71>",
    '\x72' : "<0x72>",
    '\x73' : "<0x73>",
    '\x74' : "<0x74>",
    '\x75' : "<0x75>",
    '\x76' : "<0x76>",
    '\x77' : "<0x77>",
    '\x78' : "<0x78>",
    '\x79' : "<0x79>",
    '\x7A' : "<0x7A>",
    '\x7B' : "<0x7B>",
    '\x7C' : "<0x7C>",
    '\x7D' : "<0x7D>",
    '\x7E' : "<0x7E>",
    '\x7F' : "<0x7F>",
    }

# extendec ascii
ascii2hexstring_extended = {
    '\x80' : "<0x80>",
    '\x81' : "<0x81>",
    '\x82' : "<0x82>",
    '\x83' : "<0x83>",
    '\x84' : "<0x84>",
    '\x85' : "<0x85>",
    '\x86' : "<0x86>",
    '\x87' : "<0x87>",
    '\x88' : "<0x88>",
    '\x89' : "<0x89>",
    '\x8A' : "<0x8A>",
    '\x8B' : "<0x8B>",
    '\x8C' : "<0x8C>",
    '\x8D' : "<0x8D>",
    '\x8E' : "<0x8E>",
    '\x8F' : "<0x8F>",
    '\x90' : "<0x90>",
    '\x91' : "<0x91>",
    '\x92' : "<0x92>",
    '\x93' : "<0x93>",
    '\x94' : "<0x94>",
    '\x95' : "<0x95>",
    '\x96' : "<0x96>",
    '\x97' : "<0x97>",
    '\x98' : "<0x98>",
    '\x99' : "<0x99>",
    '\x9A' : "<0x9A>",
    '\x9B' : "<0x9B>",
    '\x9C' : "<0x9C>",
    '\x9D' : "<0x9D>",
    '\x9E' : "<0x9E>",
    '\x9F' : "<0x9F>",
    '\xA0' : "<0xA0>",
    '\xA1' : "<0xA1>",
    '\xA2' : "<0xA2>",
    '\xA3' : "<0xA3>",
    '\xA4' : "<0xA4>",
    '\xA5' : "<0xA5>",
    '\xA6' : "<0xA6>",
    '\xA7' : "<0xA7>",
    '\xA8' : "<0xA8>",
    '\xA9' : "<0xA9>",
    '\xAA' : "<0xAA>",
    '\xAB' : "<0xAB>",
    '\xAC' : "<0xAC>",
    '\xAD' : "<0xAD>",
    '\xAE' : "<0xAE>",
    '\xAF' : "<0xAF>",
    '\xB0' : "<0xB0>",
    '\xB1' : "<0xB1>",
    '\xB2' : "<0xB2>",
    '\xB3' : "<0xB3>",
    '\xB4' : "<0xB4>",
    '\xB5' : "<0xB5>",
    '\xB6' : "<0xB6>",
    '\xB7' : "<0xB7>",
    '\xB8' : "<0xB8>",
    '\xB9' : "<0xB9>",
    '\xBA' : "<0xBA>",
    '\xBB' : "<0xBB>",
    '\xBC' : "<0xBC>",
    '\xBD' : "<0xBD>",
    '\xBE' : "<0xBE>",
    '\xBF' : "<0xBF>",
    '\xC0' : "<0xC0>",
    '\xC1' : "<0xC1>",
    '\xC2' : "<0xC2>",
    '\xC3' : "<0xC3>",
    '\xC4' : "<0xC4>",
    '\xC5' : "<0xC5>",
    '\xC6' : "<0xC6>",
    '\xC7' : "<0xC7>",
    '\xC8' : "<0xC8>",
    '\xC9' : "<0xC9>",
    '\xCA' : "<0xCA>",
    '\xCB' : "<0xCB>",
    '\xCC' : "<0xCC>",
    '\xCD' : "<0xCD>",
    '\xCE' : "<0xCE>",
    '\xCF' : "<0xCF>",
    '\xD0' : "<0xD0>",
    '\xD1' : "<0xD1>",
    '\xD2' : "<0xD2>",
    '\xD3' : "<0xD3>",
    '\xD4' : "<0xD4>",
    '\xD5' : "<0xD5>",
    '\xD6' : "<0xD6>",
    '\xD7' : "<0xD7>",
    '\xD8' : "<0xD8>",
    '\xD9' : "<0xD9>",
    '\xDA' : "<0xDA>",
    '\xDB' : "<0xDB>",
    '\xDC' : "<0xDC>",
    '\xDD' : "<0xDD>",
    '\xDE' : "<0xDE>",
    '\xDF' : "<0xDF>",
    '\xE0' : "<0xE0>",
    '\xE1' : "<0xE1>",
    '\xE2' : "<0xE2>",
    '\xE3' : "<0xE3>",
    '\xE4' : "<0xE4>",
    '\xE5' : "<0xE5>",
    '\xE6' : "<0xE6>",
    '\xE7' : "<0xE7>",
    '\xE8' : "<0xE8>",
    '\xE9' : "<0xE9>",
    '\xEA' : "<0xEA>",
    '\xEB' : "<0xEB>",
    '\xEC' : "<0xEC>",
    '\xED' : "<0xED>",
    '\xEE' : "<0xEE>",
    '\xEF' : "<0xEF>",
    '\xF0' : "<0xF0>",
    '\xF1' : "<0xF1>",
    '\xF2' : "<0xF2>",
    '\xF3' : "<0xF3>",
    '\xF4' : "<0xF4>",
    '\xF5' : "<0xF5>",
    '\xF6' : "<0xF6>",
    '\xF7' : "<0xF7>",
    '\xF8' : "<0xF8>",
    '\xF9' : "<0xF9>",
    '\xFA' : "<0xFA>",
    '\xFB' : "<0xFB>",
    '\xFC' : "<0xFC>",
    '\xFD' : "<0xFD>",
    '\xFE' : "<0xFE>",
    '\xFF' : "<0xFF>",
    }

# for mode="hexstring", fast convertion for printable ascii , ord()+128
ascii2hexstring_printable_tempsymbol = {
    '\x20' : "\xBC\xB0\xF8\xA0\xBE",
    '\x21' : "\xBC\xB0\xF8\xA1\xBE",
    '\x22' : "\xBC\xB0\xF8\xA2\xBE",
    '\x23' : "\xBC\xB0\xF8\xA3\xBE",
    '\x24' : "\xBC\xB0\xF8\xA4\xBE",
    '\x25' : "\xBC\xB0\xF8\xA5\xBE",
    '\x26' : "\xBC\xB0\xF8\xA6\xBE",
    '\x27' : "\xBC\xB0\xF8\xA7\xBE",
    '\x28' : "\xBC\xB0\xF8\xA8\xBE",
    '\x29' : "\xBC\xB0\xF8\xA9\xBE",
    '\x2A' : "\xBC\xB0\xF8\xAA\xBE",
    '\x2B' : "\xBC\xB0\xF8\xAB\xBE",
    '\x2C' : "\xBC\xB0\xF8\xAC\xBE",
    '\x2D' : "\xBC\xB0\xF8\xAD\xBE",
    '\x2E' : "\xBC\xB0\xF8\xAE\xBE",
    '\x2F' : "\xBC\xB0\xF8\xAF\xBE",
    '\x30' : "\xBC\xB0\xF8\xB0\xBE",
    '\x31' : "\xBC\xB0\xF8\xB1\xBE",
    '\x32' : "\xBC\xB0\xF8\xB2\xBE",
    '\x33' : "\xBC\xB0\xF8\xB3\xBE",
    '\x34' : "\xBC\xB0\xF8\xB4\xBE",
    '\x35' : "\xBC\xB0\xF8\xB5\xBE",
    '\x36' : "\xBC\xB0\xF8\xB6\xBE",
    '\x37' : "\xBC\xB0\xF8\xB7\xBE",
    '\x38' : "\xBC\xB0\xF8\xB8\xBE",
    '\x39' : "\xBC\xB0\xF8\xB9\xBE",
    '\x3A' : "\xBC\xB0\xF8\xBA\xBE",
    '\x3B' : "\xBC\xB0\xF8\xBB\xBE",
    '\x3C' : "\xBC\xB0\xF8\xBC\xBE",
    '\x3D' : "\xBC\xB0\xF8\xBD\xBE",
    '\x3E' : "\xBC\xB0\xF8\xBE\xBE",
    '\x3F' : "\xBC\xB0\xF8\xBF\xBE",
    '\x40' : "\xBC\xB0\xF8\xC0\xBE",
    '\x41' : "\xBC\xB0\xF8\xC1\xBE",
    '\x42' : "\xBC\xB0\xF8\xC2\xBE",
    '\x43' : "\xBC\xB0\xF8\xC3\xBE",
    '\x44' : "\xBC\xB0\xF8\xC4\xBE",
    '\x45' : "\xBC\xB0\xF8\xC5\xBE",
    '\x46' : "\xBC\xB0\xF8\xC6\xBE",
    '\x47' : "\xBC\xB0\xF8\xC7\xBE",
    '\x48' : "\xBC\xB0\xF8\xC8\xBE",
    '\x49' : "\xBC\xB0\xF8\xC9\xBE",
    '\x4A' : "\xBC\xB0\xF8\xCA\xBE",
    '\x4B' : "\xBC\xB0\xF8\xCB\xBE",
    '\x4C' : "\xBC\xB0\xF8\xCC\xBE",
    '\x4D' : "\xBC\xB0\xF8\xCD\xBE",
    '\x4E' : "\xBC\xB0\xF8\xCE\xBE",
    '\x4F' : "\xBC\xB0\xF8\xCF\xBE",
    '\x50' : "\xBC\xB0\xF8\xD0\xBE",
    '\x51' : "\xBC\xB0\xF8\xD1\xBE",
    '\x52' : "\xBC\xB0\xF8\xD2\xBE",
    '\x53' : "\xBC\xB0\xF8\xD3\xBE",
    '\x54' : "\xBC\xB0\xF8\xD4\xBE",
    '\x55' : "\xBC\xB0\xF8\xD5\xBE",
    '\x56' : "\xBC\xB0\xF8\xD6\xBE",
    '\x57' : "\xBC\xB0\xF8\xD7\xBE",
    '\x58' : "\xBC\xB0\xF8\xD8\xBE",
    '\x59' : "\xBC\xB0\xF8\xD9\xBE",
    '\x5A' : "\xBC\xB0\xF8\xDA\xBE",
    '\x5B' : "\xBC\xB0\xF8\xDB\xBE",
    '\x5C' : "\xBC\xB0\xF8\xDC\xBE",
    '\x5D' : "\xBC\xB0\xF8\xDD\xBE",
    '\x5E' : "\xBC\xB0\xF8\xDE\xBE",
    '\x5F' : "\xBC\xB0\xF8\xDF\xBE",
    '\x60' : "\xBC\xB0\xF8\xE0\xBE",
    '\x61' : "\xBC\xB0\xF8\xE1\xBE",
    '\x62' : "\xBC\xB0\xF8\xE2\xBE",
    '\x63' : "\xBC\xB0\xF8\xE3\xBE",
    '\x64' : "\xBC\xB0\xF8\xE4\xBE",
    '\x65' : "\xBC\xB0\xF8\xE5\xBE",
    '\x66' : "\xBC\xB0\xF8\xE6\xBE",
    '\x67' : "\xBC\xB0\xF8\xE7\xBE",
    '\x68' : "\xBC\xB0\xF8\xE8\xBE",
    '\x69' : "\xBC\xB0\xF8\xE9\xBE",
    '\x6A' : "\xBC\xB0\xF8\xEA\xBE",
    '\x6B' : "\xBC\xB0\xF8\xEB\xBE",
    '\x6C' : "\xBC\xB0\xF8\xEC\xBE",
    '\x6D' : "\xBC\xB0\xF8\xED\xBE",
    '\x6E' : "\xBC\xB0\xF8\xEE\xBE",
    '\x6F' : "\xBC\xB0\xF8\xEF\xBE",
    '\x70' : "\xBC\xB0\xF8\xF0\xBE",
    '\x71' : "\xBC\xB0\xF8\xF1\xBE",
    '\x72' : "\xBC\xB0\xF8\xF2\xBE",
    '\x73' : "\xBC\xB0\xF8\xF3\xBE",
    '\x74' : "\xBC\xB0\xF8\xF4\xBE",
    '\x75' : "\xBC\xB0\xF8\xF5\xBE",
    '\x76' : "\xBC\xB0\xF8\xF6\xBE",
    '\x77' : "\xBC\xB0\xF8\xF7\xBE",
    '\x78' : "\xBC\xB0\xF8\xF8\xBE",
    '\x79' : "\xBC\xB0\xF8\xF9\xBE",
    '\x7A' : "\xBC\xB0\xF8\xFA\xBE",
    '\x7B' : "\xBC\xB0\xF8\xFB\xBE",
    '\x7C' : "\xBC\xB0\xF8\xFC\xBE",
    '\x7D' : "\xBC\xB0\xF8\xFD\xBE",
    '\x7E' : "\xBC\xB0\xF8\xFE\xBE",
    '\x7F' : "\xBC\xB0\xF8\xFF\xBE",
    }

ascii2hexstring_printable_revert = {
    '\xBC\xB0\xF8\xA0\xBE' : "<0x20>",
    '\xBC\xB0\xF8\xA1\xBE' : "<0x21>",
    '\xBC\xB0\xF8\xA2\xBE' : "<0x22>",
    '\xBC\xB0\xF8\xA3\xBE' : "<0x23>",
    '\xBC\xB0\xF8\xA4\xBE' : "<0x24>",
    '\xBC\xB0\xF8\xA5\xBE' : "<0x25>",
    '\xBC\xB0\xF8\xA6\xBE' : "<0x26>",
    '\xBC\xB0\xF8\xA7\xBE' : "<0x27>",
    '\xBC\xB0\xF8\xA8\xBE' : "<0x28>",
    '\xBC\xB0\xF8\xA9\xBE' : "<0x29>",
    '\xBC\xB0\xF8\xAA\xBE' : "<0x2A>",
    '\xBC\xB0\xF8\xAB\xBE' : "<0x2B>",
    '\xBC\xB0\xF8\xAC\xBE' : "<0x2C>",
    '\xBC\xB0\xF8\xAD\xBE' : "<0x2D>",
    '\xBC\xB0\xF8\xAE\xBE' : "<0x2E>",
    '\xBC\xB0\xF8\xAF\xBE' : "<0x2F>",
    '\xBC\xB0\xF8\xB0\xBE' : "<0x30>",
    '\xBC\xB0\xF8\xB1\xBE' : "<0x31>",
    '\xBC\xB0\xF8\xB2\xBE' : "<0x32>",
    '\xBC\xB0\xF8\xB3\xBE' : "<0x33>",
    '\xBC\xB0\xF8\xB4\xBE' : "<0x34>",
    '\xBC\xB0\xF8\xB5\xBE' : "<0x35>",
    '\xBC\xB0\xF8\xB6\xBE' : "<0x36>",
    '\xBC\xB0\xF8\xB7\xBE' : "<0x37>",
    '\xBC\xB0\xF8\xB8\xBE' : "<0x38>",
    '\xBC\xB0\xF8\xB9\xBE' : "<0x39>",
    '\xBC\xB0\xF8\xBA\xBE' : "<0x3A>",
    '\xBC\xB0\xF8\xBB\xBE' : "<0x3B>",
    '\xBC\xB0\xF8\xBC\xBE' : "<0x3C>",
    '\xBC\xB0\xF8\xBD\xBE' : "<0x3D>",
    '\xBC\xB0\xF8\xBE\xBE' : "<0x3E>",
    '\xBC\xB0\xF8\xBF\xBE' : "<0x3F>",
    '\xBC\xB0\xF8\xC0\xBE' : "<0x40>",
    '\xBC\xB0\xF8\xC1\xBE' : "<0x41>",
    '\xBC\xB0\xF8\xC2\xBE' : "<0x42>",
    '\xBC\xB0\xF8\xC3\xBE' : "<0x43>",
    '\xBC\xB0\xF8\xC4\xBE' : "<0x44>",
    '\xBC\xB0\xF8\xC5\xBE' : "<0x45>",
    '\xBC\xB0\xF8\xC6\xBE' : "<0x46>",
    '\xBC\xB0\xF8\xC7\xBE' : "<0x47>",
    '\xBC\xB0\xF8\xC8\xBE' : "<0x48>",
    '\xBC\xB0\xF8\xC9\xBE' : "<0x49>",
    '\xBC\xB0\xF8\xCA\xBE' : "<0x4A>",
    '\xBC\xB0\xF8\xCB\xBE' : "<0x4B>",
    '\xBC\xB0\xF8\xCC\xBE' : "<0x4C>",
    '\xBC\xB0\xF8\xCD\xBE' : "<0x4D>",
    '\xBC\xB0\xF8\xCE\xBE' : "<0x4E>",
    '\xBC\xB0\xF8\xCF\xBE' : "<0x4F>",
    '\xBC\xB0\xF8\xD0\xBE' : "<0x50>",
    '\xBC\xB0\xF8\xD1\xBE' : "<0x51>",
    '\xBC\xB0\xF8\xD2\xBE' : "<0x52>",
    '\xBC\xB0\xF8\xD3\xBE' : "<0x53>",
    '\xBC\xB0\xF8\xD4\xBE' : "<0x54>",
    '\xBC\xB0\xF8\xD5\xBE' : "<0x55>",
    '\xBC\xB0\xF8\xD6\xBE' : "<0x56>",
    '\xBC\xB0\xF8\xD7\xBE' : "<0x57>",
    '\xBC\xB0\xF8\xD8\xBE' : "<0x58>",
    '\xBC\xB0\xF8\xD9\xBE' : "<0x59>",
    '\xBC\xB0\xF8\xDA\xBE' : "<0x5A>",
    '\xBC\xB0\xF8\xDB\xBE' : "<0x5B>",
    '\xBC\xB0\xF8\xDC\xBE' : "<0x5C>",
    '\xBC\xB0\xF8\xDD\xBE' : "<0x5D>",
    '\xBC\xB0\xF8\xDE\xBE' : "<0x5E>",
    '\xBC\xB0\xF8\xDF\xBE' : "<0x5F>",
    '\xBC\xB0\xF8\xE0\xBE' : "<0x60>",
    '\xBC\xB0\xF8\xE1\xBE' : "<0x61>",
    '\xBC\xB0\xF8\xE2\xBE' : "<0x62>",
    '\xBC\xB0\xF8\xE3\xBE' : "<0x63>",
    '\xBC\xB0\xF8\xE4\xBE' : "<0x64>",
    '\xBC\xB0\xF8\xE5\xBE' : "<0x65>",
    '\xBC\xB0\xF8\xE6\xBE' : "<0x66>",
    '\xBC\xB0\xF8\xE7\xBE' : "<0x67>",
    '\xBC\xB0\xF8\xE8\xBE' : "<0x68>",
    '\xBC\xB0\xF8\xE9\xBE' : "<0x69>",
    '\xBC\xB0\xF8\xEA\xBE' : "<0x6A>",
    '\xBC\xB0\xF8\xEB\xBE' : "<0x6B>",
    '\xBC\xB0\xF8\xEC\xBE' : "<0x6C>",
    '\xBC\xB0\xF8\xED\xBE' : "<0x6D>",
    '\xBC\xB0\xF8\xEE\xBE' : "<0x6E>",
    '\xBC\xB0\xF8\xEF\xBE' : "<0x6F>",
    '\xBC\xB0\xF8\xF0\xBE' : "<0x70>",
    '\xBC\xB0\xF8\xF1\xBE' : "<0x71>",
    '\xBC\xB0\xF8\xF2\xBE' : "<0x72>",
    '\xBC\xB0\xF8\xF3\xBE' : "<0x73>",
    '\xBC\xB0\xF8\xF4\xBE' : "<0x74>",
    '\xBC\xB0\xF8\xF5\xBE' : "<0x75>",
    '\xBC\xB0\xF8\xF6\xBE' : "<0x76>",
    '\xBC\xB0\xF8\xF7\xBE' : "<0x77>",
    '\xBC\xB0\xF8\xF8\xBE' : "<0x78>",
    '\xBC\xB0\xF8\xF9\xBE' : "<0x79>",
    '\xBC\xB0\xF8\xFA\xBE' : "<0x7A>",
    '\xBC\xB0\xF8\xFB\xBE' : "<0x7B>",
    '\xBC\xB0\xF8\xFC\xBE' : "<0x7C>",
    '\xBC\xB0\xF8\xFD\xBE' : "<0x7D>",
    '\xBC\xB0\xF8\xFE\xBE' : "<0x7E>",
    '\xBC\xB0\xF8\xFF\xBE' : "<0x7F>",
    }


class _AT():
    """
    It's an _AT port object class and provide the method to operate the port. you can init an AT port object instance(DUT1/DUT2/any).

    """

    name = '_AT'

    objs = {}

    def __init__(self, conf):
        """
        _AT constructor function, init and open serial port

        Args:
            conf : The com serial config

        Returns:
            none

        """
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
        """
        Open AT port, maybe you shouldn't use it, because the initialization of the port is already ready before running the case.

        Examples:
            open("/dev/acis/DUT1/AT")

        Kwargs:
            port : the AT serial port
            baudrate : the baudrate of the port
            bytesize : the bytesize of the port
            parity : the parity of the port
            stopbits : the stopbits of the port
            rtscts :  I/o for request/clear to send signal
            OpenPortTimeout: detect port timeout
            timeout:  Read timeout
            dsrdtr: I/O for Data ready signal
            xonxoff: software flow control
            interCharTimeout: Character interval timeout
            write_timeout: write timeout

        Returns:
            return serial port instance.
        """

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
        """
        Reopen serial port, it's will close and reopen the ports.

        Examples:
            reopen()

        Kwargs:
            cfun_delay_time : the delay time to exec the function

        Returns:
            return the callback open.
        """

        self.close()
        self.sleep(cfun_delay_time)

        return self.open(self.hCom.port,
                         self.hCom.baudrate,
                         self.hCom.bytesize,
                         self.hCom.parity,
                         self.hCom.stopbits)

    @allure.step
    def detect_port(self, port, timeout=2000, logmsg="logmsg"):
        """
        Detect the serial port

        Examples:
            detect_port("/dev/acis/DUT1/AT")

        Args:
            port : the serial port you want to detect.

        Kwargs:
            timeout : detect port timeout
            logmsg:     logmsg, peer with log message.\n
                        debug, peer with log and debug message.\n
                        nologmsg, peer without any message. \n

        Returns:
            none.
        """

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
        """
        Call the time module and execute sleep function.

        Examples:
            sleep(1000)

        Args:
            millisecond : sleep time(ms).

        Kwargs:
            silent: It's a bool flag to control whether to print sleep time log or not

        Returns:
            none

        """
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
        """
        The method will close and release the occupation of the port.

        Examples:
            close()

        Args:
            none

        Returns:
            none
        """
        try:
            self.hCom.close()

            peer("CLOSE: Close the "+self.hCom.port)
        except Exception as e:
            peer(e)
            peer("CLOSE: Error for "+self.hCom.port)

    def timeDisplay(self, dt = None):
        """
        Display the time, if dt is empty retrun actual date time under format, otherless return dt under format

        Examples:
            timeDisplay()

        Kwargs:
            dt : date time.

        Returns:
            date Time under format hh:mm:ss:???.

        """
        if dt == None:
            dt = datetime.now()
        return "(%0.2d:%0.2d:%0.2d:%0.3d)"%(dt.hour, dt.minute, dt.second, dt.microsecond/1000)

    @allure.step
    def send_cmd(self, cmd, printmode="symbol"):
        """
        Sends an AT command to a serial port.

        Examples:
            send_cmd("ATE0\r")

        Args:
            cmd: the AT command you want to send.

        Kwargs:
            printmode: the log print mode(symbol, hexstring, raw)

        Returns:
            none.

        """
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
        """
        ASCII convert

        Examples:
            ascii2print("ATE0\r", mode="symbol")

        Args:
            inputstring: the inputstring need to be coverted.

        Kwargs:
            mode: convert mode(symbol, hexstring, raw)

        Returns:
            the convert outputstring.

        """

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
        """
        The method clears the input buffer of serial port instance

        Examples:
            clean_buffer()

        Args:
            none

        Returns:
            none.

        """
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
        """
        Parses the contents of the serial buffer and provide some specified filtering conditions.

        Examples:
            waitn_match_resp(["*\r\nOK\r\n"], 4000)

        Args:
            waitpattern: the matching pattern for the received data
            timeout: timeout value in second

        Kwargs:
            update_result:  critical, update result to global variable statOfItem \n
                            not_critical, do nothing for the result \n
            condition:      matching condition
            log_msg:    logmsg, peer with log message.\n
                        debug, peer with log and debug message.\n
                        nologmsg, peer without any message. \n
            printmode: the log print mode(symbol, hexstring, raw)

        Returns:
            match result.

        """
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
        """
        The method compares the received command response to the expected command response and display the comparison result,maybe you should use waitn_match_resp instead of this.

        Args:
            resp : Response object or a string
            keywords: expected response

        Kwargs:
            condition : matching condition
            update_result:      critical, update result to global variable statOfItem  \n
                                not_critical, do nothing for the result\n
            log_msg:    logmsg, peer with log message\n
                        debug, peer with log and debug message\n
                        nologmsg, peer without any message\n
            printmode: the log print mode(symbol, hexstring, raw)

        Returns:
            Boolean >> True:response matched, False:repsonse mis-matched"

        """
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
        """
        The method waits for the data received from serial port.

        Examples:
            wait_resp(["*\r\nOK\r\n"], 4000)

        Args:
            waitpattern : the matching pattern for the received data.

        Kwargs:
            timeout : timeout between each received packet
            log_msg : option for log message
            printmode: the log print mode(symbol, hexstring, raw)

        Returns:
            Received data (String).

        """
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
    """
    It's an AT port class, it's will from _AT class to init the AT port object instance

    """
    name = "AT"

    def __init__(self, obj, conf):
        """
        AT constructor function, init the _AT class to get an AT port object instance

        Args:
            obj: the AT port object instance name
            conf: The AT com port config

        Returns:
            none

        """

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
        """
        The method will reinit an AT port object instance.

        Args:
            obj: the object you want to init.
            conf: the object config.

        Returns:
            return the initialized object
        """

        if obj == "DUT1":
            self.conf["DUT1"] = conf
            self.DUT1 = _AT(conf)
        else:
            self.conf["DUT2"] = conf
            self.DUT2 = _AT(conf)
        return self

    @allure.step
    def closeall(self):
        """
        The method will close and release all open port.

        Args:
            none

        Returns:
            none.
        """

        if self.DUT1:
            self.DUT1.close()
        if self.DUT2:
            self.DUT2.close()
        if self.any:
            self.any.close()

    def info(self):
        peer("My name is : {name}\n- conf:\n<{conf}>".format(name = AT.name, conf = self.conf))
