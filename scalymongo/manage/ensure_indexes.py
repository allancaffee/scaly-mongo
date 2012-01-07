from optparse import OptionParser

from scalymongo.connection import Connection


def parse_arguments():
    """Parse and validate the arguments.

    This returns a tuple like ``(options, module_name, endpoint)``.

    """
    parser = OptionParser()
    parser.usage = '%prog [options] MODULE ENDPOINT'
    parser.add_option(
        '--background', action='store_true',
        help='create indexes as a non-blocking operation [default]',
    )
    parser.add_option(
        '--no-background', action='store_false', dest='background',
        help='disable background index creation',
    )
    parser.set_defaults(background=True)

    options, arguments = parser.parse_args()

    if len(arguments) != 2:
        parser.print_help()
        exit(1)

    module_name, endpoint = arguments
    return options, module_name, endpoint


def main():
    options, module_name, endpoint = parse_arguments()

    # Import the models so that they get registered with Connection.
    __import__(module_name)

    connection = Connection(endpoint)
    ensure_indexes(connection, options)


def ensure_indexes(connection, options):
    for model in connection.models:
        model.ensure_indexes(background=options.background)


if __name__ == '__main__':  # pragma: no cover
    main()
