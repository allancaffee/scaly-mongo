from optparse import OptionParser

from scalymongo.connection import Connection


def parse_arguments():
    """Parse and validate the arguments.

    This returns a tuple like ``(options, module_name, endpoint)``.

    """
    parser = OptionParser()
    parser.usage = '%prog MODULE ENDPOINT'

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
    ensure_indexes(connection)


def ensure_indexes(connection):
    for model in connection.models:
        model.ensure_indexes(background=True)


if __name__ == '__main__': # pragma: no cover
    main()
