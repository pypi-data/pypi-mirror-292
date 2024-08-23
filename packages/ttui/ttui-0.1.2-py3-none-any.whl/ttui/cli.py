from ttui.app import MyApp
import click


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option("-d", "--dict", is_flag=True, help="parse dict type.")
@click.option("-t", "--tuple", is_flag=True, help="parse tuple type.")
@click.option ("-l", "--list", is_flag=True, help="parse list type.")
def run(filename, dict: bool, tuple: bool, list: bool):
    """Print FILENAME if the file exists."""
    parse_type = ""
    types = [dict, tuple, list]

    true_flags = [elem for elem in types if elem]

    if len(true_flags) > 1:
        click.echo("Selected too many flags. Please pick only one type to parse for a line in .txt file.")
        return

    if dict:
        parse_type = "dict"

    if tuple:
        parse_type = "tuple"

    if list:
        parse_type = "list"

    with open(click.format_filename(filename), "r") as f:
        if not len(f.readlines()) > 0:
            click.echo("Your file is too small.")
            return
    try:
        app = MyApp(click.format_filename(filename), parse_type)
    except Exception as e:
        raise Exception(e)
    else:
        app.run()

if __name__ == "__main__":
    run()