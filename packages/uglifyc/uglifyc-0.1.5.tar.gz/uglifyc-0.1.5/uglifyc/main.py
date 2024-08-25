import click
import os

def get_max_width(file):
    max_width = 0
    with open(file, "r") as f:
        for line in f:
            if len(line) > max_width:
                max_width = len(line)
    return max_width

def get_first_normal_char_from_right(s, char_list, space_number):
    for index in range(len(s) - 1, -1, -1):
        if s[index] not in char_list:
            return s[:index+1] + ' '*space_number + s[index+1:]
    return s

@click.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1)
@click.option('-o', '--output', type=click.Path(), help='Output file for the uglified code. (Only used if --overwrite is not set)')
@click.option('--overwrite', is_flag=True, help='Overwrite the input files with the uglified code.')
def uglify(input_files, output, overwrite):
    """
    Uglifies one or more C files.
    """
    if not input_files:
        click.echo("No input files provided.")
        return

    char_list = ["}", ";", ")", "\n", " ", "{"]

    for input_file in input_files:
        # Determine the output file name
        if overwrite:
            output_file = input_file
        elif output:
            output_file = output
        else:
            output_file = input_file.replace('.c', '_uglified.c')
        
        # Ensure that if overwriting, we don't accidentally overwrite multiple files to the same name
        if overwrite and len(input_files) > 1:
            click.echo("Error: '--overwrite' cannot be used with multiple input files without specifying an output file.")
            return
        
        max_width = get_max_width(input_file)

        uglified_code = ""

        with open(input_file, "r") as f:
            for line in f:
                space_number = max_width - len(line)
                uglified_code += get_first_normal_char_from_right(line, char_list, space_number + 10)

        with open(output_file, 'w') as outfile:
            outfile.write(uglified_code)

        click.echo(f"Uglified code written to {output_file}")

if __name__ == '__main__':
    uglify()
