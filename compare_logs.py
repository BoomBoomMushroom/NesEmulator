cpuLogs = []
nestestLogs = []

with open("logs.txt", "r") as f:
    cpuLogs = f.readlines()

with open("nestest.txt", "r") as f:
    nestestLogs = f.readlines()

totalCPUInstructions = len(cpuLogs)
totalNESTESTInstructions =  len(nestestLogs)

for i in range(0, min(totalCPUInstructions,totalNESTESTInstructions)):
    cpu = cpuLogs[i].upper().split("PPU:")[0]
    nestest = nestestLogs[i].upper().split("PPU:")[0]
    
    if cpu == nestest:
        print(nestest, "\t✅")
    else:
        print("\n"*2)
        print(cpu, "\t❌\tYour CPU")
        print(nestest, "\t<---\tNESTEST")
        print(f"Worked for {i} instructions")
        break

print(f"Total NESTEST instructions: {totalNESTESTInstructions}")
print(f"NESTEST Total Instructions minus Your CPU's = {totalNESTESTInstructions - totalCPUInstructions}")

