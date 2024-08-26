# Changelog

<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/3.0.0...3.1.0) (2024-08-25)

### ✨ Features

- **cli:** implement '--stage STAGE' for '--run' to specify stage ([9ef3d2a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9ef3d2ac4c9017ca247595da41a7cd9e5f998bd7))
- **configurations:** implement matcher for 'sonar-project.properties' ([b9627a6](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b9627a653a5336e3b1483894bd7a3c0c9b71c514))
- **gcil:** inject 'gcil' badge automatically if configured or installed ([6cfe076](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6cfe07681fe0ac7e8ac35d4c95da4bc36a8f045f))
- **gcil:** implement automatic 'run-gcil-push' hooks with whitelist ([56e9e6c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/56e9e6ca4c46e11eb86479127a98042e9a039693))
- **main:** add '-D' as short flag for '--default' long flag ([6515c29](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6515c295868477d4bb3f88111b67fbf1d157ae5d))
- **pre-commit:** add 'pygrep-hooks' hooks to 'pre-commit' template ([8813f81](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8813f8119c88c39a62834fcf1f5a0b8fe74211aa))

### 🐛 Bug Fixes

- **features:** enforce 'Commands' conditional arguments syntax ([142108f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/142108f37896f9523e43144f3433092b1b4b5952))

### 📚 Documentation

- **cliff:** improve 'Unreleased' and refactor to 'Development' ([abaf0c9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/abaf0c9c11ac9e1e5bbf37fa3d5fe99f9290e436))
- **mkdocs, prepare:** resolve Markdown support in hidden '<details>' ([d647166](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d647166f68fcccd2ab7ec1c3717622fa365a8bd8))
- **prepare:** regenerate development 'CHANGELOG' with 'git-cliff' ([0cc6cc7](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0cc6cc7995c56d91b1fb1eb7f9f63c35ce7c3609))
- **readme:** link against 'gcil' and 'pexpect-executor' documentation pages ([3044355](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/304435558aeab4e9792b4029c8a9d9b26ef54771))
- **readme:** add 'gcil:enabled' documentation badge ([f06542b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f06542bac9d87e6844171cca4d4c96f9182ff91f))

### ⚙️ Cleanups

- **sonar:** wait for SonarCloud Quality Gate status ([f48b69e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f48b69efeb94f034b3fbf84dfaeebb35dfc0e6ea))

### 🚀 CI

- **gitlab-ci:** prevent 'sonarcloud' job launch upon 'gcil' local use ([8ba9700](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8ba97001ad13c6feb40e02dfac391c1169740f0f))
- **gitlab-ci:** run SonarCloud analysis on merge request pipelines ([0f34e2d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0f34e2da8dfff5e7eb27a987dd02ffcc2c7aa3f6))
- **gitlab-ci:** watch for 'config/*' changes in 'serve' job ([c47e433](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c47e4339fc6f321debce26c57dd265fea51eb3f8))
- **gitlab-ci:** fetch Git tags history in 'pages' job execution ([c4c8b71](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c4c8b71f55198eae1e273cd00e81df94a87c15f9))
- **gitlab-ci:** fetch with '--unshallow' for full history in 'pages' ([cd6d65e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cd6d65e3f82b61afc7d56aadec907bf1489e688a))

### 📦 Build

- **containers:** use 'apk add --no-cache' for lighter images ([d13b26a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d13b26a2bc88327bebfad60e635604ac786c9f4a))
- **pages:** add 'git-cliff' to the ':pages' image ([26f26c6](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/26f26c6f0b06e3835a5d553eb5342d2ba5ec94da))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/2.1.0...3.0.0) (2024-08-25)

### ✨ Features

