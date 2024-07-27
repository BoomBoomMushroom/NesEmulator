import os

with open("nestest.log.txt", "r") as f:
    nesTestLogs = f.read().splitlines()

with open("cpuOutputLog.txt", "r") as f:
    cpuLogs = f.read().splitlines()

#os.system("cls")
for i in range(0, len(cpuLogs)):
    cpuLog = cpuLogs[i].split("PPU:")[0]
    nesTestLog = nesTestLogs[i].split("PPU:")[0]
    
    if "*NOP" in nesTestLog: continue
    if cpuLog == nesTestLog: continue
    
    print(f"Mismatch!\n{cpuLog}\n{nesTestLog}")
    break