import os
import time

import psutil
from rich import inspect
from rich.console import Console
from rich.live import Live
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install  
install(width = 120, show_locals=True)

def processState(proc: psutil.Process):
    return f'{proc.cmdline()[1].split('/')[-1].ljust(16, ' ')} | pid: {proc.pid} | cpu usage - 100ms:{fmtCPUload(proc, inter=.1)}% | 10ms:{fmtCPUload(proc, inter=.01)} | 1ms:{fmtCPUload(proc, inter=.001)}%'

def fmtCPUload(process: psutil.Process, inter: int,  bycores = 0):
    jlenght = 4
    if not bycores: jlenght += 1
    return str(process.cpu_percent(interval = inter)/(1+bycores*(n_cores-1)))[:5].rjust(jlenght, ' ')

def scan_python_process() -> list[psutil.Process]:
    processes = []
    for proc in psutil.process_iter():
        if proc.name() == 'Python' and proc not in processes:
            processes.append(proc)
    return processes

def get_proc_file(proc: psutil.Process) -> str:
    return proc.cmdline()[1].split('/')[-1].ljust(16, ' ')

def manage_tasks(processes: list[psutil.Process], progress: Progress) -> None:
    for proc in processes:
        if get_proc_file(proc) in [task.description[:16] for task in progress.tasks]:
            for task in progress.tasks:
                if task.description[:16] == get_proc_file(proc):
                    progress.update(task.id, description=processState(proc))
        elif [get_proc_file(p) for p in processes].count(get_proc_file(proc)) > 1:
            console.log('test')
            progress.add_task(processState(proc), total = None)
        else:
            progress.add_task(processState(proc), total = None)
        for task in progress.tasks:
            try:
                if task.description[:16] not in [get_proc_file(proc) for proc in processes]:
                    progress.remove_task(task.id)
            except: 
                progress.remove_task(task.id)
    return None

###########################

os.system('clear && printf "\\e[3J"\n')

n_cores = psutil.cpu_count()
current_pid = os.getpid()

console = Console(
    highlight=True,
)

progress = Progress(
    SpinnerColumn(), 
    TextColumn('{task.description}'), 
    console = console
)

def dynamic_display() -> None:
    with Live(progress, refresh_per_second=12):
        console.log(f'[green]Dynamic tracking of every active python processes')
        while True:
            manage_tasks(scan_python_process(), progress)
            time.sleep(1)


dynamic_display()