import time 

file_name = "misc/UM3_hourglass3.gcode"

lines = []
linesxy = []
lineDict = {}
lineNum = 0
lastZ = 0.0
zval = 0
zstart = 0
with open(file_name) as fp:
    while True:
        lineNum += 1
        line = fp.readline()
        if "Z" in line and ";" not in line:
            idx = line.find("Z")
            zval = line[idx:-1]
            if not zstart:
                zstart = 1 if "Z0.27" in line else 0

            if zstart:
                if float(zval[1:]) > lastZ:
                    lineDict[zval] = {"lines":[str(line[:-1])], "Z":str(zval[1:]), "lineNr": lineNum}
                    lastZ = float(zval[1:])
            
        if "G" in line and zstart:
            lineDict[zval]["lines"].append(str(line[:-1]))
            lines.append(line[:-1])
            split_line = line.split()
            xword = [word for word in split_line if word[0] is "X"]
            yword = [word for word in split_line if word[0] is "Y"]
            if xword and yword:
                linesxy.append([xword[0]+" "+yword[0]])
        if not line:
            break

t1 = time.time()
lines.index("G280")
t2 = time.time()
print(float(t2-t1))
print(lines)