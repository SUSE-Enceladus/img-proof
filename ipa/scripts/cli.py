#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import sys


def validate_count(ctx, param, value):
    if value < 0:
        raise click.BadParameter('Should be a positive integer.')
    return value


@click.group()
@click.version_option()
def ipa():
    pass


@click.command()
@click.option('-p', '--key-file',
              default='TODO From config',
              help='Private Key File.',
              type=click.Path(exists=True))
@click.option('-r', '--results-dir',
              default='/tmp/ipa/results',
              help='Location to store the test results.',
              type=click.Path(exists=True))
@click.argument('image-id', type=click.STRING)
@click.argument('provider', type=click.STRING)
@click.argument('region', type=click.STRING)
def test(key_file, results_dir, image_id, provider, region):
    """Test image console script"""
    try:
        raise Exception('Test Image not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)


@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--count',
              default=10,
              help='Number of tests run.',
              callback=validate_count)
def results(verbose, count):
    if verbose:
        click.echo(click.style('Passed: %i tests successful.' % count,
                               fg='green'))
    else:
        click.echo(click.style('Passed!', fg='green'))


ipa.add_command(test)
ipa.add_command(results)

if __name__ == "__main__":
    ipa()
