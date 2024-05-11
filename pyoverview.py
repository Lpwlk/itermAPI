import os
import time

import psutil
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install
from humanize import naturalsize
install(width = 120, show_locals=True)

def processState(
    proc: psutil.Process, 
    pid: bool = True, 
    cpu: bool = True, 
    mem: bool = True
    ) -> str | None:
    try:
        state = get_pfile(proc)
        if pid: state += f' | pid: {str(proc.pid).ljust(5, ' ')}'
        if cpu: state += f' | CPU - 50ms:{fmtCPUload(proc, inter=.05)}% | 10ms:{fmtCPUload(proc, inter=.01)}'
        if mem: state += f' | Memory - rss: {naturalsize(proc.memory_info().rss)} vms: {naturalsize(proc.memory_info().rss)}'
        return state
    except KeyboardInterrupt:
        console.log(f'Trailing interrupted, killing current process to exit', style = 'bold red')
        os.system(f'kill {os.getpid()}')
    except:
        # console.log('State formatting exception')
        return None

def get_pfile(process: psutil.Process) -> str:
    format_proc_file = f'{process.cmdline()[1].split('/')[-1].ljust(15, ' ')}'
    return format_proc_file

def fmtCPUload(process: psutil.Process, inter: int,  bycores = 0):
    jlenght = 4
    if not bycores: jlenght += 1
    return str(process.cpu_percent(interval = inter)/(1+bycores*(n_cores-1)))[:5].rjust(jlenght, ' ')

def scan_python_process() -> list[psutil.Process]:
    try:
        scan = psutil.process_iter()
        filtered_scan = [p for p in scan if p.name() == 'Python']
        return filtered_scan
    except KeyboardInterrupt:
        os.system('clear && printf "\\e[3J"\n')
        console.log(f'Trailing interrupted, killing current process to exit', style = 'bold red')
        os.system(f'kill {os.getpid()}')
    except:
        # console.log('Process scan exception')
        return None

def manage_tasks(processes: list[psutil.Process], progress: Progress) -> None:
    try:
        states = [processState(p) for p in processes]
        for task in progress.tasks:
            progress.remove_task(task.id)
        for state in states:
            progress.add_task(state, total = None)
    except:
        pass
    
###########################

console = Console(highlight=True)
progress = Progress(SpinnerColumn(), TextColumn('{task.description}'), console = console)
os.system('clear && printf "\\e[3J"\n')
n_cores = psutil.cpu_count()
current_pid = os.getpid()

def dynamic_display() -> None:
    with Live(progress, refresh_per_second=10, console = console):
        console.rule(f'[green]Dynamic tracking of every active python processes')
        while True:
            time.sleep(.05)
            manage_tasks(scan_python_process(), progress)

dynamic_display()