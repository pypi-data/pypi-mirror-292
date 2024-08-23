#!/usr/bin/env python
# encoding: utf-8

import urllib.request
import datetime
from lxml import etree
from packaging.version import parse as parse_version

class Definitions():
    """Definitions for the module."""

    DOWNLOADPAGE = "https://www.libreoffice.org/download/download/"
    ARCHIVE = "https://downloadarchive.documentfoundation.org/libreoffice/old/"
    RELEASE = "https://download.documentfoundation.org/libreoffice/stable/"
    DAILY = "https://dev-builds.libreoffice.org/daily/master/"
    PRERELEASE = "https://dev-builds.libreoffice.org/pre-releases/deb/x86_64/"

    SELECTORS = {
        'still': {
            'URL': DOWNLOADPAGE,
            'xpath': '(//span[@class="dl_version_number"])[last()]/text()'
        },
        'fresh': {
            'URL': DOWNLOADPAGE,
            'xpath': '(//span[@class="dl_version_number"])[1]/text()'
        },
        'prerelease': {
            'URL': DOWNLOADPAGE,
            'xpath': '//p[@class="lead_libre"][last()]/following-sibling::ul[last()]/li/a/text()'
        },
        'daily': {
            'URL': DAILY,
            'xpath': '//td/a'
        }
    }

class Base():
    """Contains methods that might be useful outside class."""
    # Class for static methods which might be useful even outside the build
    # scripts.

    @staticmethod
    def dailyurl(date = datetime.datetime.today()):
        """Returns the URL for the latest valid daily build."""
        # As per other parts of the build, we need to maintain an URL also for
        # x86 versions that it isn't really provided.
        # As such, the return value must be a dictionary

        # Fixing daily selector
        # As seen, the number of the tinderbox building the daily version can
        # change. We try to fulfill the void by adding a step.
        tinderboxpage = etree.HTML(urllib.request.urlopen(Definitions.DAILY).read())
        tburl = tinderboxpage.xpath(
            "//td/a[starts-with(text(), 'Linux-rpm_deb-x86') and contains(text(), 'TDF/')]/text()"
        )[0]
        daily_selector = f"{Definitions.DAILY}{tburl}"

        # Get the anchor for today's builds
        raw_page = etree.HTML(urllib.request.urlopen(daily_selector).read())


        results = raw_page.xpath(
            f"""//td/a[contains(text(), "{date.strftime('%Y-%m-%d')}")]/text()"""
        )
        if len(results) == 0:
            # No results found, no version found, let's return a
            return { 'x86': '-', 'x86_64': '-' }

        # On the contrary, more than a version is found. let's order the
        # list and get the latest item
        return { 'x86': '-', 'x86_64': f"{daily_selector}{sorted(results)[-1]}" }

    @staticmethod
    def dailyver(date = datetime.datetime.today()):
        """Returns versions present on the latest daily build."""
        url = Base.dailyurl(date)['x86_64']
        # If no daily releases has been provided yet, return empty
        if url == '-':
            return []

        # Rerun the page parsing, this time to find out the versions built
        b = etree.HTML(urllib.request.urlopen(url).read()).xpath("//td/a[contains(text(), '_deb.tar.gz')]/text()")
        # This should have returned the main package for a version, but can
        # have returned multiple ones, so let's treat it as a list
        return [ x.split('_')[1] for x in b ]

    @staticmethod
    def namedver(query):
        """Gets the version for a specific named version."""

        if query == 'daily' or query == 'yesterday':
            # Daily needs double parsing for the same result to apply.
            # We first select today's build anchor:
            date = datetime.datetime.today()
            if query == 'yesterday':
                # Use yesterdays' date for testing purposes.
                date += datetime.timedelta(days=-1)
            return Base.dailyver(date)

        # In case the query isn't for daily
        return etree.HTML(urllib.request.urlopen(Definitions.SELECTORS[query]['URL']).read()).xpath(Definitions.SELECTORS[query]['xpath'])

    @staticmethod
    def fullversion(version):
        """Get latest full version from Archive based on partial version."""
        versionlist = etree.HTML(urllib.request.urlopen(Definitions.ARCHIVE).read()).xpath(f"//td/a[starts-with(text(), '{version}')]/text()")
        if versionlist:
            cleanlist = sorted([ x.strip('/') for x in versionlist ])

            # Sorting, then returning the last version
            return cleanlist[-1]

        return None

    @staticmethod
    def urlfromqueryandver(query, version):
        """Returns the fetching URL based on the queried version and the numeric version of it."""
        # This has the purpose to simplify and explain how the releases are
        # layed out.

        # If the query tells about daily or 'yesterday' (for testing purposes),
        # we might ignore versions and return the value coming from dailyurl:
        if query == 'daily':
            return Base.dailyurl()
        if query == 'yesterday':
            date = datetime.datetime.today() + datetime.timedelta(days=-1)
            return Base.dailyurl(date)

        # All other versions will be taken from Archive, as such we need a full
        # version.

        # If the version has only 2 points in it (or splits into three parts by '.'), that's not a full version and we will call the getlatestver() function
        fullversion = str(version)
        if len(fullversion.split('.')) <= 3:
            fullversion = str(Base.fullversion(version))

        # So the final URL is the Archive one, plus the full versions, plus a
        # final '/deb/' - and an arch subfolder
        baseurl = Definitions.ARCHIVE + fullversion + '/deb/'
        retval = {}

        # x86 binaries are not anymore offered after 6.3.0.
        if parse_version(fullversion) < parse_version('6.3.0'):
            retval['x86'] = baseurl + 'x86/'
        else:
            retval['x86'] = '-'
        
        retval['x86_64'] = baseurl + 'x86_64/'
    
        return retval

    @staticmethod
    def collectedbuilds(query):
        """Creates a list of Builds based on each queried version found."""
        retval = []
        if '.' in query:
            # Called with a numeric query. Pass it to RemoteBuild
            retval.append(RemoteBuild(query))
        else:
            # Named query
            a = Base.namedver(query)

            if not a:
                # a is empty
                return retval

            if isinstance(a, list) and len(a) > 1:
                retval.extend([ RemoteBuild(query, version) for version in a ])
            else:
                retval.append(RemoteBuild(query))

        return sorted(retval, key=lambda x: x.version)


