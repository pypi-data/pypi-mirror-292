import click

#find empty-line and print numbers of lines
def find_empty_lines(filename):
    try:
        empty_line = 0
        with open (filename, mode='r') as rf:
            for line in rf:
                strip_line = line.strip()
                if not strip_line:
                    empty_line += 1
                    
    except FileNotFoundError:
        click.echo("can't open file or invalid file name or path")
        
    else:
        click.echo(f"Count of empty lines: {empty_line}")