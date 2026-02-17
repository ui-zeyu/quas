import click

from quas.wav.frequency import frequency


@click.group()
def app() -> None: ...


app.add_command(frequency)
