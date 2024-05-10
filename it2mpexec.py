import iterm2
import psutil, os, time
import argparse
from rich.console import Console, Group
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.status import Status
from rich.live import Live
from rich.rule import Rule
from rich import inspect

clear_cmd = 'clear && printf "\\e[3J"\n'
iteration_style = 'bright_yelow'

console = Console(
    highlight = 1,
    log_time = 1,
)

progress = Progress(
    SpinnerColumn(),
    TextColumn('{task.description}'),
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

def sleep(delay) -> None:
    time.sleep(delay*args.timescale)

def switch_scope(
        outlogmsg: str = 'Scope output log text',
        newstatus: str = 'Scope input status text',
        console: Console = console,
        status: Status = status,
        error_status: bool = False,
        delay: float = 1,
        ) -> None:
    console.log(f'[italic]{outlogmsg}')
    if not error_status: 
        newstatus = f'[italic green]{newstatus}'
    else: 
        newstatus = f'[red]{newstatus}'
        status.spinner_style = 'red'
    status.update(newstatus)
    console.log(newstatus)
    sleep(delay)

def check_ext_term() -> bool:
    os.system('echo $TERM_PROGRAM >> term'); 
    with open('term', 'r') as f: term = f.read().strip()
    os.system('rm term')
    if term == 'vscode': return True
    else: return False

########################## 

os.system(clear_cmd)
console.print('\n'*32)

parser = argparse.ArgumentParser(
    description = '''│ Debugging tool for multi-process autoexec based\n| on the Iterm2 (MacOS) Python3 API''',
    formatter_class = argparse.RawDescriptionHelpFormatter,
    epilog = 'Author : Pawlicki Loïc\n' + '─'*22 + '\n',
)
parser.add_argument('-t', '--timeout', default = 5, metavar = '\b', type = int, action= 'store', help = 'Timeout for processes auto-interruption')
parser.add_argument('-s', '--timescale', default = .1, metavar = '\b', type = float, action= 'store', help = 'Time scale for sequence execution')
parser.add_argument('-c', '--clcontent', action= 'store_true', help = 'Clearing sessions after sequence execution')
parser.add_argument('-d', '--delpanes', action= 'store_true', help = 'Deleting sessions after sequence execution ([-c] override)')
parser.add_argument('-a', '--argsdisplay', action= 'store_false', help = 'Arguments display flag')
args = parser.parse_args()

if args.argsdisplay:
    console.print(Rule('[green]Parsing autoexec arguments ...'))
    for arg in vars(args): console.print(arg, '\t─\t', getattr(args, arg))
console.print('')

async def main(connection):
    
    with Live(
            Group(status, progress), 
            refresh_per_second=20, 
            console = console, 
            transient = True,
        ) as live:
        
        maintask_id = progress.add_task('Iterm2 API call sequence', total = None)
        
        # inspect(live, methods = 1, help = 1)
        # inspect(progress.tasks[maintask_id], methods = 1, help = 1)

        switch_scope(
            outlogmsg='Iterm2 API calls sequence started',
            newstatus='Killing active python processes ...',
            delay = .5
        )
        
        killed_processes = 0
        for proc in psutil.process_iter():
            if proc.name() == 'Python' and proc.pid != os.getpid():
                if proc.cmdline()[1] != 'pyoverview.py':
                    console.log(f'Process [yellow]{os.path.basename(proc.cmdline()[1])}[/yellow] killed using pid: {proc.pid} | cpu usage: {str(proc.cpu_percent(interval = .1)).ljust(5, ' ')}')
                    killed_processes += 1
                    proc.kill()
                    
        if not killed_processes: 
            logmsg = 'No active python process to kill for autoexec sequence'
            sleep(1)
        else: 
            logmsg = f'Killed {killed_processes} python processes for autoexec sequence init'
        switch_scope(
            outlogmsg=logmsg,
            newstatus='Fetching iterm2.app connection ...',
            delay = 1,
        )
        
        app = await iterm2.async_get_app(connection)
        if app.current_terminal_window is not None:
            window = app.current_terminal_window
            
            switch_scope(
                outlogmsg='Iterm2 connection succesfully acquired',
                newstatus='Accessing control session ...',
                delay = 1,
            )
            
            tab = window.current_tab
            control_session = tab.current_session
            
            switch_scope(
                outlogmsg='Accessed control session into acquired window for grid creation',
                newstatus='Creating sessions grid for commands execution ...',
                delay = 1,
            )
            
            for session in tab.sessions:
                if session != control_session:
                    await session.async_send_text('\x03\n')
                    await session.async_close()

            top_left_pan = await control_session.async_split_pane(vertical=False)
            console.log(f'Created top left session  → {top_left_pan}', style = 'yellow'); sleep(.1)
            top_right_pan = await top_left_pan.async_split_pane(vertical=True)
            console.log(f'Created top right session → {top_right_pan}', style = 'yellow'); sleep(.1)
            btm_left_pan = await top_left_pan.async_split_pane(vertical=False)
            console.log(f'Created btm left session  → {btm_left_pan}', style = 'yellow'); sleep(.1)
            btm_right_pan = await top_right_pan.async_split_pane(vertical=False)
            console.log(f'Created btm right session → {btm_right_pan}', style = 'yellow'); sleep(.1)
            
            switch_scope(
                outlogmsg = 'Created 2x2 grid for each exec commands',
                newstatus = 'Managing control session depending on terminal ...',
                delay = 1
            )
            
            if 0: # toggle to enable 2x4 grid
                top_left_pan2 = await control_session.async_split_pane(vertical=False)
                console.log(f'Created top left session 2  → {top_left_pan2}', style = 'yellow'); sleep(.1)
                top_right_pan2 = await top_left_pan2.async_split_pane(vertical=True)
                console.log(f'Created top right session 2 → {top_right_pan2}', style = 'yellow'); sleep(.1)
                btm_left_pan2 = await top_left_pan2.async_split_pane(vertical=False)
                console.log(f'Created btm left session 2  → {btm_left_pan2}', style = 'yellow'); sleep(.1)
                btm_right_pan2 = await top_right_pan2.async_split_pane(vertical=False)
                console.log(f'Created btm right session 2 → {btm_right_pan2}', style = 'yellow'); sleep(.1)
                
                cmd_top_left2 = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'
                cmd_top_right2 = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'
                cmd_btm_left2 = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Server/DataBase/Logs/log_server.log\n'
                cmd_btm_right2 = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'

                await top_left_pan2.async_send_text (cmd_top_left2)
                console.log(f'Sent cmd_top_left2  → {cmd_top_left2[:-1]}', style = 'yellow'); sleep(.2)
                await top_right_pan2.async_send_text(cmd_top_right2)
                console.log(f'Sent cmd_top_right2 → {cmd_top_right2[:-1]}', style = 'yellow'); sleep(.2)
                await btm_left_pan2.async_send_text (cmd_btm_left2)
                console.log(f'Sent cmd_btm_left2  → {cmd_btm_left2[:-1]}', style = 'yellow'); sleep(.2)
                await btm_right_pan2.async_send_text(cmd_btm_right2)
                console.log(f'Sent cmd_btm_right2 → {cmd_btm_right2[:-1]}', style = 'yellow'); sleep(.2)
            
            if check_ext_term():
                await control_session.async_send_text(clear_cmd)
                await control_session.async_close()
                # await control_session.async_send_text(f'{clear_cmd}cdi; py pyoverview.py\n')
                logmsg = 'Running from vscode, control session closed → full window autoexec'
            else:
                logmsg = 'Running from iterm2 window →  holding current exec session'
            
            switch_scope(
                outlogmsg = logmsg,
                newstatus = 'Sending commands to sessions ...',
                delay = .5
            )

            cmd_top_left = 'cdp; cl; py server.py\n'
            cmd_top_right = 'cdp; cl; py client.py\n'
            cmd_btm_left = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Server/DataBase/Logs/log_server.log\n'
            cmd_btm_right = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'
            
            await top_left_pan.async_send_text (cmd_top_left)
            console.log(f'Sent cmd_top_left  → {cmd_top_left[:-1]}', style = 'yellow'); sleep(.2)
            await top_right_pan.async_send_text(cmd_top_right)
            console.log(f'Sent cmd_top_right → {cmd_top_right[:-1]}', style = 'yellow'); sleep(.2)
            await btm_left_pan.async_send_text (cmd_btm_left)
            console.log(f'Sent cmd_btm_left  → {cmd_btm_left[:-1]}', style = 'yellow'); sleep(.2)
            await btm_right_pan.async_send_text(cmd_btm_right)
            console.log(f'Sent cmd_btm_right → {cmd_btm_right[:-1]}', style = 'yellow'); sleep(.2)
            
            logmsg = 'Sessions commands executed'
            
            if args.timeout != 0:
                progress.update(maintask_id, description = 'Timeout execution mode')
                switch_scope(
                    outlogmsg = logmsg + f', starting {args.timeout} seconds timeout',
                    newstatus = f'Waiting {args.timeout} seconds before sessions interruption ...',
                    delay = 1
                )
            
                timeout_id = progress.add_task('Timeout before interruption', total = args.timeout)
                progress.update(maintask_id, visible = False)
                try:
                    while not progress.tasks[timeout_id].finished:
                        time.sleep(1/10)
                        progress.update(timeout_id, advance = 1/10)
                    logmsg = f'[green]Timeout reached after {args.timeout} seconds'
                except KeyboardInterrupt:
                    logmsg = f'[red]Timeout interrupted by user after {str(progress.tasks[timeout_id].completed)[:4]} seconds'
                    progress.remove_task(timeout_id)
                progress.update(maintask_id, visible = True)
                switch_scope(
                    outlogmsg = logmsg,
                    newstatus = 'Managing sessions before closing ...',
                    delay = 1
                )
                for session in tab.sessions:
                    if session != control_session:
                        await session.async_send_text('\x03\n')
                        logmsg = ', holding sessions content'
                        if session != top_left_pan:
                            if args.delpanes: 
                                await session.async_close()
                                logmsg = 'with deletion from iterm2 window'
                            else:
                                if args.clcontent: 
                                    await session.async_send_text(clear_cmd)
                                    logmsg = 'with output content deletion'
                    else:
                        if check_ext_term() and args.clcontent: await session.async_send_text(clear_cmd)
                
                progress.update(maintask_id, visible = False)
                switch_scope(
                    outlogmsg = 'Sessions remote interruption ' + logmsg,
                    newstatus = f'Now exiting from iterm2 API calls sequence ...',
                    delay = 1
                )
            
            else: 
                progress.update(maintask_id, description = 'Idle execution mode')
                switch_scope(
                    outlogmsg = logmsg + ' using no timeout',
                    newstatus = f'Timeout set to 0 : sessions now waiting for remote interrupt ...',
                    delay = 1
                )
                
                run_flag = True
                while run_flag:
                    try:
                        sleep(100)
                    except KeyboardInterrupt:
                        run_flag = False
                        
                        switch_scope(
                            outlogmsg = 'Interruption received, exiting idle mode',
                            newstatus = 'Managing sessions after interruption ...',
                            delay = 1
                        )
                        for session in tab.sessions:
                            if session != control_session:
                                await session.async_send_text('\x03\n')
                                logmsg = ', holding sessions content'
                                if session != top_left_pan:
                                    if args.delpanes: 
                                        await session.async_close()
                                        logmsg = 'and removed from iterm2 window'
                                    else:
                                        if args.clcontent: 
                                            await session.async_send_text(clear_cmd)
                                            logmsg = 'and cleared from output content'
                                else:
                                    if check_ext_term() and args.clcontent: await session.async_send_text(clear_cmd)
                                    
                        progress.update(maintask_id, visible = False)
                        switch_scope(
                            outlogmsg = 'Sessions remotely interrupted ' + logmsg,
                            newstatus = f'Now exiting from iterm2 API calls sequence ...',
                            delay = 1
                        )
        
        else:
            progress.update(maintask_id, visible = False)
            switch_scope(
                outlogmsg = '[red][underline]Warning:[/underline] Failed to acces iterm2 window connection : manual open required[/red]',
                newstatus = f'Program exiting because no connection could be acquired ...',
                error_status = True,
                delay = 1
            )

iterm2.run_until_complete(main)