- **cli:** implement '--config FOLDER' and '--default' configurations ([081fd94](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/081fd94afd0d89ef2ac3ca23c68858c53df1216d))
- **cli:** implement '--clean' to run 'pre-commit clean' cache cleanups ([b971337](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b9713370b85e610aa724c2f45322c50dc461227d))
- **entrypoint:** configure unused hooks upon '--default' use ([a271c43](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/a271c431988f116a57f5fa375eb1bf8cf4dbbc89))
- **entrypoint:** inject badge in 'README.md' upon '--configure' ([739774d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/739774d6b44f7cd5ce3b45738758215e74152f69))
- **entrypoint:** add 'README.md' to '--configure' commmands hint ([8d7ddcc](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8d7ddccf2b530ad02c92a0a29b0894f37e8154df))
- **entrypoint:** migrate to commitizen '3.29.0+adriandc.20240825' ([9c6f378](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9c6f37849e17f3ccd2baf302789045ed16424e86))
- **entrypoint:** allow newer commitizen versions usage ([138ef35](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/138ef3533a03ceb0b5a6a7a7568795efd717e975))
- **entrypoint, features:** refactor into static features classes ([9b85378](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9b85378eb831690fe83550dbea5b9575e1f04fa7))
- **🚨 BREAKING CHANGE 🚨 |** **main:** avoid running '--run' features upon '--enable' ([1c9134d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1c9134d152c69fbe34192461f62f1522e32bac21))
- **prepare_commit_message:** inject signoff if commitizen 'always_signoff' ([f402004](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f402004cde6c84a6bc8857fd6cd6ddcd0618d0a0))
- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([1205341](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1205341bc1b7d7f96dfb8830b32c8853a96a31de))

### 🐛 Bug Fixes

- **entrypoint:** resolve unused hooks issues with '--default' ([9dc8309](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9dc8309dc8c2ff819d7ffe8fc0f7b46f1e52e438))
- **entrypoint:** remove 'README.md' debugging log in '--configure' ([71ceb42](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/71ceb42808eaabf64998a79624a3be0a7995e29c))
- **precommit:** resolve '--default' use with existing configuration ([7543149](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/7543149382f5280b074a24b1dbd403821810e36e))
- **templates:** migrate to 'run-gcil-*' skipped hooks names ([63df3c3](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/63df3c36819540f119f82c1a37e7848078580e13))

### 📚 Documentation

- **readme:** add badge compatibility and syntax documentation ([9de0ad9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9de0ad97fdadf6cccd958b425ab5aafda1c02b38))
- **readme:** add 'mkdocs' and 'mkdocs-material' references ([f9eac20](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f9eac20e5db2c7b383462930c9b1ca194da07af7))
- **requirements:** install 'types-PyYAML>=6.0.12.2' as quality dependency ([4d09100](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4d0910084d1392467dbca5298c01bcab7befaec8))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([4342bea](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4342bea56efb8e9c45bcaa7372770cc0c240ae44))
- **entrypoint:** constantify '{PACKAGE_REVISION}' template string ([8a77371](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8a77371e9f476293941e27748817b4a858cb6e9a))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([31738fe](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/31738fe68508926ed433190d870d7aea4c9464a5))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([001b11d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/001b11d840056d2a0a30faabac2e246f450163dd))
- **pre-commit:** add 'additional_dependencies' for missing YAML ([9c80622](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9c806225083194d7d4e21de7b49fcefe38b53bfd))
- **pre-commit:** improve syntax for 'args' arguments ([0d7e947](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0d7e9476f5bf41c56ca699c4339a74900fa073c8))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([8e0f5cf](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8e0f5cfcee7db56b2dff830401e97ce8b6a70f86))
- **pre-commit:** update against 'run-gcil-push' hook template ([cb69d0b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cb69d0bbe2b1ca9f0338e005ec1447577355f856))
- **pre-commit:** add missing 'commit-msg' stage for commitizen ([a27b9dd](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/a27b9dd23b33a0fbd99164a386d01485cc5b51c0))

### 📦 Build

- **requirements:** add 'PyYAML>=6.0' as runtime dependency ([2fe8d58](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2fe8d58e586daa760d8d062368cdfe33028cddc4))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/2.0.2...2.1.0) (2024-08-24)

### ✨ Features

- **entrypoint:** use 'pre-commit install --allow-missing-config' ([d41b2f3](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d41b2f39d024ba14dde024ae021649b991631a0d))
- **entrypoint:** use 'pre-commit run --all-files' parameter syntax ([956cb33](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/956cb333028e61d2e1e14b5971d233f4882d069a))
- **pre-commit:** exclude '.patch' Git patch files from hooks ([e865955](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e865955cc09781725dc0aa88314506b951ce3350))
- **pre-commit:** disable 'detect-private-key' by default ([5ef6060](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5ef6060fba92d46fde84530ccb08a271d50d2c94))
- **pre-commit-config:** exclude 'eicar.*' Anti Malware Testfile ([6dbdb7c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6dbdb7c5c7727788ffd9974e8dc0dee8c9c0c467))

### 🐛 Bug Fixes

