import argparse
import datetime
import threading
import os, time
from rich.console import Console
from rich.rule import Rule
from rich.live import Live
from rich.status import Spinner
from humanize import naturalsize

console = Console()

def richtail_header() -> None:
    os.system('clear && printf "\\e[3J"\n')
    f.seek(0)
    console.print(Rule('📁 Rich file monitoring tool'))
    
def richtail_footer() -> None:
    fname = os.path.basename(args.filepath)
    t_start = datetime.datetime.now()
    footer = Rule(f'Tailing since {str(datetime.datetime.now()-t_start)[:-4]} | currently {os.stat(args.filepath).st_size} bytes displayed')
    with Live(footer, console = console, refresh_per_second=20) as live_footer:
        while True:
            time.sleep(.1)
            live_footer.update(Rule(f'Tailing since {str(datetime.datetime.now()-t_start)[:-4]} | currently {os.stat(args.filepath).st_size} bytes displayed'))
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
                richtail_header()
            else:
                time.sleep(.1)                
    except KeyboardInterrupt:
        # console.print(f'Trailing interrupted, killing current process to exit', style = 'bold red')
        os.system('kill %d' % os.getpid())
                                   