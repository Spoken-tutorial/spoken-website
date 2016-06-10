import math

def convert_to_html(rawdata):
    splchars = {
        39: '&#39;',
        40: '&#40;',
        41: '&#41;',
        47: '&#47;',
        92: '&#92;',
        32: '&nbsp;',
        34: '&quot;',
        38: '&amp;',
        60: '&lt;',
        62: '&gt;',
        198: '&AElig;',
        193: '&Aacute;',
        194: '&Acirc;',
        192: '&Agrave;',
        197: '&Aring;',
        195: '&Atilde;',
        196: '&Auml;',
        199: '&Ccedil;',
        208: '&ETH;',
        201: '&Eacute;',
        202: '&Ecirc;',
        200: '&Egrave;',
        203: '&Euml;',
        205: '&Iacute;',
        206: '&Icirc;',
        204: '&Igrave;',
        207: '&Iuml;',
        209: '&Ntilde;',
        211: '&Oacute;',
        212: '&Ocirc;',
        210: '&Ograve;',
        216: '&Oslash;',
        213: '&Otilde;',
        214: '&Ouml;',
        222: '&THORN;',
        218: '&Uacute;',
        219: '&Ucirc;',
        217: '&Ugrave;',
        220: '&Uuml;',
        221: '&Yacute;',
        225: '&aacute;',
        226: '&acirc;',
        230: '&aelig;',
        224: '&agrave;',
        229: '&aring;',
        227: '&atilde;',
        228: '&auml;',
        231: '&ccedil;',
        233: '&eacute;',
        234: '&ecirc;',
        232: '&egrave;',
        240: '&eth;',
        235: '&euml;',
        237: '&iacute;',
        238: '&icirc;',
        236: '&igrave;',
        239: '&iuml;',
        241: '&ntilde;',
        243: '&oacute;',
        244: '&ocirc;',
        242: '&ograve;',
        248: '&oslash;',
        245: '&otilde;',
        246: '&ouml;',
        223: '&szlig;',
        254: '&thorn;',
        250: '&uacute;',
        251: '&ucirc;',
        249: '&ugrave;',
        252: '&uuml;',
        253: '&yacute;',
        255: '&yuml;',
        162: '&cent;',
    }
    hex_data = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    result_data = ''
    for rch in rawdata:
        ch = ord(rch)
        if ch == 10:
            result_data = result_data + '<br/>'
        elif ch in splchars:
            result_data = result_data + splchars[ch]
        elif ch > 127:
            c = ch;
            a4 = int(c % 16);
            c = math.floor(c / 16);
            a3 = int(c % 16);
            c = math.floor(c / 16);
            a2 = int(c % 16);
            c = math.floor(c / 16);
            a1 = int(c % 16);
            tmp_hex = '&#x' + hex_data[a1] + hex_data[a2] + hex_data[a3] + hex_data[a4] + ';'
            result_data = result_data + tmp_hex
        else:
            result_data = result_data + rch
    return result_data
