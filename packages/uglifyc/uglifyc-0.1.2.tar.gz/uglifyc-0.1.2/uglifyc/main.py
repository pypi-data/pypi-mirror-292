import click

def get_max_width(file):
    max_width = 0
    with open(file, "r") as f:
        for i in f.readlines():
            if len(i) > max_width:
                max_width = len(i)

    return max_width

def get_first_normal_char_from_right(s, char_list, space_number):
    for index in range(len(s) - 1, -1, -1):
        if s[index] not in char_list:
            return s[:index+1 ] + ' '*space_number + s[index+1:]
    return s

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file for the uglified Python code.')
def uglify(input, output):
    """
    Uglifies a C file.
    """
    # Set the output file name
    if output is None:
        output = input.replace('.c', '_uglified.c')

    char_list = ["}", ";", ")", "\n", " ", "{"]

    max_width = get_max_width(input)

    uglified_code = ""

    with open(input, "r") as f:
        for line in f.readlines():
            space_number = max_width - len(line)

            uglified_code += get_first_normal_char_from_right(line, char_list, space_number+10)

    with open(output, 'w') as outfile:
        outfile.write(uglified_code)

    click.echo(f"Uglified code written to {output}")

if __name__ == '__main__':
    uglify()