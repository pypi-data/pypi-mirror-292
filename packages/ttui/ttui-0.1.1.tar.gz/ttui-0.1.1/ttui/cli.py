from ttui.app import MyApp
import click


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def run(filename):
    """Print FILENAME if the file exists."""

    with open(click.format_filename(filename), "r") as f:
        if not len(f.readlines()) > 0:
            click.echo("Your file is too small.")
            return

    try:
        app = MyApp(click.format_filename(filename))
    except Exception as e:
        raise Exception(e)
    else:
        app.run()

if __name__ == "__main__":
    run()