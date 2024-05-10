from rich.console import Console, Group
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.status import Status
from rich.live import Live
from rich.rule import Rule
from rich import inspect

# inspect(Console(), methods = 1)
# inspect(Group(), methods = 1)
# inspect(Rule(), methods = 1)

progress = Progress()
task = progress.add_task('')
inspect(progress, methods = 1)
inspect(progress.tasks, methods = 1)

# inspect(SpinnerColumn()(), methods = 1)
# inspect(TextColumn(), methods = 1)
# inspect(BarColumn(), methods = 1)
# inspect(TaskProgressColumn(), methods = 1)
# inspect(TimeRemainingColumn(), methods = 1)

# inspect(Status(), methods = 1)
# inspect(Live(), methods = 1)