- **pre-commit:** fix 'destroyed-symlinks' v4.6.0 missing stages ([5377b8f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5377b8fc5349301a8c10cb24edf3e6d511626ddb))
- **templates/commits:** avoid failing without 'local-gcil-*' hooks ([1d9dc15](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1d9dc15b5fa3310251b35ab5f7f24398b2cfff93))

### 📚 Documentation

- **components:** add GitLab CI/CD Catalog for components URL ([47068c6](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/47068c6bce3758119db692ff74d0de9370ae199c))
- **hooks:** fix hooks 'repo:' URL for '.pre-commit-config.yaml' ([b7c059e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b7c059ef2a72d307c629231606e836ade5564ec5))
- **hooks:** improve hook '.pre-commit-config.yaml' documentation ([7a3c283](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/7a3c283ffb7c60bcdb9f9909c8b9194755982cfe))
- **prepare:** fix 'Commit type' list faulty indentation issue ([42f49cb](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/42f49cb494c206752723df29996012ca4935e742))

### ⚙️ Cleanups

- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([1fcb35c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1fcb35c0224b31a0641f138c784ca59a53da75b5))

### 🚀 CI

- **gitlab-ci:** improve 'serve' job syntax for YAML rendering ([aa41a7e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/aa41a7e3544e40ede01733a83a9b9b936a8747e0))
- **gitlab-ci:** cleanup cache upon 'serve' job end ([4574326](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/45743265d47b41929cebda731b444857feba9e14))
- **gitlab-ci:** ignore 'serve' job failure due to 'Ctrl+C' end ([c8718b5](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c8718b5257069ab7e5410bea086aecece90a39a3))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([6660428](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/666042865a99dd49fd092abc13e06f3de039b887))


<a name="2.0.2"></a>
## [2.0.2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/2.0.1...2.0.2) (2024-08-22)

### 📚 Documentation

- **components, hooks:** add file name headers for sources changes ([77cfb9b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/77cfb9b4dc249e70811afc1161d4fefd170877e4))
- **prepare:** bind 'preview.svg' image as a webpage asset ([2e214bd](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2e214bdb63459c4265b035a6d86fe2e0ef69c1ef))
- **preview:** add 'clear' calls before 'git add' sections ([8dd763c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8dd763c308e2319ea48c771fcb0abebdaa58f591))
- **preview:** fix SVG preview for version 2.0.1 ([1d34359](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1d34359768b881efd1a6ee3a0ec9a17f9fac17be))
- **readme:** remove '{ ... }' wrappers for single commands ([dd892d8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/dd892d8233f304b4b24cf3475f6c24f2a1e1ce5d))
- **readme:** simplify and cleanup commands documentation ([d2d3b38](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d2d3b38a87780524bcd56a41ca52b8276f633553))

### 🚀 CI

- **gitlab-ci:** create 'hooks' local job for maintenance ([df35dc9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/df35dc992f811dbd35981d59643c7d20b51d20c0))
- **gitlab-ci:** prepare and remove '.cache' even upon failures ([f56f38e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f56f38e29e33877871ce1cc538e569374e1fa349))
- **gitlab-ci:** use 'origin/develop' as hooks revision for 'preview' ([9c0c29c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9c0c29c353297c8ec21329ea3dfec3b1187c708a))


<a name="2.0.1"></a>
## [2.0.1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/2.0.0...2.0.1) (2024-08-21)

### ✨ Features

- **commitizen:** refactor commits documentation and improve markdown ([10d1da9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/10d1da9cf8e6a957a63ab820b4aa36235130db37))

### 📚 Documentation

- **docs:** add 'commitizen' to the project main description ([effba2f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/effba2fa32ad96e3373332fc143240eab36308c6))
- **docs:** embed files directly using 'mkdocs' syntax '--8<-- "..."' ([a51755e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/a51755e1db63ea04d23d2f77af53f053687707fa))
- **docs:** improve headers with links for configurations files ([565c92f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/565c92f6151201c3bde104619f8c9f36442092ad))
- **preview:** refresh SVG preview for version 2.0.1 ([50621dc](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/50621dc1eb74c6382d9865f02e4819f83b6a3b26))
- **readme:** add 'Package' link in the 'README' documentation ([6238b85](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6238b85d63fac17cd658c89c7af92def065f6a43))

### 🚀 CI

- **gitlab-ci:** watch for '.cz.yaml' in 'serve' job ([e1f8319](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e1f8319c6cb4b5530f9bd24bc08f4bf4e54216d6))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/1.1.0...2.0.0) (2024-08-21)

### ✨ Features

