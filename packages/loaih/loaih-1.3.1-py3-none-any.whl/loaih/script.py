#!/usr/bin/env python
# encoding: utf-8
"""Helps with command line commands."""

import os
import json
import click
import yaml
import loaih
import loaih.build

@click.group()
def cli():
    """Helps with command line commands."""

@cli.command()
@click.option('-j', '--json', 'jsonout', default=False, is_flag=True,
    help="Output format in json.")
@click.argument('query')
def getversion(query, jsonout):
    """Get the numeral version from a named version."""

    batch = []
    queries = []
    if ',' in query:
        queries.extend(query.split(','))
    else:
        queries.append(query)

    for singlequery in queries:
        batch.extend(loaih.Base.collectedbuilds(singlequery))

    if len(batch) > 0:
        if jsonout:
            click.echo(json.dumps([x.todict() for x in batch]))
        else:
            for value in batch:
                click.echo(value)

@cli.command()
@click.option('-a', '--arch', 'arch', default='all',
    type=click.Choice(['x86', 'x86_64', 'all'], case_sensitive=False),
    help="Build the AppImage for a specific architecture. If there is no specific options, the process will build for both architectures (if available). Default: all")
@click.option('-c/-C', '--check/--no-check', 'check', default=True,
    help="Check in the final storage if the queried version is existent. Default: check")
@click.option('-d', '--download-path', 'download_path',
    default = '/var/tmp/downloads', type=str,
    help="Path to the download folder. Default: /var/tmp/downloads")
@click.option('-l', '--language', 'language', default = 'basic', type=str,
    help="Languages to be included. Options: basic, standard, full, a language string (e.g. 'it') or a list of languages comma separated (e.g.: 'en-US,en-GB,it'). Default: basic")
@click.option('-o/-O', '--offline-help/--no-offline-help', 'offline', default = False,
    help="Include or not the offline help for the chosen languages. Default: no offline help")
@click.option('-p/-P', '--portable/--no-portable', 'portable', default = False,
    help="Create a portable version of the AppImage or not. Default: no portable")
@click.option('-r', '--repo-path', 'repo_path', default = '/mnt/appimage',
    type=str, help="Path to the final storage of the AppImage. Default: /mnt/appimage")
@click.option('-s/-S', '--sign/--no-sign', 'sign', default=True,
    help="Wether to sign the build. Default: sign")
@click.option('-u/-U', '--updatable/--no-updatable', 'updatable', default = True,
    help="Create an updatable version of the AppImage or not. Default: updatable")
@click.argument('query')
def build(arch, language, offline, portable, updatable, download_path, repo_path, check, sign, query):
    """Builds an Appimage with the provided options."""

    # Parsing options
    arches = []
    if arch.lower() == 'all':
        # We need to build it twice.
        arches = [ 'x86', 'x86_64' ]
    else:
        arches = [ arch.lower() ]

    if query.endswith('.yml') or query.endswith('.yaml'):
        # This is a buildfile. So we have to load the file and pass the build options ourselves.
        config = {}
        with open(query, 'r', encoding= 'utf-8') as file:
            config = yaml.safe_load(file)

        # With the config file, we ignore all the command line options and set
        # generic default.
        for cbuild in config['builds']:
            # Loop a run for each build.
            collection = loaih.build.Collection(cbuild['query'], arches)

            for obj in collection:
                # Configuration phase
                obj.language = cbuild['language']
                obj.offline_help = cbuild['offline_help']
                obj.portable = cbuild['portable']
                obj.updatable = True
                obj.storage_path = "/srv/http/appimage.sys42.eu"
                if 'repo' in config['data'] and config['data']['repo']:
                    obj.storage_path = config['data']['repo']
                obj.download_path = "/var/tmp/downloads"
                if 'download' in config['data'] and config['data']['download']:
                    obj.download_path = config['data']['download']
                if 'http' in obj.storage_path:
                    obj.remoterepo = True
                    obj.remote_host = "ciccio.libreitalia.org"
                    if 'remote_host' in config['data'] and config['data']['remote_host']:
                        obj.remote_host = config['data']['remote_host']
                    obj.remote_path = "/var/lib/nethserver/vhost/appimages"
                    if 'remote_path' in config['data'] and config['data']['remote_path']:
                        obj.remote_path = config['data']['remote_path']

                if 'sign' in config['data'] and config['data']['sign']:
                    obj.sign = True

                # Build phase
                obj.calculate()
                if not 'force' in config['data'] or not config['data']['force']:
                    obj.check()

                obj.download()
                obj.build()
                obj.checksums()
                if obj.remoterepo and obj.appnamedir:
                    obj.generalize_and_link(obj.appnamedir)
                obj.publish()
                if not obj.remoterepo:
                    obj.generalize_and_link()
                del obj

    else:
        collection = loaih.build.Collection(query, arches)
        for obj in collection:
            # Configuration phase
            obj.language = language
            obj.offline_help = offline
            obj.portable = portable
            obj.updatable = updatable
            if repo_path == '.':
                repo_path = os.getcwd()
            obj.storage_path = repo_path
            obj.download_path = download_path

            if sign:
                obj.sign = True

            # Running phase
            obj.calculate()

            if check:
                obj.check()

            obj.download()
            obj.build()
            obj.checksums()
            obj.publish()
            obj.generalize_and_link()
            del obj
