#!/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import json
import shutil
from pathlib import Path

CWD = os.path.dirname(__file__)
HOME = os.getenv('HOME')
VCPKG_ROOT = os.path.join(HOME, "vcpkg")

NAME = "native-libs"
VERSION = "1.0.0"
minSdkVersion = 25
targetSdkVersion = 31
ndkVersion = 25
STL = 'c++_static'


def write_prefab_json(modules_dir: Path):
    prefab_json = modules_dir.parent / 'prefab.json'
    with open(prefab_json, "w+") as fp:
        json.dump({
            "name": NAME,
            "schema_version": 1,
            "dependencies": [],
            "version": VERSION
        }, fp, indent=2)

    print(">>> write", os.path.relpath(prefab_json, CWD))


def write_androidmanifest_xml(modules_dir: Path):
    androidmanifest_xml = modules_dir.parent.parent / 'AndroidManifest.xml'
    with open(androidmanifest_xml, 'w+') as fp:
        fp.writelines([
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n',
            '          package="com.vcpkg.ndk.support.nativelibs"\n',
	    '          android:versionCode="1"\n',
	    '          android:versionName="1.0">\n',
           f'    <uses-sdk android:minSdkVersion="{minSdkVersion}"\n',
	   f'              android:targetSdkVersion="{targetSdkVersion}" />\n',
            '</manifest>'
        ])

    print(">>> write", os.path.relpath(androidmanifest_xml, CWD))


def write_module_json(module_dir: Path):
    module_json = module_dir / 'module.json'
    with open(module_json, 'w+') as fp:
        json.dump({
	    "export_libraries": [],
	    "library_name": None,
	    "android": {
		"export_libraries": None,
		"library_name": None
            }
        }, fp, indent=2)

    print(">>> write", os.path.relpath(module_json, CWD))


def write_abi_json(module_dir: Path, abi: str):
    abi_json = module_dir / 'libs' / f'android.{abi}' / 'abi.json'
    with open(abi_json, 'w+') as fp:
        json.dump({
	    "abi": abi,
	    "api": minSdkVersion,
	    "ndk": ndkVersion,
	    "stl": STL
        }, fp, indent=2)

    print(">>> write", os.path.relpath(abi_json, CWD))


def copy_module_files(modules_dir: Path, package_name: str, module_name: str, copy_include_dir=True):
    arch_to_abi = {
        'arm': 'armeabi-v7a',
        'arm64': 'arm64-v8a',
        'x86': 'x86',
        'x64': 'x86_64',
    }

    module_dir = modules_dir / module_name
    packages_dir = Path(VCPKG_ROOT) / 'packages'

    for arch, abi in arch_to_abi.items():
        os.makedirs(module_dir / 'libs' / f'android.{abi}', exist_ok=True)
        dst_dir = module_dir / 'libs' / f'android.{abi}'
        if copy_include_dir:
            src = packages_dir / f'{package_name}_{arch}-android' / 'include'
            shutil.copytree(src, dst_dir, dirs_exist_ok=True)

        lib_dir = packages_dir / f'{package_name}_{arch}-android' / 'lib'
        for lib in os.listdir(lib_dir):
            if re.match(f'lib{module_name}.(a|so)', lib):
                src = lib_dir / lib
                # dst = dst_dir / lib
                shutil.copy2(src, dst_dir)

        write_abi_json(module_dir, abi)

    print(f">>> copy module {module_name} files from package {package_name}")
    write_module_json(module_dir)


# script part
prefab_dir = Path(CWD) / 'prefab' / NAME
if prefab_dir.exists():
    shutil.rmtree(prefab_dir) 

modules_dir = prefab_dir / 'prefab' / 'modules'
os.makedirs(modules_dir)

write_prefab_json(modules_dir)
write_androidmanifest_xml(modules_dir)
copy_module_files(modules_dir, 'bzip2', 'bz2')
copy_module_files(modules_dir, 'libffi', 'ffi')
copy_module_files(modules_dir, 'libuuid', 'uuid')
copy_module_files(modules_dir, 'sqlite3', 'sqlite3')
copy_module_files(modules_dir, 'openssl', 'ssl')
copy_module_files(modules_dir, 'openssl', 'crypto', copy_include_dir=False)
copy_module_files(modules_dir, 'python3', 'python3.10')

with os.popen(f"cd {prefab_dir} && zip -r -q ../{NAME}-{VERSION}.aar .") as fp:
    pass

print(f">>> aar file {NAME}-{VERSION}.aar created in {os.path.relpath(prefab_dir, CWD)}")