- **cli:** refactor 'manage' tool into 'pre-commit-crocodile' entrypoint ([fcd6a33](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/fcd6a33aa3dc87c070415e259e6da544a663eaad))
- **cli:** run requested mode only and not related modes too ([4aef5dd](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4aef5dd4381ebaa0b5e5ecb06c040c7c1e8fec08))
- **cli:** implement '--list' mode to list installed hooks ([72bc197](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/72bc1978900f9aa8920927e3065b7109339abf92))
- **configurations:** add 'mkdocs' detection and isolate 'docs/' ([3d8f988](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3d8f98867c86efa6d71da44cd8c10950e48fb599))
- **configurations:** refactor 'docs/' and 'test[s]?/' into evaluators ([f0e880c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f0e880cf87f9961710940ce44469b0a32e0d8062))
- **configurations:** catch 'recipes-*/(...)' Yocto recipe as fallback ([ee8d4c2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ee8d4c20264ffb3c0d5021a70797bff31b23d781))
- **configurations:** evaluate 'containers/' changes for commits ([1078898](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/10788981f8c41940bb5820022780dec969f14ba5))
- **configurations:** add evaluator for 'templates/' as 'ci' commit ([e818b59](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e818b59e4c1c6353eb411dfcc584e75aade95195))
- **entrypoint:** configure '.pre-commit-config.yaml' with revision ([db6f0f8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/db6f0f84c10333dc7a4197944d330efd81c6cf29))
- **entrypoint:** list detected Git remote upon 'git remote set-head' ([4b91a48](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4b91a4898009d8a50323a617fa7cd55e0e7d220e))
- **entrypoint:** add commit instructions for '--configure' mode ([750d69b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/750d69b7e82b87f47005cf0af0894d382de72806))
- **entrypoint:** automatically resolve 'check-hooks-apply' errors ([69852d1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/69852d159be15f8be3944fd8eae18ddd3b227238))
- **hooks:** comment 'Issue: #...' template by default ([bdf466f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/bdf466f0412fa7b88f42d8ef5e80a8434e139c13))
- **main:** set '--configure' as 'Edit sources with hooks configurations' ([ff16952](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ff16952901c9d6f59571fac99df34de09a7d2944))
- **main:** avoid '--autoupdate' features upon '--enable' mode ([c715b6a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c715b6a0bc2565580a9cf2094b54bef538a7962b))
- **main:** enable '--enable' features upon '--autoupdate' mode ([2e5464b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2e5464b92d04ee70dc233b6f862408e82504339b))
- **mkdocs, gitlab-ci:** implement GitLab Pages with 'mkdocs' ([76b963a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/76b963a65c898b490b3c639d61a84a860fd45456))
- **package:** add 'DEBUG_REVISION_SHA' to force package revision ([372c7c0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/372c7c09313bf418b47ec078cc56f4804a710c46))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.8 due to 'importlib.resources' ([0e2772f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0e2772f0827568693c796f990c8881e900c22a52))
- **src:** import package, prints, system and types from 'gcil' ([f30ec12](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f30ec121b3584b0e311a511a2b12cd3927405e35))
- **version:** create 'Version.revision' API to get tag or SHA1 revision ([6d28e45](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6d28e45d2367a789f1ffbf45d01ba157d07f5f86))

### 🐛 Bug Fixes

- **cli, assets:** implement '--configure' to deploy configurations ([e64a0a8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e64a0a83ace8c121580bd47806bf3f0c71ffa78e))
- **configurations:** detect 'requirements/' changes for commit messages ([06d0243](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/06d0243d5c043a36c566916d60575d778b445696))
- **configurations:** make folder and file name regexes non-greedy ([356001f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/356001f53d2221bde08d0136e6fbdcd49ee715c6))
- **entrypoint:** uninstall Python packages only if installed first ([ed6291f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ed6291f52fa6d33625c1cf4efa713072a55235da))
- **entrypoint:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([fe44ab8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/fe44ab8f12ef324269e9c4a7dec37ffd39fc2576))
- **entrypoint:** update Git remote upon '--enable' instead of '--autoupdate' ([e3f9ead](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e3f9eadf2d8c0d4d625c22e405b80482fbc4cc97))
- **entrypoint:** pre-stage '.pre-commit-config.yaml' for hooks checks ([a3bcfc9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/a3bcfc903e1780a1e72719f1150c0a33208359fc))
- **entrypoint:** resolve Python 3.8 support of f-string with quotes ([6f127a7](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6f127a7a3fd2f91ccdf4018b9e378a5a43a0e0d9))
- **entrypoint:** fix Python <3.11 without 'importlib.resources.abc' ([0708445](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/07084454c7665275355b0321c54bd52457f5e54a))
- **hooks:** use '\n' as commit message lines separator ([8abf039](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8abf03901691a502456528632bb421d6082694c7))
- **main:** align help position limit to 23 chars ([db766b8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/db766b89f99d56657136c71622bc2722bf9716f1))
- **main:** merge and refactor modes validation (python:S108) ([5f76347](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5f76347623a546d20eeae97268183b3a431c8d4b))
- **platform:** always flush on Windows hosts without stdout TTY ([3848f85](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3848f85860243ebdf97620a9444f58b433796b00))
- **pre-commit-config:** enable all 'pre-commit-hooks' hooks by default ([c487bf8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c487bf80ed1f4f8f082ba978fbafbce9a6dab31c))

