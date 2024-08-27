import click

#find all code lines and print number of lines
def find_code_lines(filename):
    try:
        code_line = 0
        with open(filename, mode='r') as rf:
            for line in rf:
                strip_line = line.strip()
                if strip_line and not strip_line.startswith('#'):
                    code_line += 1
                
    except FileNotFoundError:
        click.echo("can't open file or invalid file name or path")
        
    else:
        click.echo(f"Count of code lines: {code_line}")