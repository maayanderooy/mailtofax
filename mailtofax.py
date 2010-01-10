#!/usr/bin/env python

import email
from optparse import OptionParser
import sys

import settings


def main():
    parser = OptionParser()
    usage = "usage: %prog [options] file"
    parser = OptionParser(usage)
    parser.add_option('-c', '--stdin', dest='stdin', action="store_true",
                      help='read data from stdin, not the file argument')
    (options, args) = parser.parse_args()

    if options.stdin:
        mailfile = sys.stdin
    else:
        try:
            mailfile = open(args[0])
        except IndexError:
            print "The file argument is required!"
            sys.exit(1)
        except IOError:
            print "Input file not found!"
            sys.exit(1)
    msg = email.message_from_file(mailfile)

if __name__ == '__main__':
    main()

