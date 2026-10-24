# Ghidra Jython post-script. Run only through analyzeHeadless.
# @category XenonHarness

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

args = getScriptArgs()
if not args:
    raise RuntimeError("ExportEvidence.py requires an output directory")
out_dir = args[0]
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

decompiler = DecompInterface()
decompiler.openProgram(currentProgram)
monitor = ConsoleTaskMonitor()
listing = currentProgram.getListing()
refs = currentProgram.getReferenceManager()
fm = currentProgram.getFunctionManager()
manifest = []


def names(iterator):
    result = []
    while iterator.hasNext():
        f = iterator.next()
        result.append("0x%08X %s" % (f.getEntryPoint().getOffset(), f.getName()))
    return result


for function in fm.getFunctions(True):
    entry = function.getEntryPoint()
    body = function.getBody()
    address = entry.getOffset()
    filename = "%08X.json" % address
    instructions = []
    it = listing.getInstructions(body, True)
    while it.hasNext():
        ins = it.next()
        instructions.append("%s  %s" % (ins.getAddress(), ins.toString()))

    callers = []
    rit = refs.getReferencesTo(entry)
    while rit.hasNext():
        ref = rit.next()
        caller = fm.getFunctionContaining(ref.getFromAddress())
        if caller:
            callers.append("0x%08X %s" % (caller.getEntryPoint().getOffset(), caller.getName()))

    callees = names(function.getCalledFunctions(monitor).iterator())
    decomp = decompiler.decompileFunction(function, 30, monitor)
    c_text = decomp.getDecompiledFunction().getC() if decomp.decompileCompleted() else ""
    payload = {
        "address": "0x%08X" % address,
        "name": function.getName(),
        "size": body.getNumAddresses(),
        "callers": sorted(set(callers)),
        "callees": sorted(set(callees)),
        "strings": [],
        "globals": [],
        "decompilation": c_text,
        "disassembly": "\n".join(instructions),
    }
    with open(os.path.join(out_dir, filename), "w") as handle:
        json.dump(payload, handle, indent=2)
    manifest.append({"address": payload["address"], "name": payload["name"], "evidence": filename})

with open(os.path.join(out_dir, "functions.json"), "w") as handle:
    json.dump(manifest, handle, indent=2)

decompiler.dispose()
print("XenonHarness exported %d functions" % len(manifest))
