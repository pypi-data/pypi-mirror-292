#!/usr/bin/env python
# encoding: utf-8

import click
import yaml
import loaih, loaih.build
import re, sys, json

@click.group()
def cli():
    pass

@cli.command()
@click.option('-j', '--json', 'jsonout', default=False, is_flag=True, help="Output format in json.")
@click.argument('query')
def getversion(query, jsonout):
    b = []
    queries = []
    if ',' in query:
        queries.extend(query.split(','))
    else:
        queries.append(query)

    for q in queries:
        b.extend(loaih.Base.collectedbuilds(q))

    if len(b) > 0:
        if jsonout:
            click.echo(json.dumps([x.todict() for x in b]))
        else:
            for v in b:
                click.echo(v)

@cli.command()
@click.option('-a', '--arch', 'arch', type=click.Choice(['x86', 'x86_64', 'all'], case_sensitive=False), default='all', help="Build the AppImage for a specific architecture. If there is no specific options, the process will build for both architectures (if available). Default: all")
@click.option('-c/-C', '--check/--no-check', 'check', default=True, help="Check in the final storage if the queried version is existent. Default: check")
@click.option('-d', '--download-path', 'download_path', default = '/var/tmp/downloads', type=str, help="Path to the download folder. Default: /var/tmp/downloads")
@click.option('-l', '--language', 'language', default = 'basic', type=str, help="Languages to be included. Options: basic, standard, full, a language string (e.g. 'it') or a list of languages comma separated (e.g.: 'en-US,en-GB,it'). Default: basic")
@click.option('-o/-O', '--offline-help/--no-offline-help', 'offline', default = False, help="Include or not the offline help for the chosen languages. Default: no offline help")
@click.option('-p/-P', '--portable/--no-portable', 'portable', default = False, help="Create a portable version of the AppImage or not. Default: no portable")
@click.option('-r', '--repo-path', 'repo_path', default = '/mnt/appimage', type=str, help="Path to the final storage of the AppImage. Default: /mnt/appimage")
@click.option('-s/-S', '--sign/--no-sign', 'sign', default=True, help="Wether to sign the build. Default: sign")
@click.option('-u/-U', '--updatable/--no-updatable', 'updatable', default = True, help="Create an updatable version of the AppImage or not. Default: updatable")
@click.argument('query')
def build(arch, language, offline, portable, updatable, download_path, repo_path, check, sign, query):
    # Parsing options
    arches = []
    if arch.lower() == 'all':
        # We need to build it twice.
        arches = [ u'x86', u'x86_64' ]
    else:
        arches = [ arch.lower() ]

    if query.endswith('.yml') or query.endswith('.yaml'):
        # This is a buildfile. So we have to load the file and pass the build options ourselves.
        config = {}
        with open(query, 'r') as file:
            config = yaml.safe_load(file)

        # With the config file, we ignore all the command line options and set
        # generic default.
        for build in config['builds']:
            # Loop a run for each build.
            collection = loaih.build.Collection(build['query'], arches)

            for obj in collection:
                # Configuration phase
                obj.language = build['language']
                obj.offline_help = build['offline_help']
                obj.portable = build['portable']
                obj.updatable = True
                obj.storage_path = config['data']['repo'] if 'repo' in config['data'] and config['data']['repo'] else '/srv/http/appimage.sys42.eu'
                obj.download_path = config['data']['download'] if 'download' in config['data'] and config['data']['download'] else '/var/tmp/downloads'

                if 'sign' in config['data'] and config['data']['sign']:
                    obj.sign = True

                # Build phase
                obj.calculate()
                if not 'force' in config['data'] or not config['data']['force']:
                    obj.check()

                obj.download()
                obj.build()
                obj.checksums()
                obj.publish()
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
