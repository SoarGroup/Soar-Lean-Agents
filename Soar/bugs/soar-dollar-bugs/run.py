import sys
B = __import__("os").environ.get("SOAR_BIN", ".")   # folder with the Soar Python SML bindings
sys.path[:0]=[B]
import Python_sml_ClientInterface as S
k=S.Kernel.CreateKernelInNewThread(0); a=k.CreateAgent('a'); out=[]
a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda m,u,ag,msg: out.append(msg), None)
for c in ['source '+sys.argv[1]]+sys.argv[2:]: a.ExecuteCommandLine(c)
a.ExecuteCommandLine('watch 1'); a.ExecuteCommandLine('run 10')
print(''.join(out)); k.Shutdown()
