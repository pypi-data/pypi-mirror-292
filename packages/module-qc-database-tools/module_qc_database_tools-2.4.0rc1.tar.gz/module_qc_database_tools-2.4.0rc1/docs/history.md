# module-qc-tools history

---

All notable changes to module-qc-tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [2.4.0](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-database-tools/-/tags/v2.4.0) - 2024-07-13 ## {: #mqt-v2.4.0 }

**_Changed:_**

- refactored some common code across the command-line interfaces

**_Added:_**

- ability to sync component stages recursively (!51)

## [2.3.0](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-database-tools/-/tags/v2.3.0) - 2024-07-13 ## {: #mqt-v2.3.0 }

First release for this documentation. (!47)

**_Changed:_**

- connectivity generation supports a `--dp`/`--port` option for specifying the
  DP Port (!42)

**_Added:_**

- command-line interface for fetching reference IVs (!46)
- support for ITkPix v2 (!39, !43)
- `ssl` option for mongo-client connections from command line (!37)

**_Fixed:_**

- bug in obtaining chip type from config when saving to localDB (!45)