### 🚜 Code Refactoring

- **hooks:** isolate all hooks sources under 'src/hooks/' ([49beecf](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/49beecf79eca3b38db805bb8c11be8d313d9ac0f))

### 📚 Documentation

- **components:** document GitLab CI/CD component for 'commits' ([db8565d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/db8565d78947423659b8193363d7929641affa82))
- **docs:** refactor and create new specification pages ([15b43ff](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/15b43ff9a4afe2e22d73afb112023f9379ea1501))
- **docs:** remove 'Documentation:' link from 'README.md' sources ([b269976](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b26997691f4962d27b58f4c92da5092086f0e51a))
- **mkdocs:** migrate to 'mkdocs-material' theme and features ([d7079d6](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d7079d67f326e71e7e2c8ed8994bc29c8e6eaf35))
- **mkdocs:** add 'commitizen' and 'pre-commit' reference pages ([864af2a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/864af2a9c141c1aca96df58e5a299183cc0e7f82))
- **prepare:** fixup `[optional !]:` quotings for 'commits` ([612f2a1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/612f2a102ba11dd7250f2f1b0a0aa6828537116e))
- **preview:** implement 'preview' SVG documentation ([86831d5](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/86831d51e1235f604b5e575eae2e42f22ba7ca8f))
- **preview:** implement commits creation documentation ([3b2709e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3b2709eace6f7be2595796a18cbb84bd4ed3c2a3))
- **preview:** refresh SVG preview for 'check-hooks-apply' fixes ([9710474](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/97104741931832f3f6593df65054e4d7f2977f80))
- **readme:** improve 'prepare-commit-message' documentation ([f7cdcd4](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f7cdcd4e7b11854c114eef937ffcc16810e661c1))
- **readme:** document 'pre-commit' and 'commitizen' installations ([9ec1970](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9ec1970e858986cdfa41bcde86e2fe1487789882))
- **readme:** document '--settings' and 'NO_COLOR' configurations ([30931f6](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/30931f69ae2a17126cacc03dafd4e875207294ae))
- **readme:** add new dependencies and references links ([9949b22](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9949b22350a7b0557e91f64eb48bf3bfad068af3))
- **readme:** improve 'Features' and 'Commands' documentations ([2b52013](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2b52013238df998c6fbbdbdaf797c96066ca8fbd))
- **readme:** fix 'pre-commit-crocodile --autoupdate' documentation ([b392403](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b39240331e6d67b0218b6662f0c7863372abf5e0))
- **readme:** refactor and use 'pre-commit' badges for 'Commands' ([03b3b7c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/03b3b7c8e8725682f19fb59344482a3d3aa357b9))
- **readme:** add 'pre-commit-crocodile' documentation badges ([812d22b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/812d22b496c3f404a7c918ea016978abc11c0ee4))
- **readme:** add SonarCloud analysis project badges ([0a55099](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0a55099210f4c4bd797c9e53d758183c10c3823f))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([5f90c33](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5f90c33f77e350ace19b0f9d47c470e3618200ef))
- **readme:** isolate '--autoupdate' from '--enable' instructions ([2f87610](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2f876104b4b8c10fd102ce7ef0131442c20f7271))
- **readme:** clarify commands for projects with/without configurations ([5be9579](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5be95798c90ca790d21ae7dd5f1f22a506706ec8))
- **readme, docs:** add 'pre-commit enabled' badges ([df4de33](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/df4de33c8c1f1255d355c2ef799ed6930523e735))
- **settings:** remove 'engines' configuration derived from 'gcil' ([136173f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/136173f3edec9350b0a8bd3b4de75e9cea91c9a7))

