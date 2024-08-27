import click

# Dictionary of language comment styles
language = {
    'py': ["#", "'''", "'''"],
    'cpp': ['//', '/*', '*/'],
    'js': ['//', '/*', '*/'],
    'html': ['<!--', '-->'],
    'css': ['/*', '*/'],
    'ts': ['//', '/*', '*/'],
    'jsx': ['{/*', '*/}'],
    'cs': ['//', '/*', '*/'],
    'asm': [';', '#', '@'],  
    'sql': ['--', '/*', '*/']
}

# Find all comment lines and print the number of lines
def find_comment_line(filename):
    try:
        comment_line = 0
        format = filename.split('.')[-1]
        
        single_line_comment = language[format][0]
        multiline_comment_start = language[format][1] if len(language[format]) > 1 else None
        multiline_comment_end = language[format][2] if len(language[format]) > 2 else None
        
        in_multiline_comment = False
        
        with open(filename, mode='r') as rf:
            for line in rf:
                strip_line = line.strip()
                
                # Check for single-line comment
                if strip_line.startswith(single_line_comment):
                    comment_line += 1
                
                # Check for start of multi-line comment
                if multiline_comment_start and strip_line.startswith(multiline_comment_start):
                    in_multiline_comment = True
                    comment_line += 1
                
                # Check if within multi-line comment
                elif in_multiline_comment:
                    comment_line += 1
                    if multiline_comment_end and strip_line.endswith(multiline_comment_end):
                        in_multiline_comment = False
                
    except FileNotFoundError:
        click.echo("Can't open file or invalid file name or path")
        
    else:
        click.echo(f"Count of comment lines: {comment_line}")
