# Copyright 2019-2024 Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import io
import tarfile
from unittest import mock
import unittest

import requests_mock

import upt
from upt_cran.upt_cran import CranFrontend

DESCRIPTION_PKG = '''Package: pkg
Version: 1.33.7
Title: Package
Description: A description
  on multiple
  lines.
Depends: R
Imports: foo,
  bar (>= 12)
Suggests: baz
Enhances: foobarbaz
License: BSD_3_clause
'''


def _fake_tarball(files):
    '''Return an io.BytesIO object representing a tarball.

    Takes a dictionary of filename:content mappings as argument.
    '''
    fh = io.BytesIO()
    with tarfile.open(fileobj=fh, mode='w:gz') as t:
        for filename, content in files.items():
            ti = tarfile.TarInfo(name=filename)
            ti.size = len(content)
            t.addfile(ti, fileobj=io.BytesIO(content))
    return fh


class TestCranFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = CranFrontend()

    def test__fetch_url(self):
        pkg_name = 'pkg'
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        with requests_mock.mock() as m:
            m.get(url, text=DESCRIPTION_PKG)
            out = self.frontend._fetch_url(url)
            expected = DESCRIPTION_PKG.encode()
            self.assertEqual(m.call_count, 1)
            self.assertEqual(out, expected)
            self.frontend._fetch_url(url)
            self.assertEqual(m.call_count, 1)
            self.assertEqual(out, expected)

    @requests_mock.mock()
    def test_get_description_with_valid_name(self, requests):
        '''The simplest use case: a valid package with no specific version.

        Here, the user is trying to package "pkg".
        '''
        pkg_name = 'pkg'
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        requests.get(url, text=DESCRIPTION_PKG)
        self.assertEqual((DESCRIPTION_PKG, True),
                         self.frontend._get_description(pkg_name))

    @requests_mock.mock()
    def test_get_description_with_valid_version(self, requests):
        '''A simple use case: a valid package with a valid version.

        Here, the user is trying to package "pkg@1.33.7"
        '''
        pkg_name = 'pkg'
        version = '1.33.7'
        url = 'https://cran.r-project.org/src/contrib/Archive/'
        url += f'{pkg_name}/{pkg_name}_{version}.tar.gz'

        fake_tarball = _fake_tarball({
            'pkg/DESCRIPTION': DESCRIPTION_PKG.encode(),
        })
        requests.get(url, content=fake_tarball.getvalue())
        self.assertEqual((DESCRIPTION_PKG, False),
                         self.frontend._get_description(pkg_name, version))

    @requests_mock.mock()
    def test_get_description_with_latest_version(self, requests):
        '''A not-so-simple use case: explicitely asking for the latest version.

        Here, the user is trying to package "pkg@1.33.7" which is the latest
        version. This is trickier than it seems: refer to the comments in
        upt_cran.py.
        '''
        pkg_name = 'pkg'
        version = '1.33.7'
        url = 'https://cran.r-project.org/src/contrib/Archive/'
        url += f'{pkg_name}/{pkg_name}_{version}.tar.gz'
        requests.get(url, status_code=404)
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        requests.get(url, text=DESCRIPTION_PKG)
        self.assertEqual((DESCRIPTION_PKG, True),
                         self.frontend._get_description(pkg_name, version))

    @requests_mock.mock()
    def test_get_description_invalid_package_name(self, requests):
        '''The simplest failure: an valid package with no specific version.

        Here, the user is trying to package "invalid".
        '''
        pkg_name = 'invalid'
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        requests.get(url, status_code=404)
        with self.assertRaises(upt.InvalidPackageNameError):
            self.frontend._get_description(pkg_name)

    @requests_mock.mock()
    def test_get_description_with_invalid_package_and_version(self, requests):
        '''A simple use case: an invalid package with a version.

        Here, the user is trying to package "invalid@42"
        '''
        pkg_name = 'invalid'
        version = '42'
        url = 'https://cran.r-project.org/src/contrib/Archive/'
        url += f'{pkg_name}/{pkg_name}_{version}.tar.gz'
        requests.get(url, status_code=404)
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        requests.get(url, status_code=404)
        with self.assertRaises(upt.InvalidPackageNameError):
            self.frontend._get_description(pkg_name, version)

    @requests_mock.mock()
    def test_get_description_with_invalid_version(self, requests):
        '''A simple use case: a valid package with an invalid version.

        Here, the user is trying to package "pkg@42"
        '''
        pkg_name = 'pkg'
        version = '1.33.8'
        url = 'https://cran.r-project.org/src/contrib/Archive/'
        url += f'{pkg_name}/{pkg_name}_{version}.tar.gz'
        requests.get(url, status_code=404)
        url = f'https://cran.r-project.org/web/packages/{pkg_name}/DESCRIPTION'
        requests.get(url, text=DESCRIPTION_PKG)
        with self.assertRaises(upt.InvalidPackageVersionError):
            self.frontend._get_description(pkg_name, version)

    def test__description_to_dict(self):
        expected = {
            'Package': 'pkg',
            'Version': '1.33.7',
            'Title': 'Package',
            'Description': 'A description on multiple lines.',
            'Depends': 'R',
            'Imports': 'foo, bar (>= 12)',
            'Suggests': 'baz',
            'Enhances': 'foobarbaz',
            'License': 'BSD_3_clause',
        }
        self.assertEqual(expected,
                         self.frontend._description_to_dict(DESCRIPTION_PKG))

    def test__cran_homepage(self):
        self.assertEqual('https://cran.r-project.org/package=pkg',
                         self.frontend._cran_homepage('pkg'))

    def test__get_licenses(self):
        self.assertEqual(
            self.frontend._get_licenses('GPL-2', 'http://'),
            [upt.licenses.GNUGeneralPublicLicenseTwo()]
        )
        self.assertEqual(
            self.frontend._get_licenses('GPL-2 + file LICENSE', 'http://'),
            [upt.licenses.GNUGeneralPublicLicenseTwo()]
        )
        self.assertEqual(
            self.frontend._get_licenses('GPL-2 | BSD_3_clause', 'http://'),
            [upt.licenses.GNUGeneralPublicLicenseTwo(),
             upt.licenses.BSDThreeClauseLicense()]
        )

        # We are supposed to read the LICENSE file, but it's not there :-(
        fake_tarball = _fake_tarball({
            'pkg/DESCRIPTION': DESCRIPTION_PKG.encode(),
        })
        with mock.patch.object(self.frontend, '_fetch_url') as m:
            m.return_value = fake_tarball.getvalue()
            out = self.frontend._get_licenses('file LICENSE', 'http://')
            expected = []
            self.assertEqual(out, expected)

        # We are supposed to read the LICENSE file, and it's there!
        fake_tarball = _fake_tarball({
            'pkg/LICENSE': b'This is a license!',
        })
        with (mock.patch.object(self.frontend, '_fetch_url') as m,
              mock.patch.object(upt.licenses, 'guess_from_file') as gff):
            m.return_value = fake_tarball.getvalue()
            gff.return_value = upt.licenses.BSDTwoClauseLicense()
            out = self.frontend._get_licenses('file LICENSE', 'http://')
            expected = [upt.licenses.BSDTwoClauseLicense()]
            self.assertEqual(out, expected)

    def test__tarball_url(self):
        url = 'https://cran.r-project.org/src/contrib/x_1.2.3.tar.gz'
        self.assertEqual(self.frontend._tarball_url('x', '1.2.3', True), url)
        url = 'https://cran.r-project.org/src/contrib/Archive/x/x_1.2.3.tar.gz'
        self.assertEqual(self.frontend._tarball_url('x', '1.2.3', False), url)

    def test__get_requirements(self):
        out = self.frontend._get_requirements([], [], [])
        expected = {}
        self.assertEqual(out, expected)

        out = self.frontend._get_requirements(['foo'], [], [])
        expected = {'run': [upt.PackageRequirement('foo', None)]}
        self.assertEqual(out, expected)

        out = self.frontend._get_requirements([], ['foo'], [])
        expected = {'run': [upt.PackageRequirement('foo', None)]}
        self.assertEqual(out, expected)

        out = self.frontend._get_requirements([], [], ['foo'])
        expected = {'test': [upt.PackageRequirement('foo', None)]}
        self.assertEqual(out, expected)

        # Multiple requirements in the same group
        out = self.frontend._get_requirements([], [], ['foo', 'bar (>= 12)'])
        expected = {
            'test': [
                upt.PackageRequirement('foo', None),
                upt.PackageRequirement('bar', '>=12'),
            ]
        }
        self.assertEqual(out, expected)

        # With specifiers
        out = self.frontend._get_requirements([], [], ['foo (>= 1.2)'])
        expected = {'test': [upt.PackageRequirement('foo', '>=1.2')]}
        self.assertEqual(out, expected)

        # We ignore the language itself
        out = self.frontend._get_requirements(['R'], [], [])
        expected = {}
        self.assertEqual(out, expected)

    @requests_mock.mock()
    def test_parse(self, requests):
        url = 'https://cran.r-project.org/web/packages/pkg/DESCRIPTION'
        requests.get(url, text=DESCRIPTION_PKG)
        targz_url = 'https://cran.r-project.org/src/contrib/pkg_1.33.7.tar.gz'
        out = self.frontend.parse('pkg')
        self.assertEqual(out.name, 'pkg')
        self.assertEqual(out.version, '1.33.7')
        self.assertEqual(out.homepage,
                         'https://cran.r-project.org/package=pkg')
        self.assertEqual(out.summary, 'Package')
        self.assertEqual(out.description, 'A description on multiple lines.')

        self.assertDictEqual(out.requirements, {
                'run': [
                    upt.PackageRequirement('foo'),
                    upt.PackageRequirement('bar', '>=12'),
                ],
                'test': [
                    upt.PackageRequirement('baz')
                ],
            }
        )
        self.assertEqual(len(out.archives), 1)
        self.assertEqual(out.archives[0].url, targz_url)
        self.assertEqual(out.licenses, [upt.licenses.BSDThreeClauseLicense()])