### 🧪 Test

- **requirements:** raise 'pexpect-executor' version to 4.0.0 ([240a9e2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/240a9e253d2dddf74c96c19b9e93c9456c38667b))
- **requirements:** raise 'pexpect-executor' version to 4.0.1 ([66fad86](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/66fad8614f106f7298a52be4c4d10896f83d64d4))

### ⚙️ Cleanups

- **cliff:** fix 'pre-commit-crocodile' GitLab URL in CHANGELOG ([b92eaca](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b92eacae357f606cc5714c26038b61ab268a1e7e))
- **entrypoint:** refactor assets resources access ([aaa104f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/aaa104f796093425ba914fa7ce3ed38af3812da8))
- **entrypoint:** reorder 'options.disable' code section ([cdd8dad](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cdd8dad082a59a377e4198a28d51f109580ff905))
- **entrypoint:** minor 'Commands' codestyle improvements ([4751c20](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4751c20621b8dbba8faf74dc29a76c0f6d2cd321))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([6ff1836](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/6ff1836a02f37fa9ef2e556268851b0f3b1296d2))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([b63d959](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b63d959c7e714d6ccdf6252cf9ac8c107b897f00))
- **gitignore:** ignore '.tmp.*' intermediate files ([c11c992](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/c11c9928104d0bc47d120f9e8ac42a9599b50684))
- **gitignore:** minor comment improvement for 'Documentation' ([cb96c3c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cb96c3ccdd0d3dceb2ae7ea449bcf10444df6cd4))
- **pre-commit:** rename repository to 'pre-commit-crocodile' ([8e92229](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8e922290f490a31eeced7332df317f90cf1a1e0b))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([6556920](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/655692022b12f7175d01d65cfb6b1433e01cdd23))
- **pre-commit:** fix '.py' local Python hook execution ([27d8d2e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/27d8d2ef49a85bb75ad22095d866b4c18c0e5643))
- **setup:** add requirements from 'runtime.txt' as dependencies ([73ed96f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/73ed96f92f752e7c5591ca82646106e39f126765))
- **setup:** add 'Statistics' URL to the package description ([33a92e5](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/33a92e514df909e248fdda99bb49a23c076694cd))
- **vscode:** ignore '.tmp.entrypoint.*' files in VSCode ([39e9170](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/39e917045fa8661ddfb9bdd0e3c81a34340db9f9))

### 🚀 CI

