#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibpqConan(ConanFile):
    name = "libpq"
    version = "10.4"
    description = "The library used by all the standard PostgreSQL tools."
    topics = ("conan", "libpq", "postgresql", "database", "db")
    url = "https://github.com/zinnion/conan-libpq"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    author = "Zinnion <mauro@zinnion.com>"
    license = "PostgreSQL"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'with_zlib': True, 'with_openssl': True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = None
    _autotools = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.shared

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported yet.")
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11@zinnion/stable")
        if self.options.with_openssl:
            self.requires.add("OpenSSL/1.1.1b@zinnion/stable")

    def source(self):
        source_url = "https://ftp.postgresql.org/pub/source"
        sha256 = "60192bc75cd73e688500e8350ea065cca032e21abe57e72d4f556e0bf84fcf17"
        tools.get("{0}/v{1}/postgresql-{2}.tar.gz".format(source_url, self.version, self.version), sha256=sha256)
        extracted_dir = "postgresql-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._build_subfolder = os.path.join(self.build_folder, "output")
            args = ['--without-readline']
            args.append('--with-zlib' if self.options.with_zlib else '--without-zlib')
            args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            with tools.chdir(self._source_subfolder):
                self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
            autotools.make()
        with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
            autotools.make()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
            autotools.install()
        with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
            autotools.install()
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._build_subfolder, "include"))
        self.copy(pattern="postgres_ext.h", dst="include", src=os.path.join(self._source_subfolder, "src", "include"))
        self.copy(pattern="pg_config_ext.h", dst="include", src=os.path.join(self._source_subfolder, "src", "include"))
        if self.settings.os == "Linux":
            pattern = "*.so*" if self.options.shared else "*.a"
        elif self.settings.os == "Macos":
            pattern = "*.dylib" if self.options.shared else "*.a"
        elif self.settings.os == "Windows":
            pattern = "*.a"
            self.copy(pattern="*.dll", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
        self.copy(pattern=pattern, dst="lib", src=os.path.join(self._build_subfolder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
