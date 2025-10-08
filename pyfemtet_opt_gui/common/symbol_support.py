def convert(name):
    return (
        name
        .replace('.', '__dot__')
        .replace('@', '__at__')
        .replace('-', '__hyphen__')
    )


def revert(name):
    return (
        name
        .replace('__dot__', '.')
        .replace('__at__', '@')
        .replace('__hyphen__', '-')
    )