- **commits:** use 'pre-commit-crocodile:commits' image ([f3fefc2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f3fefc28f135391eb9474dd3235a054f7d0f1fdb))
- **commits:** implement 'commits' job as a GitLab component ([510f44c](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/510f44c79c9ad34acc93055e29d83c85bdf2c23b))
- **gitlab-ci:** show fetched merge request branches in 'commits' ([b109199](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b10919985d627023719b9e21fb92ee898348b90b))
- **gitlab-ci:** need preparation jobs for 'pages' deployment job ([4f68937](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4f689373dd794148fbfa03a7db9f302b6eb3d1f4))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([3c54504](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3c54504413f2bc1e30d254033611988bdccb39be))
- **gitlab-ci:** fix 'image' of 'commits' job ([9a7614b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9a7614bc4dcbbee9edfa7b58022fd1156803374c))
- **gitlab-ci:** fix 'before_script' of 'commits' job and add comments ([cc7492a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cc7492a30166a64f59596841dd41b18dff7afb20))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([ac2291d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ac2291d83d46307a8c92267feb211084a31158fe))
- **gitlab-ci:** rehost 'python:3.12' with 'images' job for 'pages' ([bca847a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/bca847ae7c8fa631ad197ec638f5fbba7a3d337a))
- **gitlab-ci:** prepare 'build' and 'deploy' container images ([355c3fb](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/355c3fbe1c73638de6d7f59251fdf92a1ab7465e))
- **gitlab-ci:** implement 'build' job to build and package '.whl' ([dc2558d](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/dc2558d15a757fc5f942c3af5f626c2fb25fa495))
- **gitlab-ci:** import 'install' job from 'gcil' ([5c3327b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5c3327bf12b8756ad4390d89909cadc29b2016d0))
- **gitlab-ci:** import 'readme' job from 'gcil' ([2b0ec11](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2b0ec110a9a144ad0b7730f270c478c38e87ba97))
- **gitlab-ci:** isolate documentation preparation into 'docs/prepare.sh' ([5ad76f5](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5ad76f5ad6d86ece331457a640ee804550a00013))
- **gitlab-ci:** create 'serve' local jobs for 'mkdocs' tests ([017e0cf](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/017e0cfae85376472d99f1e02ece9090898f1235))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([e2978b8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e2978b80d9ab67c72ca32de5258705acb7b2738f))
- **gitlab-ci:** patch '.pre-commit-config.yaml' asset version upon tag ([482c221](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/482c2214cb19394958a3fdf355a3699065f84c7a))
- **gitlab-ci:** use 'pre-commit-crocodile:build' image ([bb1e245](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/bb1e2450623e4570cc5189b33cfba1830a441961))
- **gitlab-ci:** check only Python files in 'typings' job ([b511437](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/b5114374c1ae1da2b2726e823dab367bdccbd5a4))
- **gitlab-ci:** use 'DEBUG_REVISION_SHA' for unreleased 'preview' use ([ab92cde](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ab92cde321d7af4ba34798e1426f089d0cfbabb8))
- **gitlab-ci:** implement SonarCloud quality analysis ([2b16fe9](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2b16fe923d946474f6692aa4dcf36758ea208e7c))
- **gitlab-ci:** implement 'deploy:*' release jobs from 'gcil' ([3d9ddff](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3d9ddff70f749878e57a5ad0fcb3e281df528257))
- **gitlab-ci:** deploy 'pages' on 'main' branch only ([1c61717](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1c61717b13fdf1df609f6416c1e25b84aa5c191e))
- **gitlab-ci:** run 'pages' jobs after successful tests and coverage ([ab223cc](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ab223cc5a2d67a2ad40fd91271ee6b5e0a953ccb))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([85291d1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/85291d1c9ed91a9251a1efab4d5abe9212a64472))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([7305d70](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/7305d70396b7cacbbadcf66060c6e4fddb3a7fda))
- **gitlab-ci:** watch 'docs/' changes for 'prepare.sh' in 'serve' job ([cbb3b33](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cbb3b33ce25bc49662ad53ba51d03737db08243c))
- **gitlab-ci, containers:** create 'pre-commit-crocodile:pages' image ([44470bc](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/44470bcffc5b72c7507a0cfd3146ace8568b0ce1))
- **gitlab-ci, containers:** create 'pre-commit-crocodile:codestyle' image ([987ec50](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/987ec50824379d4ec7c365227721f6276cc1a595))
- **gitlab-ci, containers:** create 'pre-commit-crocodile:preview' image ([215e1d3](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/215e1d332a2eabe67960abae1327347a966cb965))
- **gitlab-ci, tests:** implement coverage initial jobs and tests ([5169994](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/516999439e1aa0635034f2ef4755ac2df63eab65))

### 📦 Build

- **codestyle:** install 'pexpect-executor' in the ':codestyle' image ([7faf133](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/7faf13385f0cd972afd55b1c65ec645b72c8e8b7))
- **commits:** create 'pre-commit-crocodile:commits' simple image ([48fcf9e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/48fcf9e22787075370c224a6f53656b4b3e58e47))
- **preview:** install 'git' in the ':preview' image ([e03e6d0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/e03e6d0fe0d34e3440844a6fa139036fc2c739bf))
- **preview:** install 'nano' in the ':preview' image ([ae44cc0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ae44cc0f5a4e67cbeda1c39c53b329b39d0a736f))
- **requirements:** install 'pexpect-executor' in ':preview' image ([5587450](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5587450dc848462b8de593e57a644ce960e71fde))
- **requirements:** install 'pipx' in the ':preview' image ([250a536](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/250a53665bcdb4861d91050143f300a8089cf494))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/1.0.1...1.1.0) (2024-08-17)

### ✨ Features

- **pre-commit-crocodile:** migrate to 'pre-commit-crocodile' name ([cd8bad7](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cd8bad75a4fdd63cd96a042f5965bb59c3df602d))

### 🚜 Code Refactoring

- **src:** isolate all sources under 'src/' ([894a161](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/894a161d32771ae6c64d1d4fae032a84a107d25f))

### 📚 Documentation

- **readme:** update project descriptions for developers ([cf33578](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cf335785989aa5ec7121a6c8767f7ecc8b3a7e31))
- **readme:** add 'Conventional Commits' URL as reference link ([d984931](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d984931f3f343a987958ceb3ec71cdc49dc86319))
- **readme:** document features and usage of 'prepare-commit-message' ([985524e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/985524e9c7e4cbbd5dde0b0a0692a9599187b2f4))

