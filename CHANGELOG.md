# Changelog

## [Unreleased]

### Added

### Changed

### Fixed

- Fixed bugs in segmenter module.

## [4.1.0] - 2021-04-14

### Added

- New preload functionality for preloading annotators to speed up annotation process.
- Added verbose mode for progress bar, showing all concurrently running tasks (by using the `-v` flag, mainly usable
  together with the `-j` flag for multiprocessing).
- Ability to limit the number of parallel processes used by specific annotators.
- Source document names are now shown in error messages.
- Added exporter configuration to wizard.
- Added several new configuration options for Stanza, and helpful error message to help mitigate memory problems.
- An error message is now displayed when attempting to run annotations without input files.
- Added new command (`languages`) to show a list of supported languages.
- You can now refer to models outside the Sparv data dir.
- Added importers section to `sparv run-rule --list`.
- Class values inferred from annotation usage is now shown when running `sparv classes`.
- Dry-running (`sparv run -n`) now shows a summary of tasks.

### Changed

- Improved progress bar. Shows number of tasks completed and left, instead of estimated time (which wasn't very
  helpful).
- Slightly quicker startup time.
- Malt and Stanza no longer perform dependency parsing on tokens not belonging to any sentences.
- The `build-models` command no longer builds all models by default unless the `--all` flag is used.
- Regular annotators used as `custom_annotations` are now configured using `config` instead of `params`.
- Updated and improved documentation.

### Fixed

- Fixed broken combined XML export.
- Fixed several problems with the Stanza module.
- MySQL tables now support all unicode characters (by using the utf8mb4 charset).
- Fixed support for retaining existing segments in segment module.
- Fixed crash in SALDO module due to orphaned tokens.
- Fixed unicode normalization in XML import module.
- Removed broken unused models from `build-models`.
- Fixed YAML syntax highlighting which was unreadable in some terminals.
- Fixed rare TreeTagger crash.
- Fixed some bugs in Stanford module.

## [4.0.0] - 2020-12-07

- This version contains a complete make-over of the Sparv Pipeline!
  - Everything is written in Python now (no more Makefiles or bash code).
  - Increased platform independence
  - This facilitates creating new modules, debugging, and maintenance.

- Easier installation process, Sparv is now on PyPI!
  - New plugin system facilitates installation of Sparv plugins (like FreeLing).

- New format for corpus config files
  - The new format is yaml which is easier to write and more human readable than makefiles.
  - There is a command-line wizard which helps you create corpus config files.
  - You no longer have to specify XML elements and attributes that should be kept from the original files. The  XML
    parser now parses all existing elements and their attributes by default. Their original names will be kept and
    included in the export (unless you explicitly override this behaviour in the corpus config).

- Improved interface
  - New command line interface with help messages
  - Better feedback with progress bar instead of illegible log output (log output is still available though)
  - More helpful error messages

- New corpus import and export formats
  - Import of plain text files
  - Export to csv (a user-friendly, non-technical column format)
  - Export to (Språkbanken Text version of) CoNNL-U format
  - Export to corpus statistics (word frequency lists)

- Updated models and tools for processing Swedish corpora
  - Sparv now uses Stanza with newly trained models and higher accuracy for POS-tagging and dependency parsing on
    Swedish texts.

- Better support for annotating other (i.e. non-Swedish) languages
  - Integrated Stanford Parser for English analysis (POS-tags, baseforms, dependency parsing, named-entity recognition).
  - Added named-entity recognition for FreeLing languages.
  - If a language is supported by multiple annotation tools, you can now choose which tool to use.

- Improved code modularity
  - Increased independence between modules and language models
  - This facilitates adding new annotation modules and import/export formats.
