#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
A python script that utilises getontracks API to store tasks. Can be fed with a
mail message through mutt's pipe command.

'''

import os
import sys
import argparse
import getpass
import xml.etree.ElementTree as ET
from email.header import decode_header
from email.parser import Parser
from termcolor import colored
import requests

def findel(element, **kwargs):
    headers = {"Content-Type":"text/xml"}
    r = requests.get('https://%s/%s.xml' % (kwargs['server'],element),
                     auth=(kwargs['username'],kwargs['password']),
                     verify=kwargs['verifyCert'], headers=headers)

    if r.status_code == 200:
        tree = ET.fromstring(r.text)
        return list(map(lambda item: (item[0].text, item[1].text), tree))
    else:
        print(colored(("Couldn't get %s from server: %s\n"
                       % (element, kwargs['server'])), 'red'))
        sys.exit(1)

def writeel(description, project, context, **kwargs):
    payload = unicode("""
            <todo>
                    <description>%s</description>
                    <context_id>%i</context_id>
                    <project_id>%i</project_id>
            </todo>"""
               % (description, context, project)).encode("utf-8")

    p = payload.encode('utf-8')

    headers = {"Content-Type":"application/xml"}
    r = requests.post('https://%s/todos.xml' % (kwargs['server']),
                      auth=(kwargs['username'],kwargs['password']),
                      verify=kwargs['verifyCert'], data=p,
                      headers=headers)

    if r.status_code == 201:
        print(colored(("Succesfully created task: %s\n"
                       % r.headers['Location']), 'green'))
        return
    else:
        print(colored("Couldn't insert todo\n", 'red'))
        sys.exit(1)


def main():

    parser = argparse.ArgumentParser(description='Input parameters',
                                     epilog='''EXAMPLE:
                                     mutt2getontracks.py -t tracks.example.com''',
                                     add_help=False,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--help', dest='printhelp', action='store_true', 
                        help='Print help.')
    try:
        printhelp = parser.parse_known_args()[0].printhelp
    except AttributeError:
        printhelp = False

    parser.add_argument('-u', '--username', dest='username', action='store',
                        default=os.environ['USER'], help='username to connect\
                        to server.')
    parser.add_argument('-p', '--password', dest='password', action='store',
                        help='user\'s password.')
    parser.add_argument('-t', '--target', dest='target', action='store',
                        help='getontracks server URL')
    parser.add_argument('-c', '--config', dest='configfile', action='store',
                        required=False, help='Configuration file to read.')
    parser.add_argument('--no-certverify', dest='verifyCert',
                        action='store_false',
                        help='Do not verify certificate if https is used')

    if printhelp:
        parser.print_help()
        sys.exit(0)

    parser.set_defaults(verifyCert=True)
    args = parser.parse_args()

    if not args.target:
        sys.stdout.write('getontracks server not set. Aborting!\n')
        sys.exit(1)

    if not args.password:
        args.password = getpass.getpass(args.username + '\'s Password:')

    params = {
        'server': args.target,
        'username': args.username,
        'password': args.password,
        'verifyCert': args.verifyCert
        }

    if not sys.stdin.isatty():
        input_stream = sys.stdin.read()
        if input_stream:
            headers = Parser().parsestr(input_stream)
            description = decode_header(headers['Subject'])[0][0].decode('utf-8')
            description = ' '.join([ unicode(t[0], t[1] or default_charset) 
                                    for t in decode_header(headers['Subject'])])
    else:
        sys.stderr.write("No data available from stdin.\n")
        sys.exit(1)
    sys.stdin = open('/dev/tty')

    contexts = findel('contexts', **params)
    projects = findel('projects', **params)
    print(colored("-------------------------------------------------------------\n", 'magenta'))
    print(colored("Available contexts:", "cyan"))
    for c in contexts:
        print(colored (('%s, %s' % (c[0], c[1])), 'yellow'))
    print(colored("-------------------------------------------------------------\n", 'magenta'))
    context = int()
    while context not in [item[0] for item in contexts]:
        context = input('Select context: ')
    print(colored("-------------------------------------------------------------\n", 'magenta'))
    print(colored("Available projects:", "cyan"))
    for p in projects:
        print(colored (('%s, %s' % (p[0], p[1])), 'yellow'))
    print(colored("-------------------------------------------------------------\n", 'magenta'))
    project = int()
    while project not in [item[0] for item in projects]:
        project = input('Select project: ')
    writeel(description, int(context), int(project), **params)
    sys.exit(0)

if __name__ == '__main__':
    main()
