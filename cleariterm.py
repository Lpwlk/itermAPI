import iterm2
import iterm2.util
import psutil, os

for proc in psutil.process_iter():
    if proc.name() == 'Python' and proc.pid != os.getpid():
        proc.kill()

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window

    if window is not None:
        
        tab = window.current_tab
        clear_session = tab.current_session
        for session in tab.sessions:
            if session != clear_session:
                await session.async_send_text('\x03\n')
                await session.async_close()
        await clear_session.async_send_text('cl\n')
    else:
        print("No current window")

iterm2.run_until_complete(main)
