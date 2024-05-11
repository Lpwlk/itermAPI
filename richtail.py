import argparse
import threading
import os, time
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from humanize import naturalsize

console = Console()

def richtail_header() -> None:
    os.system('clear && printf "\\e[3J"\n')
    f.seek(0)
    console.rule('📁 Rich file monitoring tool', style = 'green')
    
def richtail_footer() -> None:
    fname = os.path.basename(args.filepath)
    footer = Progress(
        SpinnerColumn(speed = 3/2), 
        TimeElapsedColumn(), 
        TextColumn('{task.description}'), 
        BarColumn(pulse_style='#94CA64'), 
        console = console
    )
    with Live(footer, console = console, refresh_per_second=10):
        footer_task = footer.add_task('', total = None)
        while True:
            time.sleep(.1)
            footer.update(footer_task, description = f'Trailing [green]{fname}[/green] | File size - {naturalsize(os.stat(args.filepath).st_size)}')
            
parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = '''│ Monitoring tool for file content tracking with rich package implementation.
| Similar behaviour as tail -f but with dynamic display of file content (data deletion isn't displayed in term window.)''',
    epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')

parser.add_argument('-f', '--filepath', default = '', type = str, metavar = '', action= 'store', help = 'File path to be monitored')
args = parser.parse_args()
for arg in vars(args): console.print(arg, '\t─\t', getattr(args, arg))

footer_thread = threading.Thread(target = richtail_footer)
footer_thread.start()

with open(args.filepath, 'r') as f:
    try:
        richtail_header()
        while True:
            line = f.readline()
            if line:
                console.print(f'{line.strip()}') 
            elif os.stat(args.filepath).st_size == 0:
                time.sleep(.2)
                richtail_header()
            else:
                time.sleep(.2)                
    except KeyboardInterrupt:
        console.print(f'Trailing interrupted, killing current process to exit', style = 'bold red')
        os.system(f'kill {os.getpid()}')