import sys,os,re,time
import soar_sml as S
d,main,maxd=sys.argv[1],sys.argv[2],int(sys.argv[3])
k=S.Kernel.CreateKernelInNewThread(); a=k.CreateAgent('a'); out=[]
a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid,ud,ag,msg: out.append(msg), None)
os.chdir(d); r=a.ExecuteCommandLine('source '+main)
m=re.search(r'Total: \d+ productions sourced.*',r); print(m.group(0) if m else r[-600:])
a.ExecuteCommandLine('watch 0'); acts=[]; t=time.time()
for step in range(maxd):
    a.RunSelf(1)
    for i in range(a.GetNumberCommands()):
        c=a.GetCommand(i)
        if c.GetCommandName()=='perform-action' and c.GetParameterValue('status') is None:
            acts.append((c.GetParameterValue('name'),c.GetParameterValue('argument1'),c.GetParameterValue('argument2'))); c.AddStatusComplete()
    a.Commit(); a.ClearOutputLinkChanges()
    if 'success' in a.ExecuteCommandLine('print (s1 ^success *)'): print('SUCCESS at step',step+1); break
print('actions:',len(acts),acts)
print(a.ExecuteCommandLine('stats').splitlines()[2:6], round(time.time()-t,1),'s')
txt="".join(out); print(txt[:int(sys.argv[4])] if len(sys.argv)>4 else txt[-2500:])
k.Shutdown()
