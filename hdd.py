__module_name__ = "hdd"
__module_version__ = "1.0"
__module_description__ = "Sends HDD info"

import hexchat, win32api, ctypes, sys, collections

def getHDDList():
    drives = win32api.GetLogicalDriveStrings()
    return drives.split('\000')[:-1]
    
def formatSIPrefix(number):
    if number != 0: # Too tired to do this properly.
        prefixes = collections.OrderedDict(((1000000000000000000000000, ("Y", "yotta", 24)),
                    (1000000000000000000000, ("Z", "zetta", 21)),
                    (1000000000000000000, ("E", "exa", 18)),
                    (1000000000000000, ("P", "peta", 15)),
                    (1000000000000, ("T", "tera", 12)),
                    (1000000000, ("G", "giga", 9)),
                    (1000000, ("M", "mega", 6)),
                    (1000, ("k", "kilo", 3)),
                    (1, ("", "", 0)),
                    (0.001, ("m", "milli", -3)),
                    (0.000001, ("μ", "micro", -6)),
                    (0.000000001, ("n", "nano", -9)),
                    (0.000000000001, ("p", "pico", -12)),
                    (0.000000000000001, ("f", "femto", -15)),
                    (0.000000000000000001, ("a", "atto", -18)),
                    (0.000000000000000000001, ("z", "zepto", -21)),
                    (0.000000000000000000000001, ("y", "yocto", -24))))
        number = float(number)
        for minimum, prefix in prefixes.items():
            if number >= float(minimum):
                prefix_to_use = prefix
                break
        short_prefix = prefix_to_use[0]
        long_prefix = prefix_to_use[1]
        value = number * (10**(-prefix_to_use[2]))
        return (value, short_prefix, long_prefix)
    return (0, "", "")
    
def disk_usage(path):
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
    _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
                       ctypes.c_ulonglong()
    if sys.version_info >= (3,) or isinstance(path, unicode):
        fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
    else:
        fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
    ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
    #if ret == 0:
        #raise ctypes.WinError()
    used = total.value - free.value
    return _ntuple_diskusage(total.value, used, free.value)

def getHDDInfo(word, word_eol, userdata):
    HDDList = getHDDList()
    output = []
    overallFree = 0
    overallTotal = 0
    #stats = collections.OrderedDict((("Total", (0, 0)),))
    stats = collections.OrderedDict()
    for letter in HDDList:
        try:
            data = disk_usage(letter)
            totalSpace = data[0]
            freeSpace = data[2]
            if totalSpace != 0:
                stats[letter] = (freeSpace, totalSpace)
                overallFree += freeSpace
                overallTotal += totalSpace
        except:
            pass
    stats["Total"] = (overallFree, overallTotal)
    
    
    for letter, info in stats.items():
        totalSpace = info[1]
        freeSpace = info[0]
        percent = 100 * (freeSpace / totalSpace)
        fifths = int(round(percent / 5, 0))
        bar = "%s%s" % ("■" * (20 - fifths), "-" * fifths)
        totalSpaceStr = "%s%sB" % (str(round(formatSIPrefix(totalSpace)[0], 2)), formatSIPrefix(totalSpace)[1])
        freeSpaceStr = "%s%sB" % (str(round(formatSIPrefix(freeSpace)[0], 2)), formatSIPrefix(freeSpace)[1])
        
        if percent > 20:
            output.append("11%s [%s] 07%s (%s%%) Free 03[%s]" % (letter, totalSpaceStr, freeSpaceStr, str(round(percent, 1)), bar))
        else:
            output.append("11%s [%s] 07%s (%s%%) Free 04[%s]" % (letter, totalSpaceStr, freeSpaceStr, str(round(percent, 1)), bar))
    
    for line in output:
        hexchat.command("SAY %s" % line)

    return hexchat.EAT_HEXCHAT

hexchat.hook_command("hdd", getHDDInfo, help="")
