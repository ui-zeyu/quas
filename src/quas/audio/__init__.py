import click

from quas.audio.dtmf import dtmf
from quas.audio.frequency import frequency
from quas.audio.lsb import lsb
from quas.audio.morse import morse
from quas.audio.visualize import visualize


@click.group(help="Audio waveform analysis tools")
def app() -> None: ...


app.add_command(dtmf)
app.add_command(frequency)
app.add_command(lsb)
app.add_command(morse)
app.add_command(visualize)
