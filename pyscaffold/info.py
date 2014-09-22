# -*- coding: utf-8 -*-
"""
Provide general information about the system, user etc.
"""
from __future__ import print_function, absolute_import

import os
import imp
import copy
import socket
import getpass
import random
from subprocess import CalledProcessError

from . import utils
from . import shell

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def username():
    """
    Retrieve the user's name

    :return: user's name as string
    """
    try:
        user = next(shell.git("config", "--global", "--get", "user.name"))
        user = str(user).strip()
    except CalledProcessError:
        user = getpass.getuser()
    return user


def email():
    """
    Retrieve the user's email

    :return: user's email as string
    """
    try:
        email = next(shell.git("config", "--global", "--get", "user.email"))
        email = str(email).strip()
    except CalledProcessError:
        user = getpass.getuser()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)
    return email


def is_git_installed():
    """
    Check if git is installed

    :return: boolean
    """
    try:
        shell.git("--version")
    except CalledProcessError:
        return False
    return True


def project(args):
    """
    Update user settings with the settings of an existing PyScaffold project

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: updated command line parameters as :obj:`argparse.Namespace`
    """
    args = copy.copy(args)
    if not os.path.exists(args.project):
        raise RuntimeError("Project {project} does not"
                           " exist!".format(project=args.project))
    imp.load_source("versioneer", os.path.join(args.project, "versioneer.py"))
    # Generate setup with random module name since this function might be
    # called several times (in unittests) and imp.load_source seems to
    # not properly reload an already loaded file.
    mod_name = "setup_{rand}".format(rand=random.getrandbits(32))
    setup = imp.load_source(mod_name, os.path.join(args.project, "setup.py"))
    if args.description is None:
        args.description = setup.DESCRIPTION
    if args.license is None:
        args.license = setup.LICENSE
    if args.url is None:
        args.url = setup.URL
    if args.junit_xml is None:
        args.junit_xml = utils.safe_get(setup, "JUNIT_XML")
    if args.coverage_xml is None:
        args.coverage_xml = utils.safe_get(setup, "COVERAGE_XML")
    if args.coverage_html is None:
        args.coverage_html = utils.safe_get(setup, "COVERAGE_HTML")
    args.package = setup.MAIN_PACKAGE
    args.console_scripts = utils.list2str(setup.CONSOLE_SCRIPTS, indent=19)
    args.classifiers = utils.list2str(setup.CLASSIFIERS, indent=15)

    return args
