import click

#numbers of all lines in file
def all_line(filename):
    try:
        all_line = 0
        with open (filename, mode='r') as rf:
            for line in rf:
                all_line += 1
                    
    except FileNotFoundError:
        click.echo("can't open file or invalid file name or path")
        
    else:
        click.echo(f"Count of all lines: {all_line}")