### 🚀 CI

- **gitlab-ci:** remove unused 'requirements' folder changes checks ([f1b5f64](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/f1b5f644b94993624601bf999d96ecf8cad4764b))


<a name="1.0.1"></a>
## [1.0.1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/compare/1.0.0...1.0.1) (2024-08-17)

### 📚 Documentation

- **cliff:** import 'git-cliff' configurations from 'gcil' ([584fea2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/584fea2b90eaa64fbfccd4cd1ccdc7ce4d1ec768))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commits/1.0.0) (2024-08-17)

### ✨ Features

- **pre-commit:** bind 'prepare-commit-message' CLI entrypoint ([38257d2](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/38257d2dcc5493ead37750fada5b46fa69fc90c4))
- **pre-commit-hooks:** migrate to '.pre-commit-hooks.yaml' hook ([75ca0c1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/75ca0c1797ad17cbbfbfe5a04059392f2dd92153))
- **prepare-commit-msg-template:** evaluate 'pre_commit_hooks' path ([cce56ea](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cce56ea35e6e6aea020e479ce05cbfec70494cb2))
- **setup:** implement initial 'setup.py' packaging from 'gcil' ([337322a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/337322aed20bac65b6a4f2e7667595e38af23b37))

### 📚 Documentation

- **license:** apply Apache License 2.0 license to the project ([5796350](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/5796350db55b66d221de9d7ab771324984caf57f))
- **readme:** initial 'README.md' documentation with dependencies ([9108c38](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9108c3872174c4e418c1fa18fd5b28adb0f42485))
- **readme:** document RadianDevCore 'pre-commit-hooks' repository ([2b75e41](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2b75e410b5d44ce475289cb86e5f5d461e66492c))
- **readme:** document 'prepare-commit-message' as available hook ([27ae472](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/27ae472654f86bcd4a71358af1f35d2aec15635b))

### 🎨 Styling

- **commitizen, pre-commit:** implement 'commitizen' configurations ([ad3713b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ad3713b695a8099596b31e2c2417c7af8d9e59a6))
- **markdownlint:** import Markdown codestyle rules from 'gcil' ([2d2c43e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/2d2c43e7629bf1aa75a5c3d30a378d8d11d9d3f3))
- **mypy:** import Python Mypy linting rules from 'gcil' ([1fc611a](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/1fc611a28d43e64b8f5c9cd2e7187af3d7c59188))
- **pre-commit:** implement initial 'pre-commit' configurations ([cd9d252](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/cd9d252b26d6ac901d909e1bc94d70b4518e1d2c))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([0a61f1b](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/0a61f1bcff0232c86e6338a21fa27945084cbde2))
- **yapf:** import Python YAPF codestyle rules from 'gcil' ([51983c4](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/51983c4a302cf1967885766b1a2dfeb12888747b))

### ⚙️ Cleanups

- **gitignore:** ignore Python compiled intermediates ([853f1ca](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/853f1ca7a90b38364835f9167daa6f303081782c))
- **gitignore:** ignore '.tmp' folder intermediates ([3737d2f](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/3737d2fcde139812b684036572dfd0e65f71c422))
- **hooks:** implement evaluators and matchers priority parser ([4975ec1](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/4975ec1cbb4633f1028b1f65a50aae7707ecaf38))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([81ae190](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/81ae1900205e3589211352f98e1e210e681d162d))
- **pre-commit:** disable 'check-xml' and 'check-toml' unused hooks ([ecc2a18](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/ecc2a18da3ab60eab84215c9478078485ab52c90))
- **vscode:** import Visual Studio configurations from 'gcil' ([8ea708e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/8ea708ef1c6a19837c714be26d0d2912c056ea49))

### 🚀 CI

- **gitlab-ci:** import 'changelog' and quality jobs from 'gcil' ([9ce445e](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/9ce445e4d9fe096b5eb6d29b54715907ba4ede6c))

### 📦 Build

- **hooks:** implement 'prepare-commit-msg' template generator ([60221d8](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/60221d87cdd22a050b2892aa31ca729e84eb3b35))
- **hooks:** create './.hooks/manage' hooks manager for developers ([d731261](https://gitlab.com/RadianDevCore/tools/pre-commit-crocodile/commit/d731261c93750eae2fc193f84d74869e888b97b8))


