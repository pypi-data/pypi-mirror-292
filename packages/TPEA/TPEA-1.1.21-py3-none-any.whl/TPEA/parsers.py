"""Argument parsers."""

import argparse
import sys

from TPEA import __version__

def add_SRRHISAT_subparser(subparsers):
    parser = subparsers.add_parser(
        "SRRHISAT",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $TPEA SRRHISAT --SRR SRR16092814 --SILVA SILVA_Bacteria --CPU 10 --miniLen 150\n"
        "  Output: SRR16092814.sam and SRR16092814.summary\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--SILVA",
        help="INDEX of 16S genes, e.g., SILVA_Bacteria",
        type=str,
    )
    
    parser.add_argument(
        "--CPU",
        default="10",
        help="Number of CPU",
        type=int,
    )
    
    parser.add_argument(
        "--miniLen",
        default="50",
        help="Minimum length of reads",
        type=int,
    )

def add_SRRHISATSIN_subparser(subparsers):
    parser = subparsers.add_parser(
        "SRRHISATSIN",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $TPEA SRRHISAT --SRR SRR16092814 --SILVA SILVA_Bacteria --CPU 10 --miniLen 150\n"
        "  Output: SRR16092814.sam and SRR16092814.summary\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--SILVA",
        help="INDEX of 16S genes, e.g., SILVA_Bacteria",
        type=str,
    )
    
    parser.add_argument(
        "--CPU",
        default="10",
        help="Number of CPU",
        type=int,
    )
    
    parser.add_argument(
        "--miniLen",
        default="50",
        help="Minimum length of reads",
        type=int,
    )

def add_HISATLOCAL_subparser(subparsers):
    parser = subparsers.add_parser(
        "HISATLOCAL",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in TEST:\n"
        "  require TEST_1.fastq.gz and TEST_2.fastq.gz "
        "  $TPEA HISATLOCAL --SRR TEST --SILVA SILVA_Bacteria --CPU 10\n"
        "  Output: TEST.sam and TEST.summary\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Local RUN, e.g., TEST",
        type=str,
    )
    
    parser.add_argument(
        "--SILVA",
        help="INDEX of 16S genes, e.g., SILVA_Bacteria",
        type=str,
    )
    
    parser.add_argument(
        "--CPU",
        default="10",
        help="Number of CPU",
        type=int,
    )


def add_HISATFA_subparser(subparsers):
    parser = subparsers.add_parser(
        "HISATFA",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in TEST:\n"
        "  require TEST_1.fastq.gz and TEST_2.fastq.gz "
        "  $TPEA HISATFA --SRR TEST --SILVA SILVA_Bacteria --CPU 10\n"
        "  Output: TEST.sam and TEST.summary\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Local RUN, e.g., TEST",
        type=str,
    )
    
    parser.add_argument(
        "--SILVA",
        help="INDEX of 16S genes, e.g., SILVA_Bacteria",
        type=str,
    )
    
    parser.add_argument(
        "--CPU",
        default="10",
        help="Number of CPU",
        type=int,
    )

def add_MAP16S_subparser(subparsers):
    parser = subparsers.add_parser(
        "MAP16S",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $TPEA MAP16S --SRR SRR16092814 --TaxB tax_slv_ssu_138.bacteria.txt --RefID SILVA_138.1_used_tax_silva.ID_List\n"
        "  Output: SRR16092814.class1 and SRR16092814.class2\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--TaxB",
        default="tax_slv_ssu_138.bacteria.txt",
        help="tax",
        type=str,
    )
    
    parser.add_argument(
        "--RefID",
        default="SILVA_138.1_used_tax_silva.ID_List",
        help="tax",
        type=str,
    )

def add_MAP16SSIN_subparser(subparsers):
    parser = subparsers.add_parser(
        "MAP16SSIN",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $TPEA MAP16S --SRR SRR16092814 --TaxB tax_slv_ssu_138.bacteria.txt --RefID SILVA_138.1_used_tax_silva.ID_List\n"
        "  Output: SRR16092814.class1 and SRR16092814.class2\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--TaxB",
        default="tax_slv_ssu_138.bacteria.txt",
        help="tax",
        type=str,
    )
    
    parser.add_argument(
        "--RefID",
        default="SILVA_138.1_used_tax_silva.ID_List",
        help="tax",
        type=str,
    )

def add_MAPN_subparser(subparsers):
    parser = subparsers.add_parser(
        "MAPN",
        help="Find plant reads matched bacteria lineages",
        description="Find plant reads matched 16S genes of bacteria lineages from the SILVA database.",
        epilog="Usage examples\n--------------\n"
        "Detecting reads in SRR16092814:\n"
        "  $TPEA MAPN --SRR SRR16092814 --TaxB tax_slv_ssu_138.bacteria.txt --RefID SILVA_138.1_used_tax_silva.ID_List\n"
        "  Output: SRR16092814.class1 and SRR16092814.class2\n\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--SRR",
        help="Accession Number of RUN, e.g., SRR16092814",
        type=str,
    )
    
    parser.add_argument(
        "--TaxB",
        default="tax_slv_ssu_138.bacteria.txt",
        help="tax",
        type=str,
    )
    
    parser.add_argument(
        "--RefID",
        default="SILVA_138.1_used_tax_silva.ID_List",
        help="tax",
        type=str,
    )

def get_parser():
    parser = argparse.ArgumentParser(
        "TPEA",
        description="TPEA: Toolkit for Plant Endophyte Analyses",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    subparsers = parser.add_subparsers(dest="command")
    add_SRRHISAT_subparser(subparsers)
    add_SRRHISATSIN_subparser(subparsers)
    add_MAP16S_subparser(subparsers)
    add_MAP16SSIN_subparser(subparsers)
    add_HISATLOCAL_subparser(subparsers)
    add_HISATFA_subparser(subparsers)
    add_MAPN_subparser(subparsers)
    return parser

def parse_args(args):
    parser = get_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        parser.exit(1)

    return args