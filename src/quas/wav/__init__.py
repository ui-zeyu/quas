import click

from quas.wav.frequency import frequency


@click.group(help="Audio waveform analysis tools")
def app() -> None: ...


app.add_command(frequency)
