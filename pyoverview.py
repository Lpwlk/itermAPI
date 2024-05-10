import psutil, os, time, sys
from rich.status import Status
from rich.live import Live
from rich.console import Console, Group
from rich import inspect

console = Console(highlight=True)
            
def processState(proc):
    return f'{proc.cmdline()[1].split('/')[-1].ljust(16, ' ')} | pid: {proc.pid} | cpu usage - 100ms {fmtCPUload(proc)}% | 10ms = {fmtCPUload(proc)}%'

def fmtCPUload(process, bycores = 0):
    return str(process.cpu_percent(interval = .1)/(1+bycores*(n_cores-1)))[:5].rjust(5, ' ')

n_proc = 6
n_cores = psutil.cpu_count()
current_pid = os.getpid()

main_status = Status('', console = console)
statuses = [Status(status = 'Empty status', console = console) for _ in range(n_proc)]
statuses.append(main_status)
clear_cmd = 'clear && printf "\\e[3J"\n'
os.system(clear_cmd)

with Live(Group(*statuses), refresh_per_second=12):
    main_status.update(f'[green]Dynamic tracking of {n_proc} python processes')
    while True:
        processes = []
        for proc in psutil.process_iter():
            if proc.name() == 'Python':
                processes.append(proc)
        try:
            for proc in processes:
                statuses[processes.index(proc)].update(processState(proc))

        except Exception as e:
            console.log(e)
            for status in statuses: status.update('Empty status')