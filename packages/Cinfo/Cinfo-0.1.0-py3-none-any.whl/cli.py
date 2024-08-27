import click
from code_lines import find_code_lines
from all_lines import all_line
from empty_lines import find_empty_lines
from comment_lines import find_comment_line
import file_info

@click.command()
@click.option('--all', help="Count all lines in your file", is_flag=True)
@click.option('--empty-line', help="Count number of empty lines in your file", is_flag=True)
@click.option('--comment', help="Count number of written comment in your file", is_flag=True)
@click.option('--code', help="Count number of written code in your file", is_flag=True)
@click.option('--info', help="show all data about file", is_flag=True)

@click.argument('filename')

def readFile(code, all, empty_line, comment, info, filename):
    if code:
        find_code_lines(filename)
        
    elif all:
        all_line(filename)
        
    elif empty_line:
        find_empty_lines(filename)
        
    elif comment:
        find_comment_line(filename)
        
    elif info:
        file_info.info(filename)