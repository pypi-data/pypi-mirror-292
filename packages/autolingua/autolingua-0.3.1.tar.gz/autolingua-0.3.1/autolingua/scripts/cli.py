import argparse

from autolingua.scripts import codification, replacement


def main():
    parser = argparse.ArgumentParser(
        prog='autolingua', description='Autolingua CLI interface'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Replacement subcommand
    replacement_parser = subparsers.add_parser(
        'replacement',
        description='Automated replacement script',
        help='Run the replacement script',
    )
    replacement_parser.add_argument(
        '-fases_filename',
        default='PRUEBA',
        help='Excel file with fases replacement columns',
    )
    replacement_parser.add_argument(
        '-input_filename',
        default='CA_UNIVERSIDAD_LEXICO_FASE1-2',
        help='Input file to replace words from',
    )
    replacement_parser.add_argument(
        '-extension', default='.xlsx', help='Default Excel files extension'
    )
    replacement_parser.add_argument(
        '-fase2_1_col', default='AB', help='Name of two columns for fase 2.1'
    )
    replacement_parser.add_argument(
        '-fase2_2_col', default='CD', help='Name of two columns for fase 2.2'
    )
    replacement_parser.add_argument(
        '-fase2_3_col', default='EF', help='Name of two columns for fase 2.3'
    )
    replacement_parser.add_argument(
        '-fase3_col', default='GH', help='Name of two columns for fase 3'
    )
    replacement_parser.add_argument(
        '-fase4_col', default='JK', help='Name of two columns for fase 4'
    )
    replacement_parser.add_argument(
        '-input_col', default='D', help='Name of column for input file content'
    )
    replacement_parser.add_argument(
        '-fase2_from_file',
        default='None',
        help='Extract Fase 2 data from file',
    )
    replacement_parser.add_argument(
        '-fase3_from_file',
        default='None',
        help='Extract Fase 3 data from file',
    )
    # Add any specific arguments for the replacement script here
    replacement_parser.set_defaults(func=replacement.main)

    # Codification subcommand
    codification_parser = subparsers.add_parser(
        'codification',
        description='Automated codification script',
        help='Run the codification script',
    )
    codification_parser.add_argument(
        '-color', action='store_true', help='color automated cells'
    )
    codification_parser.add_argument(
        '-file_name',
        default='PRESEEA_1995_Nivel_bajo.xlsx',
        help='Excel file name',
    )
    codification_parser.add_argument(
        '-init_cell', default='D2', help='Initial cell with verb'
    )
    # Add any specific arguments for the codification script here
    codification_parser.set_defaults(func=codification.main)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