class RemoteBuild(object):

    def __init__(self, query, version = None):
        """Should simplify the single builded version."""
        self.query = query
        self.version = ''
        self.basedirurl = { 'x86': '-', 'x86_64': '-' }

        if version and isinstance(version, str):
            self.version = version

        if not '.' in self.query:
            # Named version.
            # Let's check if a specific version was requested.
            if self.version == '':
                # In case it was not requested, we will carry on the generic
                # namedver() query. 
                # If the results are more than one, we'll take the latest (since we are requested to provide a single build).
                a = Base.namedver(self.query)
                
                if isinstance(a, list):
                    # if the number of versions is zero, return and exit
                    if not a:
                        return None

                    if len(a) == 1:
                        # version is a single one.
                        self.version = a[0]
                    else:
                        # In this case, we will select the latest release.
                        self.version = sorted(a)[-1]

            # If the version has already a version, as requested by user,
            # continue using that version
        else:
            # In case of numbered queries, put it as initial version
            self.version = self.query

        if len(str(self.version).split('.')) < 4:
            # If not 4 dotted, let's search for the 4 dotted version
            self.version = Base.fullversion(self.version)
        
        self.basedirurl = Base.urlfromqueryandver(self.query, self.version)

    def todict(self):
        return {
            'query': self.query,
            'version': self.version,
            'basedirurl': self.basedirurl
        }

    def __str__(self):
        return f"""query: {self.query}
version: {self.version}
x86: {self.basedirurl['x86']}
x86_64: {self.basedirurl['x86_64']}"""
