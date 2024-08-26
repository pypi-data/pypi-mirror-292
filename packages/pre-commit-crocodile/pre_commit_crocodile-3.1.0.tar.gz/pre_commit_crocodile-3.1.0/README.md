# pre-commit-crocodile

<!-- markdownlint-disable no-inline-html -->

[![Build](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/badges/main/pipeline.svg)](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/-/commits/main/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pre-commit-crocodile&metric=bugs)](https://sonarcloud.io/dashboard?id=RadianDevCore_pre-commit-crocodile)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pre-commit-crocodile&metric=code_smells)](https://sonarcloud.io/dashboard?id=RadianDevCore_pre-commit-crocodile)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pre-commit-crocodile&metric=coverage)](https://sonarcloud.io/dashboard?id=RadianDevCore_pre-commit-crocodile)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pre-commit-crocodile&metric=ncloc)](https://sonarcloud.io/dashboard?id=RadianDevCore_pre-commit-crocodile)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_pre-commit-crocodile&metric=alert_status)](https://sonarcloud.io/dashboard?id=RadianDevCore_pre-commit-crocodile)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

Git hooks intended for developers using [pre-commit](https://pre-commit.com/) and [commitizen](https://commitizen-tools.github.io/commitizen/).

**Documentation:** <https://radiandevcore.gitlab.io/tools/pre-commit-crocodile>  
**Package:** <https://pypi.org/project/pre-commit-crocodile/>

---

## Features

**`pre-commit-crocodile` uses the following features:**

- **CLI - [pre-commit](https://pre-commit.com/):** Automated Git hooks before commits and upon pushes
- **CLI - [commitizen](https://commitizen-tools.github.io/commitizen/):** Commits tools and validation based upon [conventional commits](https://www.conventionalcommits.org/en/)
- **Hooks - [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks):** Common `pre-commit` hooks useful for developers
- **Hooks - `prepare-commit-msg`:** Prepare commit message automatically based on changes

---

## Preview

![preview.svg](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/raw/3.1.0/docs/preview.svg)

---

## Usage

<!-- prettier-ignore-start -->
<!-- readme-help-start -->

```yaml
usage: pre-commit-crocodile [-h] [--version] [--no-color] [--update-check] [--settings] [--set GROUP KEY VAL]
                            [-l | -i | -c | -e | -d | -a | -C | -r] [--config FOLDER | -D] [--stage STAGE] [--]

pre-commit-crocodile: Git hooks intended for developers using pre-commit

internal arguments:
  -h, --help           # Show this help message
  --version            # Show the current version
  --no-color           # Disable colors outputs with 'NO_COLOR=1'
                       # (or default settings: [themes] > no_color)
  --update-check       # Check for newer package updates
  --settings           # Show the current settings path and contents
  --set GROUP KEY VAL  # Set settings specific 'VAL' value to [GROUP] > KEY
                       # or unset by using 'UNSET' as 'VAL'

modes arguments:
  -l, --list           # List Git hooks installed in sources
  -i, --install        # Install dependencies for pre-commit hooks
  -c, --configure      # Update sources with hooks configurations
  -e, --enable         # Enable pre-commit hooks
  -d, --disable        # Disable pre-commit hooks
  -a, --autoupdate     # Autoupdate pre-commit hooks
  -C, --clean          # Clean pre-commit cached hooks
  -r, --run            # Run pre-commit hooks

configurations arguments:
  --config FOLDER      # Use configurations from a specific folder
  -D, --default        # Use global default configurations instead of sources
  --stage STAGE        # Run a specific pre-commit stage with --run
                       # (use 'list' to list supported stages)

positional arguments:
  --                   # Positional arguments separator (recommended)
```

<!-- readme-help-stop -->
<!-- prettier-ignore-end -->

---

## Installation

```bash
{
  # Option 1: If using pipx
  if type pipx >/dev/null 2>&1; then
    pipx ensurepath
    pipx install pre-commit-crocodile
    pipx upgrade pre-commit-crocodile

  # Option 2: If using pip
  else
    sudo pip3 install pre-commit-crocodile
  fi
}
```

---

## Compatibility

Projects compatible with `pre-commit-crocodile` can use this badge to ease things for developers, both as an indicator and a documentation shortcut button :

> [![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

```markdown title="Badge in Markdown"
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)
```

```html title="Badge in HTML"
<a href="https://radiandevcore.gitlab.io/tools/pre-commit-crocodile"><img src="https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab" alt="pre-commit-crocodile" style="max-width:100%;"></a>
```

---

## Projects without configurations | [![pre-commit](https://img.shields.io/badge/pre--commit-missing-gold)](https://github.com/pre-commit/pre-commit)

### Import configurations

```bash
pre-commit-crocodile --configure
```

---

## Projects with configurations | [![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

### Install dependencies

```bash
pre-commit-crocodile --install
```

### Enable hooks

```bash
pre-commit-crocodile --enable
```

### Run hooks

```bash
pre-commit-crocodile --run
```

### Update hooks

```bash
pre-commit-crocodile --autoupdate
```

### Disable hooks

```bash
pre-commit-crocodile --disable
```

### Cleanup hooks

```bash
pre-commit-crocodile --clean
```

---

## Dependencies

- [colored](https://pypi.org/project/colored/): Terminal colors and styles
- [commitizen](https://pypi.org/project/commitizen/): Simple commit conventions for internet citizens
- [pre-commit](https://pre-commit.com/): A framework for managing and maintaining pre-commit hooks
- [pre-commit-crocodile](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile): Git hooks intended for developers using pre-commit
- [setuptools](https://pypi.org/project/setuptools/): Build and manage Python packages
- [update-checker](https://pypi.org/project/update-checker/): Check for package updates on PyPI

---

## References

- [.gitlab-ci.yml](https://docs.gitlab.com/ee/ci/yaml/): GitLab CI/CD Pipeline Configuration Reference
- [conventionalcommits](https://www.conventionalcommits.org/en/v1.0.0/): Conventional Commits specification for commit messages
- [gcil](https://radiandevcore.gitlab.io/tools/gcil): Launch .gitlab-ci.yml jobs locally
- [git-cliff](https://github.com/orhun/git-cliff): CHANGELOG generator
- [gitlab-release](https://pypi.org/project/gitlab-release/): Utility for publishing on GitLab
- [mkdocs](https://www.mkdocs.org/): Project documentation with Markdown
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/): Material theme for mkdocs documentation
- [mypy](https://pypi.org/project/mypy/): Optional static typing for Python
- [pexpect-executor](https://radiandevcore.gitlab.io/tools/pexpect-executor): Automate interactive CLI tools actions
- [PyPI](https://pypi.org/): The Python Package Index
- [termtosvg](https://pypi.org/project/termtosvg/): Record terminal sessions as SVG animations
- [twine](https://pypi.org/project/twine/): Utility for publishing on PyPI
