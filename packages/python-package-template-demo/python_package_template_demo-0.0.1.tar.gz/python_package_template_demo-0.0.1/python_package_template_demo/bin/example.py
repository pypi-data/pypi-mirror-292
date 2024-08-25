import click


@click.command()
@click.argument('some-argument', type=str, required=True)
@click.option('-o', '--some-option', help="Option description.")
def main(some_argument, some_option):
    print(f'Hello, World! (User says: "{some_argument}")')

if __name__ == '__main__':
    main()