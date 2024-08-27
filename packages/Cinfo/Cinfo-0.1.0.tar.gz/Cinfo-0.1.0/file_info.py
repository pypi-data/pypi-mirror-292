import click
import os
import tabulate

def info(filename):
    data = []
    headers = ["Byte", "KB", "MB"]
    byte = os.path.getsize(filename)
    kbyte = (byte / 1024)
    mbyte = (byte / 1048576)
    data.append([byte, kbyte, mbyte])
    
    click.echo(tabulate.tabulate(data, headers=headers, tablefmt='grid'))