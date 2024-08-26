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

---

## Using pre-commit-crocodile hooks

```yaml title="Sources / .pre-commit-config.yaml"
# pre-commit configurations
default_install_hook_types:
  - prepare-commit-msg
  - pre-commit
  - pre-push
default_stages:
  - prepare-commit-msg
  - pre-commit
  - pre-push
minimum_pre_commit_version: 3.8.0

# pre-commit repositories
repos:

  # Repository: pre-commit-crocodile
  - repo: https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile
    rev: X.Y.Z # Adapt to latest release tag
    hooks:
      - id: ...
```

---

### `prepare-commit-message` - Prepare commit message automatically

```yaml title="Sources / .pre-commit-config.yaml"
  # Repository: pre-commit-crocodile
  - repo: ...
    ...
    hooks:
      - id: prepare-commit-message
```

**Automatically prepare the commit message based on changed sources before manual edition :**

- **Launched automatically by Git** upon `prepare-commit-msg` stage using `pre-commit`
- Parse `Changes to be committed:` **to automatically prepare a `type(scope): ...` title**
- Commit messages implementation derived from **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specifications**
- **Automatically detect and prepare templates like `ci(gitlab-ci):`, `docs(readme):`, `build(makefile):` or `docs(changelog):`**
- **Automatically evaluate sources specific scopes, for example files or folders under `src/`, or recipe folders in Yocto `recipes-.../` sources**
- Message body is automatically inserted to help developers document their commits or link to a related issue
- Commits with sign-off messages automatically receive a `---` separator for readability on GitLab
