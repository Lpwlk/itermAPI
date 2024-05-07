import iterm2
import psutil, os, time
import argparse
from rich import inspect
from rich.console import Console, Group
from rich.rule import Rule
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.status import Status
from rich.live import Live

console = Console(
    highlight = 1,
    log_time = 1,
)

progress = Progress(
    TextColumn("{task.description}"),
    # BarColumn(style = 'cornflower_blue', complete_style = 'white', pulse_style = 'white'), 
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    console = console,
)
status = Status(
    status = 'Empty status',
    console = console,
) 
status_style = 'italic green'
status_logstyle = 'italic'
iteration_style = 'bright_yelow'
status.update(f'[{status_style}]Parsing autoexec arguments ...')

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = '''
│ Debugging tool for multi-process autoexec based
| on the Iterm2 (MacOS) Python3 API
''',
    epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')
parser.add_argument('-t', '--timeout', default = 3, metavar = '\b', type = int, action= 'store', help = 'File path to be monitored')
parser.add_argument('-s', '--timescale', default = 4, metavar = '\b', type = float, action= 'store', help = 'Time scale for API sequence execution')
parser.add_argument('-c', '--clearcontent', action= 'store_true', help = 'Clearing pane(s) after timeout [-t timeout]')
parser.add_argument('-d', '--delpanes', action= 'store_true', help = 'Panes deletion after timeout [-t timeout]')
parser.add_argument('-a', '--argsdisplay', action= 'store_false', help = 'Arguments display flag')
args = parser.parse_args()

if args.argsdisplay:
    os.system('clear && printf "\e[3J"')
    console.print('Arguments')
    for arg in vars(args): 
        console.print(arg, '\t─\t', getattr(args, arg))
    console.print('')

def sleep(delay) -> None:
    time.sleep(delay*args.timescale)
    
def check_ext_term() -> bool:
    os.system("echo $TERM_PROGRAM >> term"); 
    with open("term", 'r') as f: term = f.read().strip()
    os.system('rm term')
    if term == 'vscode': return True
    else: return False
    
extTerm = check_ext_term()

async def main(connection):
    
    with Live(Group(status, progress), refresh_per_second=20, console=console):
        
        maintask_id = progress.add_task('Iterm2 API call sequence', total = None)
        
        status.update(f'[{status_style}]Killing active python processes ...')
        killed_processes = 0
        for proc in psutil.process_iter():
            if proc.name() == 'Python' and proc.pid != os.getpid():
                console.log(f'Process killed (pid={proc.pid})')
                sleep(.1)
                killed_processes += 1
                proc.kill()

        if not killed_processes:
            console.log(f'[{status_logstyle}]No active python process to kill for autoexec sequence')
            sleep(.5)
        else: 
            console.log(f'[{status_logstyle}]Killed {killed_processes} python processes for autoexec sequence init')
        
        status.update(f'[{status_style}]Fetching iterm2.app connection ...')
        sleep(.5)
        app = await iterm2.async_get_app(connection)
        if app.current_terminal_window is not None:
            window = app.current_terminal_window
            console.log(f'[{status_logstyle}]Iterm2 connection succesfully acquired')
            
            status.update(f'[{status_style}]Accessing target exec session ...')
            sleep(.5)
            tab = window.current_tab
            exec_session = tab.current_session
            console.log(f'[{status_logstyle}]Accessed exec session into acquired window for grid creation')
            
            status.update(f'[{status_style}]Creating sessions grid for commands exec ...')
            for session in tab.sessions:
                if session != exec_session:
                    await session.async_send_text('\x03\n')
                    await session.async_close()
            top_left_pan = await exec_session.async_split_pane(vertical=False)
            console.log(f'Created top left session → {top_left_pan}', style = 'yellow'); sleep(.1)
            top_right_pan = await top_left_pan.async_split_pane(vertical=True)
            console.log(f'Created top right session → {top_right_pan}', style = 'yellow'); sleep(.1)
            btm_left_pan = await top_left_pan.async_split_pane(vertical=False)
            console.log(f'Created btm left session → {btm_left_pan}', style = 'yellow'); sleep(.1)
            btm_right_pan = await top_right_pan.async_split_pane(vertical=False)
            console.log(f'Created btm right session → {btm_right_pan}', style = 'yellow'); sleep(.1)
            console.log(f'[{status_logstyle}]Created 2x2 grid for each exec commands')
            
            status.update(f'[{status_style}]Handling debug session depending on terminal ...')
            # cdp can be replaced with custom cd command for specific files access
            cmd_top_left = 'cdp; cl; py server.py\n'
            cmd_top_right = 'cdp; cl; py client.py\n'
            cmd_btm_right = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'
            cmd_btm_left = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Server/DataBase/Logs/log_server.log\n'
            
            await top_left_pan.async_send_text (cmd_top_left)
            console.log(f'Sent cmd_top_left  → {cmd_top_left[:-1]}', style = 'yellow'); sleep(.1)
            await top_right_pan.async_send_text(cmd_top_right)
            console.log(f'Sent cmd_top_right → {cmd_top_right[:-1]}', style = 'yellow'); sleep(.1)
            await btm_left_pan.async_send_text (cmd_btm_left)
            console.log(f'Sent cmd_btm_left  → {cmd_btm_left[:-1]}', style = 'yellow'); sleep(.1)
            await btm_right_pan.async_send_text(cmd_btm_right)
            console.log(f'Sent cmd_btm_right → {cmd_btm_right[:-1]}', style = 'yellow'); sleep(.1)
            
            status.update(f'[{status_style}]Handling exec session depending on terminal ...')
            sleep(.1)
            if extTerm:
                console.log(f'[{status_logstyle}]Running from vscode, closing initial target session → full window autoexec')
                await exec_session.async_send_text('clear\n')
                await exec_session.async_close()
            else:
                console.log(f'[{status_logstyle}]Running from iterm2 window →  holding current exec session')
                        
            if args.timeout != 0:
                
                status.update(f'[{status_style}]Starting {args.timeout} sec timeout for command executions ...')
                timeout_id = progress.add_task('Timeout before interrupts', total = args.timeout); res = 100
                progress.update(maintask_id, visible = False)
                
                try:
                    while not progress.tasks[timeout_id].finished:
                        time.sleep(args.timeout/res)
                        progress.update(timeout_id, advance = args.timeout/res)
                    console.print(f'Timeout reached : {args.timeout} elapsed', style = 'green', highlight = False)
                except KeyboardInterrupt:
                    console.print('Timeout interrupted by user', style = 'red')
                    progress.remove_task(timeout_id)
                progress.update(maintask_id, visible = True)
                
                for session in tab.sessions:
                    if session != exec_session:
                        await session.async_send_text('\x03\n')
                        if session != btm_right_pan:
                            if args.delpanes: await session.async_close()
                        else:
                            if args.clearcontent: await session.async_send_text('clear\n')
            else: 
                status.update(f'[{status_style}]Timeout set to 0 : commands running indefinitely without local interrupt availability')
                # progress.update(maintask_id, visible = False)
        else:
            console.log(f'[{status_logstyle+' red]'}[underline]Warning:[/underline] Failed to acces iterm2 window connection : manual open required')

iterm2.run_until_complete(main)
