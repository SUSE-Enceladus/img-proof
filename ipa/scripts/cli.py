#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import sys


@click.group()
@click.version_option()
def ipa():
    pass


@click.command()
def test():
    """Test image in the given cloud framework using the supplied test file."""
    try:
        raise Exception('Test command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)


@click.command()
def results():
    try:
        raise Exception('Results command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)

@click.command()
def list_tests():
    try:
        raise Exception('List tests command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)

ipa.add_command(test)
ipa.add_command(results)
ipa.add_command(list_tests)

if __name__ == "__main__":
    ipa()

