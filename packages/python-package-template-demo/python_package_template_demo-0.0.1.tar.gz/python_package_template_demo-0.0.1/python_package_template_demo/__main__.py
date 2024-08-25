import click

from .bin import example


@click.group()
def main():
    pass

main.add_command(example.main, name="example")

if __name__ == "__main__":
    main()