#!/usr/bin/env python

import os
import sys
if sys.version_info < (2,7):
    print("kubenamespace needs Python 2.7 to run, please upgrade")
    sys.exit(7)

from subprocess import check_output, call
from pick import pick
import argparse
import shlex
import traceback

def getNamespaces(substring=""):
    namespaces = []

    # Get terminal width
    rows, columns = os.popen('stty size', 'r').read().split()
    width = int(columns) - 7

    try:
        cmd = "kubectl get namespaces"
        output = check_output(shlex.split(cmd))
        output = output.decode(encoding='UTF-8').split("\n")[1:];
        for line in output:
            if not isBlank(line):
                if line.startswith(substring):
                    if width < len(line):
                        namespaces.append(line[:width] + "..." )
                    else:
                        namespaces.append(line)
    except Exception as e:
        print ("Unable to get namespaces when running: " + cmd)
        print (e)
        traceback.print_exc()
        pass
    return namespaces

def getCurrentNamespace():
    try:
        cmd = "kubectl config view --minify --output 'jsonpath={..namespace}'"
        output = check_output(shlex.split(cmd))
        return output.decode(encoding='UTF-8').strip()
    except Exception as e:
        print ("Unable to get current namespace")
        print (e)
        traceback.print_exc()
        return None

def setNamespace(namespace):
    try:
        cmd = "kubectl config set-context --current --namespace={}".format(namespace)
        call(shlex.split(cmd))
    except Exception as e:
        print ("Unable to set namespace")
        print (e)
        traceback.print_exc()

def getAbsolutePath (path):
    if path is None:
        return path
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def setupParser ():
    parser = argparse.ArgumentParser(description='interactively pick a k8s namespace')
    parser.add_argument('substring', nargs='?', help="substring to filter namespaces", default="")
    parser.add_argument('--list', action='store_true', help="list namespaces instead of launching interactive menu")
    return parser

def isBlank (myString):
    return not (myString and myString.strip())

def crux ():
    parser = setupParser()
    args = parser.parse_args()

    if args.list:
        namespaces = getNamespaces(args.substring)
        for ns in namespaces:
            print(ns.split(' ', 1)[0])
        sys.exit(0)

    current_index = 0
    options = getNamespaces(args.substring)
    
    if args.substring:
        matching_namespaces = [ns for ns in options if ns.startswith(args.substring)]
        if len(matching_namespaces) == 1:
            namespace = matching_namespaces[0].split(' ', 1)[0]
            print("Setting namespace to: " + namespace)
            setNamespace(namespace)
            sys.exit(0)
        elif len(matching_namespaces) > 1:
            options = matching_namespaces

    while True:
        current_namespace = getCurrentNamespace()
        if current_namespace:
            title = 'Current namespace: {}\nPick your namespace:\n'.format(current_namespace)
        else:
            title = 'Pick your namespace:\n'
        options.append("exit")
        try:
            option, index = pick(options, title, "=>", current_index)
            if option == "exit":
                sys.exit(0)

            namespace = option.split(' ', 1)[0]
            print("Selected namespace: " + namespace)
            setNamespace(namespace)
            sys.exit(0)
        except Exception as e:
            print (e)
            sys.exit(3)

if __name__ == "__main__":
    crux()
