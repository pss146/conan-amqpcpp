import os
import shutil
from conans import ConanFile, CMake, tools

class AmqpcppConan(ConanFile):
    name = "amqpcpp"
    version = "4.1.6"
    url = "https://github.com/pss146/conan-amqpcpp"
    author = "stat.perepel@gmail.com"
    homepage = "https://github.com/CopernicaMarketingSoftware/AMQP-CPP"
    license = "Apache-2.0"
    description = "C++ library for asynchronous non-blocking communication with RabbitMQ"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    _source_subfolder = "source_subfolder"

    @property
    def majorver(self):
        return int(self.version.split('.')[0])

    def source(self):
        checksum = "48832068dc1e25a5313dd9e96fb33ba954c19f9dc04eeca8f7b2c6cecde3afc9"
        tools.get("https://github.com/CopernicaMarketingSoftware/AMQP-CPP/archive/v{}.tar.gz".format(self.version), sha256=checksum)
        os.rename("AMQP-CPP-" + self.version, self._source_subfolder)
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"), os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def requirements(self):
        self.requires.add("OpenSSL/1.1.1c@conan/stable")

    def build(self):
        cmake = CMake(self)
        cmake.definitions['AMQP-CPP_BUILD_SHARED'] = self.options.shared
        cmake.definitions['AMQP-CPP_BUILD_EXAMPLES'] = False
        cmake.definitions['AMQP-CPP_LINUX_TCP'] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        self.copy("license*", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("amqpcpp.h", dst="include", src=self._source_subfolder)
        if self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.defines.extend(["NOMINMAX"])  # Set NOMINMAX that min()/max() won't be overwritten by Windows.h macroses