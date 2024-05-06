import iterm2
import iterm2.util
import psutil, os, time
import argparse
from rich import inspect
from rich.console import Console

def get_term():
    os.system("echo $TERM_PROGRAM >> term")
    with open("term", 'r') as f:
        term = f.read().strip()
    os.system('rm term')
    return term

if get_term() == 'vscode':
    extTerm = True 
else:
    extTerm = False 

console = Console()

log_style = ''
status_style = 'bright_blue'
cmd_style = 'italic'
parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = '''│ Debugging tool for multi-process autoexec based
| on the Iterm2 (MacOS) Python3 API''',
    epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')

parser.add_argument('-t', '--timeout', default = 3, type = int, action= 'store', help = 'File path to be monitored')
parser.add_argument('-c', '--clearcontent', action= 'store_true', help = 'Clearing pane(s) after timeout [-t timeout]')
parser.add_argument('-d', '--delpanes', action= 'store_true', help = 'Panes deletion after timeout [-t timeout]')
parser.add_argument('-s', '--timescale', default = 1, type = int, action= 'store', help = 'Time scale for API sequence execution')
args = parser.parse_args()
for arg in vars(args): console.print(arg, '\t─\t', getattr(args, arg))

console.print('Aborting every ongoing python processes except current one before API call sequence ...', style = log_style)
for proc in psutil.process_iter():
    if proc.name() == 'Python' and proc.pid != os.getpid():
        proc.kill()

async def main(connection):
    with console.status('[green]Iterm2 API call sequence started[/green]', speed = 2) as status:
        
        app = await iterm2.async_get_app(connection)
        window = app.current_terminal_window
        
        if window is not None:    
            console.log('Pointing to current active iterm2 session', style = log_style)
            time.sleep(.5 * args.timescale)
            tab = window.current_tab
            debug_session = tab.current_session
            time.sleep(.5 * args.timescale)
            console.log('Closing every inactive sessions', style = log_style)
            for session in tab.sessions:
                if session != debug_session:
                    await session.async_send_text('\x03\n')
                    await session.async_close()
                    
            top_left_pan = await debug_session.async_split_pane(vertical=False)
            top_right_pan = await top_left_pan.async_split_pane(vertical=True)
            btm_right_pan = await top_right_pan.async_split_pane(vertical=False)
            btm_left_pan = await top_left_pan.async_split_pane(vertical=False)
            console.log('Created 2x2 pane grid', style = log_style)
            time.sleep(0.5 * args.timescale)

            cmd_top_left = 'cdp; cl; py server.py\n'
            cmd_top_right = 'cdp; cl; py client.py\n'
            cmd_btm_right = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Client/DataBase/Logs/log_client_1.log\n'
            cmd_btm_left = 'cdp; py /Users/loicpwlk/Documents/Code/itermAPI/richtail.py -f richsockets/Server/DataBase/Logs/log_server.log\n'
            
            console.log(f'cmd_top_left  → {cmd_top_left[:-1]}', style = cmd_style); time.sleep(.2 * args.timescale)
            console.log(f'cmd_btm_left  → {cmd_btm_left[:-1]}', style = cmd_style); time.sleep(.2 * args.timescale)
            console.log(f'cmd_top_right → {cmd_top_right[:-1]}', style = cmd_style); time.sleep(.2 * args.timescale)
            console.log(f'cmd_btm_right → {cmd_btm_right[:-1]}', style = cmd_style); time.sleep(.2 * args.timescale)
            await top_left_pan.async_send_text(cmd_top_left)
            await top_right_pan.async_send_text(cmd_top_right)
            await btm_left_pan.async_send_text(cmd_btm_left)
            await btm_right_pan.async_send_text(cmd_btm_right)
            if extTerm:
                console.log('Clearing debug session', style = log_style)
                await debug_session.async_send_text('cl\n')
                await debug_session.async_close()
                        
            if args.timeout != 0:
                status.update(f'[green]Starting {args.timeout}sec timeout for command executions ...[/green]')
                t_start = time.time(); delay = time.time()-t_start
                while delay < args.timeout: 
                    time.sleep(.1)
                    delay = time.time()-t_start
                console.print(f'Timeout reached : {args.timeout} elapsed', style = 'green', highlight = False)

                for session in tab.sessions:
                    if session != debug_session:
                        await session.async_send_text('\x03\n')
                        if session != btm_right_pan:
                            if args.delpanes: await session.async_close()
                        else:
                            console.log(f'Timeout reached : {args.timeout} elapsed', style = 'green', highlight = False)
                            if args.clearcontent: await session.async_send_text('cl\n')
            else: 
                status.update(f'[green]Timeout set to 0 : commands running indefinitely[/green]')
        else:
            console.log('Manual Iterm2 window launch required', style = 'italic red')
            
iterm2.run_until_complete(main)
