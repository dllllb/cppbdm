# cppbdm

cppbdm is a prototype tool for C++ dependency management. It is inspired by BSD ports and Java dependency management tools like Apache Maven. The main idea is to download a source package, build it for the particular achitecture, and store haeaders and binareis in version-prefixed directory. Prebuilt packages are shared between projects. The tool has a set of commands to generate path locations for specific version of a library in order to set them for C/C++ compiler.

# Usage

## Add a new package for a project

    bdm.py require --name PACKAGE_NAME -- version PACKAGE_VERSION

## Get include paths for a package

    bdm.py includes --name PACKAGE_NAME -- version PACKAGE_VERSION
    
## Get lib paths for a package

    bdm.py libdirs --name PACKAGE_NAME -- version PACKAGE_VERSION
    
## Get binary paths for a package

    bdm.py bindirs --name PACKAGE_NAME -- version PACKAGE_VERSION
    
## Adding new package difinitions

Package definitions are stored in artifacts repository and are python scripts defining package download path and build instructions
