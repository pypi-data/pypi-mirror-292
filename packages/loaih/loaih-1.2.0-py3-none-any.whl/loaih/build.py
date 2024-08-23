#!/usr/bin/env python3

import urllib.request
import loaih
from lxml import etree
import tempfile, os, sys, glob, subprocess, shutil, re, shlex

class Collection(list):

    def __init__(self, query, arch = ['x86', 'x86_64']):
        """Build a list of version to check/build for this round."""
        super().__init__()
        self.extend([ Build(query, arch, version) for version in loaih.Base.collectedbuilds(query) ])

class Build(loaih.RemoteBuild):
    LANGSTD = [ 'ar', 'de', 'en-GB', 'es', 'fr', 'it', 'ja', 'ko', 'pt', 'pt-BR', 'ru', 'zh-CN', 'zh-TW' ]
    LANGBASIC = [ 'en-GB' ]
    ARCHSTD = [ u'x86', u'x86_64' ]

    def __init__(self, query, arch, version = None):
        super().__init__(query, version)
        self.arch = arch
        self.short_version = str.join('.', self.version.split('.')[0:2])
        self.branch_version = None
        if not '.' in self.query:
            self.branch_version = self.query
        self.url = self.basedirurl

        # Other default values
        self.language = 'basic'
        self.offline_help = False
        self.portable = False
        self.updatable = True
        self.sign = True
        self.storage_path = '/mnt/appimage'
        self.download_path = '/var/tmp/downloads'

        # Specific build version
        self.appversion = ''
        self.appimagefilename = {}
        self.zsyncfilename = {}

        # Creating a tempfile
        self.builddir = tempfile.mkdtemp()
        self.tarballs = {}
        self.built = { u'x86': False, u'x86_64': False }
        
        # Preparing the default for the relative path on the storage for
        # different versions.
        # The path will evaluated as part of the check() function, as it is
        # understood the storage_path can be changed before that phase.
        self.relative_path = []
        self.full_path = ''
        self.baseurl = ''

    def calculate(self):
        """Calculate exclusions and other variables."""
        # AppName
        self.appname = 'LibreOffice' if not self.query == 'daily' and not self.query == 'prerelease' else 'LibreOfficeDev'

        # Calculating languagepart
        self.languagepart = "."
        if ',' in self.language:
            self.languagepart += self.language.replace(',', '-')
        else:
            self.languagepart += self.language

        # Calculating help part
        self.helppart = '.help' if self.offline_help else ''

        # Building the required names
        for arch in Build.ARCHSTD:
            self.appimagefilename[arch] = self.__gen_appimagefilename__(self.version, arch)
            self.zsyncfilename[arch] = self.appimagefilename[arch] + '.zsync'

        # Mandate to the private function to calculate the full_path available
        # for the storage and the checks.
        self.__calculate_full_path__()


    def __gen_appimagefilename__(self, version, arch):
        """Generalize the construction of the name of the app."""
        self.appversion = version + self.languagepart + self.helppart
        return self.appname + f'-{self.appversion}-{arch}.AppImage'


    def __calculate_full_path__(self):
        """Calculate relative path of the build, based on internal other variables."""
        if len(self.relative_path) == 0:
            if self.query == 'daily':
                self.relative_path.append('daily')
            elif self.query == 'prerelease':
                self.relative_path.append('prerelease') 

            # Not the same check, an additional one
            if self.portable:
                self.relative_path.append('portable')

        fullpath_arr = self.storage_path.split('/')
        # Joining relative path only if it is not null
        if len(self.relative_path) > 0:
            fullpath_arr.extend(self.relative_path)
        self.full_path = re.sub(r"/+", '/', str.join('/', fullpath_arr))


    def check(self):
        """Checking if the requested AppImage has been already built."""
        if not len(self.appimagefilename) == 2:
            self.calculate()

        for arch in self.arch:
            print(f"Searching for {self.appimagefilename[arch]}")
            res = subprocess.run(shlex.split(f"find {self.full_path} -name {self.appimagefilename[arch]}"), capture_output=True, env={ "LC_ALL": "C" }, text=True, encoding='utf-8')

            if "No such file or directory" in res.stderr:
                # Folder is not existent: so the version was not built
                # Build stays false, and we go to the next arch
                continue

            if res.stdout and len(res.stdout.strip("\n")) > 0:
                # All good, the command was executed fine.
                print(f"Build for {self.version} found.")
                self.built[arch] = True

            if self.built[arch]:
                print(f"The requested AppImage already exists on storage for {arch}. I'll skip downloading, building and moving the results.")


    def download(self):
        """Downloads the contents of the URL as it was a folder."""
        print(f"Started downloads for {self.version}. Please wait.")
        for arch in self.arch:
            # Checking if a valid path has been provided
            if self.url[arch] == '-':
                print(f"No build has been provided for the requested AppImage for {arch}. Continue with other options.")
                # Faking already built it so to skip other checks.
                self.built[arch] = True
                continue

            if self.built[arch]:
                print(f"A build for {arch} was already found. Skipping specific packages.")
                continue

            # Identifying downloads
            contents = etree.HTML(urllib.request.urlopen(self.url[arch]).read()).xpath("//td/a")
            self.tarballs[arch] = [ x.text for x in contents if x.text.endswith('tar.gz') and 'deb' in x.text ]
            tarballs = self.tarballs[arch]
            maintarball = tarballs[0]

            # Create and change directory to the download location
            os.makedirs(self.download_path, exist_ok = True)
            os.chdir(self.download_path)
            for archive in tarballs:
                # If the archive is already there, do not do anything.
                if os.path.exists(archive):
                    continue

                # Download the archive
                try:
                    urllib.request.urlretrieve(self.url[arch] + archive, archive)
                except:
                    print(f"Failed to download {archive}.")

        print(f"Finished downloads for {self.version}.")

    def build(self):
        """Building all the versions."""

        for arch in self.arch:
            if self.built[arch]:
                # Already built for arch or path not available. User has already been warned.
                continue

            # Preparation tasks
            self.appnamedir = os.path.join(self.builddir, self.appname)
            os.makedirs(self.appnamedir, exist_ok=True)
            # And then cd to the appname folder.
            os.chdir(self.appnamedir)
            # Download appimagetool from github
            appimagetoolurl = f"https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-{arch}.AppImage"
            urllib.request.urlretrieve(appimagetoolurl, 'appimagetool')
            os.chmod('appimagetool', 0o755)

            # Build the requested version.
            self.__unpackbuild__(arch)


    def __unpackbuild__(self, arch):
        # We start by filtering out tarballs from the list
        buildtarballs = [ self.tarballs[arch][0] ] 

        # Let's process standard languages and append results to the
        # buildtarball
        if self.language == 'basic':
            if self.offline_help:
                buildtarballs.extend([ x for x in self.tarballs[arch] if 'pack_en-GB' in x ])
            else:
                buildtarballs.extend([ x for x in self.tarballs[arch] if 'langpack_en-GB' in x])
        elif self.language == 'standard':
            for lang in Build.LANGSTD:
                if self.offline_help:
                    buildtarballs.extend([ x for x in self.tarballs[arch] if ('pack_' + lang) in x ])
                else:
                    buildtarballs.extend([ x for x in self.tarballs[arch] if ('langpack_' + lang) in x ])
        elif self.language == 'full':
            if self.offline_help:
                # We need also all help. Let's replace buildtarball with the
                # whole bunch
                buildtarballs = self.tarballs[arch]
            else:
                buildtarballs.extend([ x for x in self.tarballs[arch] if 'langpack' in x ])
        else:
            # Looping for each language in self.language
            for lang in self.language.split(","):
                if self.offline_help:
                    buildtarballs.extend([ x for x in self.tarballs[arch] if ('pack' + lang) in x ])
                else:
                    buildtarballs.extend([ x for x in self.tarballs[arch] if ('langpack' + lang) in x ])
                
        os.chdir(self.appnamedir)

        # Unpacking the tarballs
        for archive in buildtarballs:
            subprocess.run(shlex.split(f"tar xzf {self.download_path}/{archive}"))

        # create appimagedir
        self.appimagedir = os.path.join(self.builddir, self.appname, self.appname + '.AppDir')
        os.makedirs(self.appimagedir, exist_ok = True)

        # At this point, let's decompress the deb packages
        subprocess.run(shlex.split("find .. -iname '*.deb' -exec dpkg -x {} . \;"), cwd=self.appimagedir)

        if self.portable:
            subprocess.run(shlex.split("find . -type f -iname 'bootstraprc' -exec sed -i 's|^UserInstallation=.*|UserInstallation=\$SYSUSERCONFIG/libreoffice/%s|g' {} \+" % self.short_version), cwd=self.appimagedir)

        # Changing desktop file
        subprocess.run(shlex.split("find . -iname startcenter.desktop -exec cp {} . \;"), cwd=self.appimagedir)
        subprocess.run(shlex.split("sed --in-place 's:^Name=.*$:Name=%s:' startcenter.desktop > startcenter.desktop" % self.appname), cwd=self.appimagedir)

        subprocess.run(shlex.split("find . -name '*startcenter.png' -path '*hicolor*48x48*' -exec cp {} . \;"), cwd=self.appimagedir)

        # Find the name of the binary called in the desktop file.
        binaryname = ''
        with open(os.path.join(self.appimagedir, 'startcenter.desktop'), 'r') as d:
            a = d.readlines()
            for line in a:
                if re.match(r'^Exec', line):
                    binaryname = line.split('=')[-1].split(' ')[0]
                    # Esci al primo match
                    break
        #binary_exec = subprocess.run(shlex.split(r"awk 'BEGIN { FS = \"=\" } /^Exec/ { print $2; exit }' startcenter.desktop | awk '{ print $1 }'"), cwd=self.appimagedir, text=True, encoding='utf-8')
        #binaryname = binary_exec.stdout.strip("\n")

        bindir=os.path.join(self.appimagedir, 'usr', 'bin')
        os.makedirs(bindir, exist_ok = True)
        subprocess.run(shlex.split("find ../../opt -iname soffice -path '*program*' -exec ln -sf {} ./%s \;" % binaryname), cwd=bindir)

        # Download AppRun from github
        apprunurl = f"https://github.com/AppImage/AppImageKit/releases/download/continuous/AppRun-{arch}"
        dest = os.path.join(self.appimagedir, 'AppRun')
        urllib.request.urlretrieve(apprunurl, dest)
        os.chmod(dest, 0o755)

        # Dealing with extra options
        buildopts = []
        if self.sign:
            buildopts.append('--sign')

        # adding zsync build if updatable
        if self.updatable:
            buildopts.append(f"-u 'zsync|{self.zsyncfilename[arch]}'")

        buildopts_str = str.join(' ', buildopts)
        # Build the number-specific build
        subprocess.run(shlex.split(f"{self.appnamedir}/appimagetool {buildopts_str} -v ./{self.appname}.AppDir/"), env={ "VERSION": self.appversion })
        
        print(f"Built AppImage version {self.appversion}")

        # Cleanup phase, before new run.
        for deb in glob.glob(self.appnamedir + '/*.deb'):
            os.remove(deb)
        subprocess.run(shlex.split("find . -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} \+"))


    def checksums(self):
        """Create checksums of the built versions."""
        # Skip checksum if initally the build was already found in the storage directory
        if all(self.built.values()):
            return

        os.chdir(self.appnamedir)
        for arch in self.arch:
            for item in [ self.appimagefilename[arch], self.zsyncfilename[arch] ]:
                # For any built arch, find out if a file exist.
                self.__create_checksum__(item)


    def __create_checksum__(self, file):
        """Internal function to create checksum file."""
        checksum = subprocess.run(shlex.split(f"md5sum {file}"), capture_output=True, text=True, encoding='utf-8')
        if checksum.stdout:
            with open(f"{file}.md5", 'w') as c:
                c.write(checksum.stdout)

    def publish(self):
        """Moves built versions to definitive storage."""
        if all(self.built.values()):
            # All files are already present in the full_path
            return

        os.chdir(self.appnamedir)
        # Forcing creation of subfolders, in case there is a new build
        os.makedirs(self.full_path, exist_ok = True)
        for file in glob.glob("*.AppImage*"):
            subprocess.run(shlex.split(f"cp -f {file} {self.full_path}"))


    def generalize_and_link(self):
        """Creates the needed generalized files if needed."""
        # If called with a pointed version, no generalize and link necessary.
        if not self.branch_version:
            return

        # If a prerelease or a daily version, either.
        if self.query == 'daily' or self.query == 'prerelease':
            return

        appimagefilename = {}
        zsyncfilename = {}

        # Creating versions for short version and query text
        versions = [ self.short_version, self.branch_version ]
        for arch in Build.ARCHSTD:
            # If already built, do not do anything.
            if self.built[arch]:
                continue

            os.chdir(self.full_path)
            # if the appimage for the reported arch is not found, skip to next
            # arch
            if not os.path.exists(self.appimagefilename[arch]):
                continue

            # Doing it both for short_name and for branchname
            for version in versions:
                appimagefilename[arch] = self.appname + '-' + version + self.languagepart + self.helppart + f'-{arch}.AppImage'
                zsyncfilename[arch] = appimagefilename[arch] + '.zsync'

                # Create the symlink
                print(f"Creating {appimagefilename[arch]} and checksums.")
                if os.path.exists(appimagefilename[arch]):
                    os.unlink(appimagefilename[arch])
                os.symlink(self.appimagefilename[arch], appimagefilename[arch])
                # Create the checksum for the AppImage
                self.__create_checksum__(appimagefilename[arch])
                # Do not continue if no zsync file is provided.
                if not self.updatable:
                    continue

                print(f"Creating zsync file for version {version}.")
                if os.path.exists(zsyncfilename[arch]):
                    os.unlink(zsyncfilename[arch])
                shutil.copyfile(self.zsyncfilename[arch], zsyncfilename[arch])
                # Editing the zsyncfile
                subprocess.run(shlex.split(f"sed --in-place 's/^Filename:.*$/Filename: {appimagefilename[arch]}/' {zsyncfilename[arch]}"))
                self.__create_checksum__(zsyncfilename[arch])


    def __del__(self):
        """Destructor"""
        # Cleaning up build directory
        shutil.rmtree(self.builddir)
