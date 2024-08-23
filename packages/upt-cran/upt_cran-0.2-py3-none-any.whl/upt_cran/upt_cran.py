# Copyright 2019-2024 Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import io
import logging
import re
import tarfile
import tempfile

import requests
import upt

LOG = logging.getLogger('upt')


class CranPackage(upt.Package):
    pass


class CranFrontend(upt.Frontend):
    name = 'cran'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__tarball_contents = {}

    def _fetch_url(self, url):
        # We might have to download the same tarball multiple times (for
        # instance, to get the DESCRIPTION file and then to get the LICENSE
        # file), so let's cache the result of the GET request. This works for
        # any URL, not just links to tarballs.
        try:
            return self.__tarball_contents[url]
        except KeyError:
            r = requests.get(url)
            if not r.ok:
                r.raise_for_status()
            self.__tarball_contents[url] = r.content
            return self.__tarball_contents[url]

    def _get_description_latest(self, pkg_name):
        '''Return the content of the DESCRIPTION file for pkg_name'''
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        r = requests.get(url)
        if not r.ok:
            raise upt.InvalidPackageNameError(self.name, pkg_name)
        return r.text

    def _get_description_version(self, pkg_name, version):
        '''Return the content of the DESCRIPTION file for pkg_name@version'''
        url = self._tarball_url(pkg_name, version, False)
        try:
            with tarfile.open(fileobj=io.BytesIO(self._fetch_url(url)),
                              mode='r:gz') as tarball:
                desc_file = tarball.extractfile(f'{pkg_name}/DESCRIPTION')
                return b''.join(desc_file.readlines()).decode()
        except requests.exceptions.HTTPError:
            raise upt.InvalidPackageVersionError(self.name, pkg_name, version)

    def _get_description(self, pkg_name, version=None):
        if version is None:
            description = self._get_description_latest(pkg_name)
            is_latest = True
        else:
            # CRAN does not store the current and old versions of a package in
            # the same place. This means that a user trying to package the
            # latest version of a package by being explicit about its version
            # (using pkgname@version on the command line, which is redundant
            # but supported) will cause upt-cran to look for the DESCRIPTION
            # file in the wrong location.
            # To work around this, if we fail to get the data we need from the
            # CRAN "archive", we try to get it from the "current" packages.
            try:
                description = self._get_description_version(pkg_name, version)
                is_latest = False
            except upt.InvalidPackageVersionError:
                description = self._get_description_latest(pkg_name)
                m = re.search(r'Version:\s*(?P<version>.*)', description)
                if m.group('version') != version:
                    raise upt.InvalidPackageVersionError(self.name, pkg_name,
                                                         version)
                is_latest = True
        return description, is_latest

    @staticmethod
    def _description_to_dict(description):
        '''Turn the package DESCRIPTION into a dictionary.

        The DESCRIPTION file attached to R packages contains key/value mappings
        in a text format. Multiline fields are allowed. Turning this file into
        a dictionary makes the mappings easier to read.
        '''
        description = re.sub(r'\n^[ \t\s]+', ' ', description,
                             flags=re.MULTILINE | re.DOTALL)
        desc_fields = {}
        for line in description.split('\n'):
            if line:
                k, v = line.split(':', maxsplit=1)
                desc_fields[k] = v.lstrip()
        return desc_fields

    @staticmethod
    def _tarball_url(pkg_name, version, latest=True):
        if latest:
            targz_url = 'https://cran.r-project.org/src/contrib/'
            targz_url += f'{pkg_name}_{version}.tar.gz'
        else:
            targz_url = 'https://cran.r-project.org/src/contrib/Archive/'
            targz_url += f'{pkg_name}/{pkg_name}_{version}.tar.gz'
        return targz_url

    @staticmethod
    def _cran_homepage(pkg_name):
        return f'https://cran.r-project.org/package={pkg_name}'

    @staticmethod
    def _get_requirements(depends, imports, suggests):
        '''Turn package dependencies into upt requirements.

        We only take the Depends, Imports and Suggests sections as input, and
        ignore the Enhances section, as the official documentation does not
        recommend using Enhances[1]

        [1]https://r-pkgs.org/description.html#sec-description-imports-suggests
        '''
        def _to_upt_reqs(requirements):
            upt_requirements = []
            for text_req in requirements:
                try:
                    pkg, specifier = text_req.strip().split(' ', 1)
                    specifier = specifier.strip('()')
                    specifier = specifier.replace(' ', '')
                except ValueError:
                    pkg, specifier = text_req.strip(), None
                # The language itself is often given as a dependency in the
                # "Depends" section. We skip it as it is not really a package
                # requirement.
                if pkg == 'R':
                    continue
                upt_requirements.append(upt.PackageRequirement(pkg, specifier))
            return upt_requirements

        # R does not define specific 'test' requirements. From the
        # documentation linked in this method's docstring:
        #
        # "Packages listed in Suggests are either needed for development tasks
        # or might unlock optional functionality for your users."
        #
        # So we only add to our runtime requirements the packages absolutely
        # needed, and bet that the suggested requirements are test
        # requirements.
        requirements = {}
        run_requirements = _to_upt_reqs(depends) + _to_upt_reqs(imports)
        test_requirements = _to_upt_reqs(suggests)
        if run_requirements:
            requirements['run'] = run_requirements
        if test_requirements:
            requirements['test'] = test_requirements
        return requirements

    def _get_licenses(self, license_field, tarball_url):
        # For more details on licenses in R, see:
        # https://cran.r-project.org/doc/manuals/r-release/R-exts.html#Licensing
        DEFAULT_LICENSE = upt.licenses.UnknownLicense
        r_to_upt = {
            # 'ACM':
            # 'AGPL':
            'AGPL (>= 3)':
                upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZeroPlus,
            'AGPL-3':
                upt.licenses.GNUAfferoGeneralPublicLicenseThreeDotZero,
            # 'Apache License':
            'Apache License (== 2)':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Apache License (>= 2)':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Apache License (== 2.0)':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Apache License (>= 2.0)':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Apache License 2.0':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Apache License Version 2.0':
                upt.licenses.ApacheLicenseTwoDotZero,
            'Artistic-2.0':
                upt.licenses.ArtisticLicenseTwoDotZero,
            'Artistic License 2.0':
                upt.licenses.ArtisticLicenseTwoDotZero,
            'BSD_2_clause':
                upt.licenses.BSDTwoClauseLicense,
            'BSD 2-clause License':
                upt.licenses.BSDTwoClauseLicense,
            'BSD_3_clause':
                upt.licenses.BSDThreeClauseLicense,
            'BSL':
                upt.licenses.BoostSoftwareLicense,
            'BSL-1.0':
                upt.licenses.BoostSoftwareLicense,
            'CC0':
                upt.licenses.CC0LicenceOneDotZero,
            # 'CC BY 4.0':
            # 'CC BY-NC 4.0':
            # 'CC BY-NC-SA 4.0':
            'CC BY-SA 4.0':
                upt.licenses.CCBYSAFourDotZero,
            # 'CeCILL':
            'CeCILL (>= 2)':
                upt.licenses.CeCILLTwoDotZero,
            'CeCILL-2':
                upt.licenses.CeCILLTwoDotZero,
            'CECILL-2.1':
                upt.licenses.CeCILLTwoDotOne,
            'Common Public License Version 1.0':
                upt.licenses.CommonPublicLicenseOneDotZero,
            'CPL-1.0':
                upt.licenses.CommonPublicLicenseOneDotZero,
            # 'CPL (>= 2)':
            # 'Creative Commons Attribution 4.0 International License':
            # 'EPL':
            # 'EUPL':
            'EUPL (>= 1.1)':
                upt.licenses.EuropeanUnionPublicLicenseOneDotOne,
            'EUPL-1.1':
                upt.licenses.EuropeanUnionPublicLicenseOneDotOne,
            'EUPL (>= 1.2)':
                upt.licenses.EuropeanUnionPublicLicenseOneDotTwo,
            'FreeBSD':
                upt.licenses.BSDTwoClauseLicense,
            # 'GNU General Public License':
            'GNU General Public License (>= 2)':
                upt.licenses.GNUGeneralPublicLicenseTwoPlus,
            'GNU General Public License (>= 3)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GNU General Public License version 2':
                upt.licenses.GNUGeneralPublicLicenseTwo,
            'GNU General Public License version 3':
                upt.licenses.GNUGeneralPublicLicenseThree,
            # 'GNU Lesser General Public License':
            # 'GPL':
            'GPL (<= 2)':
                upt.licenses.GNUGeneralPublicLicenseTwo,
            'GPL (== 2)':
                upt.licenses.GNUGeneralPublicLicenseTwo,
            'GPL (> 2)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 2)':
                upt.licenses.GNUGeneralPublicLicenseTwoPlus,
            'GPL-2':
                upt.licenses.GNUGeneralPublicLicenseTwo,
            'GPL (<= 2.0)':
                upt.licenses.GNUGeneralPublicLicenseTwo,
            'GPL (>= 2.0)':
                upt.licenses.GNUGeneralPublicLicenseTwoPlus,
            'GPL (>= 2.1)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 2.10)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 2.15.1)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (> 3)':
                upt.licenses.GNUGeneralPublicLicenseThree,
            'GPL (>= 3)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL-3':
                upt.licenses.GNUGeneralPublicLicenseThree,
            'GPL (== 3.0)':
                upt.licenses.GNUGeneralPublicLicenseThree,
            'GPL (>= 3.0)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 3.0.0)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 3.2)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 3.3.2)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            'GPL (>= 3.5.0)':
                upt.licenses.GNUGeneralPublicLicenseThreePlus,
            # 'LGPL':
            'LGPL (>= 2)':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotZeroPlus,
            'LGPL-2':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotZero,
            'LGPL (>= 2.0)':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotZeroPlus,
            'LGPL (>= 2.0, < 3)':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotZero,
            'LGPL (>= 2.1)':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotOnePlus,
            'LGPL-2.1':
                upt.licenses.GNULesserGeneralPublicLicenseTwoDotOne,
            'LGPL (>= 3)':
                upt.licenses.GNULesserGeneralPublicLicenseThreeDotZeroPlus,
            'LGPL-3':
                upt.licenses.GNULesserGeneralPublicLicenseThreeDotZero,
            'Lucent Public License':
                upt.licenses.LucentPublicLicenseOneDotZeroTwo,
            'MIT':
                upt.licenses.MITLicense,
            'MIT License':
                upt.licenses.MITLicense,
            # 'Mozilla Public License':
            'Mozilla Public License 1.1':
                upt.licenses.MozillaPublicLicenseOneDotOne,
            'Mozilla Public License 2.0':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            'Mozilla Public License Version 2.0':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            # 'MPL':
            'MPL-1.1':
                upt.licenses.MozillaPublicLicenseOneDotOne,
            'MPL (>= 2)':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            'MPL (== 2.0)':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            'MPL (>= 2.0)':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            'MPL-2.0':
                upt.licenses.MozillaPublicLicenseTwoDotZero,
            # 'Unlimited':
        }

        # We remove "+ file LICENSE" that is used to give additional terms to
        # the used license.
        license_field = re.sub(r'\+ file \w+', '', license_field)
        licenses = []
        for r_license in license_field.split('|'):
            r_license = r_license.strip()
            if r_license.startswith('file'):
                license_file = r_license.split()[1]
                c = self._fetch_url(tarball_url)
                with tarfile.open(fileobj=io.BytesIO(c),
                                  mode='r:gz') as tarball:
                    # First, let's figure out the full path of the license
                    # file, usually something like "pkgname/LICENSE".
                    for filename in tarball.getnames():
                        if filename.endswith(f'/{license_file}'):
                            break
                    else:
                        LOG.info(f'Could not find file "{license_file}" in '
                                 'the tarball. The package author should be '
                                 'told about this.')
                        continue
                    # Then, extract it to a file, because
                    # upt.licenses.guess_from_file wants to be given a file,
                    # and not a file handler or a string, unfortunately.
                    with tempfile.TemporaryDirectory() as d:
                        tarball.extract(filename, path=d, filter='data')
                        fullpath = f'{d}/{filename}'
                        license_ = upt.licenses.guess_from_file(fullpath)
            else:
                license_ = r_to_upt.get(r_license.strip(), DEFAULT_LICENSE)()
            licenses.append(license_)
        return licenses

    def parse(self, pkg_name, version=None):
        description, is_latest = self._get_description(pkg_name, version)
        desc_fields = self._description_to_dict(description)
        pkg_version = desc_fields.get('Version')
        targz_url = self._tarball_url(pkg_name, pkg_version, is_latest)

        # Weird list comprehension to filter out empty strings from the list.
        # Indeed, ''.split(',') returns [''].
        depends = [x for x in desc_fields.get('Depends', '').split(',') if x]
        imports = [x for x in desc_fields.get('Imports', '').split(',') if x]
        suggests = [x for x in desc_fields.get('Suggests', '').split(',') if x]
        d = {
            'homepage': desc_fields.get('URL', self._cran_homepage(pkg_name)),
            'summary': desc_fields.get('Title', ''),
            'description': desc_fields.get('Description', ''),
            'requirements': self._get_requirements(depends, imports, suggests),
            'archives': [upt.Archive(targz_url)],
            'licenses': self._get_licenses(desc_fields.get('License'),
                                           targz_url),
        }
        return CranPackage(pkg_name, pkg_version, **d)
