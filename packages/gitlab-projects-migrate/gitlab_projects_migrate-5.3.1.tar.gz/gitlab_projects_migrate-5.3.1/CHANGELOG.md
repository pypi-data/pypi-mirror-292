# Changelog

<a name="5.3.1"></a>
## [5.3.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.3.0...5.3.1) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([a04cd3f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a04cd3fb6432db028b74730453a6de3bf1fe5cc2))

### 📚 Documentation

- **mkdocs:** implement GitLab Pages initial documentation and jobs ([4077cf2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4077cf2279a6b41f73b529027503be6137db34b7))
- **readme:** link against 'gcil' documentation pages ([4d192ae](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4d192ae2396c0f27c76304becb6331fd1ac7eaac))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([f09adcc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f09adccef149a31f219a7373b2b4ddb6550d7fbf))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([db8336b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/db8336b2ba83b0db38e74aa043c2c0a3320f25e5))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([658d2cd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/658d2cd2123b1b5d9272b2130c191469540e420d))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([2fc9cdb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2fc9cdb663e0762452f82cd906c0e8c0404e5ec3))
- **pre-commit:** improve syntax for 'args' arguments ([75cdc0b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/75cdc0b2e5af2947295f288f3705a32d0b3c2a02))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([f81d11c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f81d11c9af1c293d0b8f9b04cb39fe82036ac013))
- **pre-commit:** update against 'run-gcil-push' hook template ([505b5b5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/505b5b513a6f6853dcdd07585149bdaee9594c33))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([a7a93ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7a93ac11aaf452f97e5af720236533858a36864))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([623c9bb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/623c9bb14ea63a6904d86411e4654e8fb238ecbd))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([9872de6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9872de62b036b9d58ea71128b164b62d55b93d91))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([88d8ab1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/88d8ab14caf43f3535723ad279946cfd95ec350d))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([cd1e3be](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cd1e3bedbdd3506e2dd562d63fd8682f17145988))


<a name="5.3.0"></a>
## [5.3.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.2.0...5.3.0) (2024-08-21)

### 🐛 Bug Fixes

- **package:** fix package name for 'importlib' version detection ([4310eeb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4310eebe61df590558817480db0307da8db68c1e))
- **platform:** always flush on Windows hosts without stdout TTY ([336fd2d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/336fd2d751e81be383d7442eaabf98be9e189133))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([3ae46f3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3ae46f30c50888138d0ff19339e9786eb97ba85e))
- **readme:** add SonarCloud analysis project badges ([79f0c09](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/79f0c09a047968d89291855af7df27f11e6f827c))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([84f65e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/84f65e2271a164a6132edda33be30c2a47d6a521))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([1ed854f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1ed854ff78ad46b90d142a78dce1534a644e09d3))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([d48e1ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d48e1aca3ad2b025fe00c603f9cf1200617a0c82))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([e87a978](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e87a978998f4b23d002adbac8cd01b2a674dd630))
- **hooks:** implement evaluators and matchers priority parser ([7e48cc8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7e48cc8f7992e3e94fbc18ce33d10c413e4a5b9d))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([f8796e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f8796e86f655151340fc5fe1a0d584eb0ba06a0a))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([f425805](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f4258050b866ac2cb5f057a1381bf35e5d671f86))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([7af39e4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7af39e444f545a128cbe9ef23673cd674caac14e))
- **gitlab-ci:** fix 'image' of 'commits' job ([2af9e4f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2af9e4f1129ee02fda6105167132d446cb99062b))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([c36657f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c36657f883ae74312fbeb8638a07d16005383fd8))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([ed18d14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ed18d1488d969edfb4c68ebee8cf5c98ed16c3cb))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([ce816ea](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce816eadfe6f53e15862bb4d64d678184de20d41))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([f0cb573](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f0cb57386c5e96190fafdb99ca966a14f879c687))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([2c7cb24](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c7cb24e0a3680ea1cea4750a4605540f76dcfbd))
- **gitlab-ci:** check only Python files in 'typings' job ([a7434b9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7434b959d536212bea6394ad921aa04b4d95d49))
- **gitlab-ci:** implement SonarCloud quality analysis ([1ec376a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1ec376a73765403b8d768cf57d031baa390221f5))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([3cd6108](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3cd61087d7891e086541d27cafb67fb8811ec7b8))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([08e9717](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/08e971789719b5863d0bbd3faee63b9d82730d43))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([9bbe33e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9bbe33e05a5657154e2f01faff4e6038a536d0e2))
- **gitlab-ci:** create 'hooks' local job for maintenance ([ab13810](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ab13810460c194dc0e4f8375dfb8e9528a83c909))
- **gitlab-ci, tests:** implement coverage initial jobs and tests ([81c5bad](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/81c5badb7f35a9325ba23b3e1874fffc6502f0bf))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([91138ae](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/91138ae288221a810db0cf1d3ccc2d55aecad6c0))


<a name="5.2.0"></a>
## [5.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.1.0...5.2.0) (2024-08-15)

### 🐛 Bug Fixes

- **setup:** refactor 'python_requires' versions syntax ([1313d2e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1313d2e83633fec3142d3f5d07f460ae48b420dc))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 due to 'questionary>=2.0.0' ([c35db2f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c35db2f0a9ca741132579aee0a50830ebb5b50db))
- **setup:** resolve project package and name usage ([e247e21](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e247e218ae95f518e26b315e3bcac2b216ad061c))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([721c199](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/721c199898a6fde1fcc1c3aee35644063350229b))
- **updates:** fix offline mode and SemVer versions comparisons ([947dfbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/947dfbc3dc2d30c33957d719145aaa8bf0e55481))

### 📚 Documentation

- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([f4b9a7e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f4b9a7eb7c786cbed38979921c457d6012d7866f))
- **license:** update copyright details for 2024 ([87d3a30](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/87d3a3056cc218d032c5d8978d7dbe385d3e5bf3))
- **readme:** add 'Commitizen friendly' badge ([6cfd434](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6cfd43495e0bb63a9acd97d5adb30aeae50ccf8f))

### 🎨 Styling

- **cli:** improve Python arguments codestyle syntax ([4aedfed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4aedfed4bfbb649a304e237bf31d13e169c2ac7e))
- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([12c4300](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/12c4300a199f2074a47ae06835980b2ac83fe80d))
- **pre-commit:** implement 'pre-commit' configurations ([7300bde](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7300bde8691f4d1ae15a031f033f1352aa6561df))

### ⚙️ Cleanups

- **cli, package:** minor Python codestyle improvements ([50f3a98](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50f3a98e14654d0627c60c9330dc7467342e2a14))
- **pre-commit:** disable 'check-xml' unused hook ([be305d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/be305d376f3348996a82d6da149c85133867d5f0))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([456a108](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/456a108cda41e3b9e250eeed5077970b9cacedaa))
- **setup:** refactor with more project configurations ([197125e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/197125e522d70e2db789ede73600ce2222310c67))
- **updates:** ignore coverage of online updates message ([9f273d9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9f273d9fe49dddbe95746bb0af46550e766d2ab9))
- **vscode:** remove illegal comments in 'extensions.json' ([a691dbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a691dbc81ccddfbeb88252d4d8b7f36ef296e7a0))

### 🚀 CI

- **gitlab-ci:** watch for 'codestyle', 'lint' and 'typings' jobs success ([a9425db](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a9425db27bb16f12aa66906154680c266407164d))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([b2c8d00](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b2c8d007872f14e3ff3c21c1f2adf204baf43941))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([4e3402e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4e3402ecd5a9a4fa2069e4bcfc75a58b98fa5a33))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([048b9f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/048b9f6f12a900eb3064a04ef59cad1401fdaf37))
- **hooks:** implement 'prepare-commit-msg' template generator ([a16f1ce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a16f1ceb465ef1959aed39126c1582cbbac327c3))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([5fd439c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5fd439c73dde86aecadf1609e071c5dbf6f84b5d))


<a name="5.1.0"></a>
## [5.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.3...5.1.0) (2024-08-11)

### ✨ Features

- **cli:** implement '--no-color' to disable colors ([294fd18](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/294fd1885e302208d97ec3cd5cf9666aba996253))

### 🐛 Bug Fixes

- **package:** check empty 'environ' values before usage ([42b25d4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/42b25d43b69ab374104d01c07f8b7902f695a72f))
- **updates:** remove unused 'recommended' feature ([201ca49](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/201ca49df3888fda1ed9bfb46332c00648199a2b))

### 📚 Documentation

- **readme:** migrate from 'gitlabci-local' to 'gcil' package ([9c81cd8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9c81cd82b6a538b2e11af76eee1e00dc9d9aafbc))

### ⚙️ Cleanups

- **cli:** resolve unused variable value initialization ([c6f99cd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c6f99cde80c7aef1d2538e4a55601314b61ac7cd))
- **colors:** resolve 'pragma: no cover' detection ([64c028e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/64c028ea18079737fb26a8b9ab6cbb50f811e240))
- **platform:** disable coverage of 'SUDO' without write access ([6c1d314](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6c1d3144acf88bfe36a30102b69cefcc2e75fc24))
- **setup:** remove faulty '# pragma: exclude file' flag ([03bb970](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/03bb970ac21e6385e86d33f5dec7e544ac94c6c2))


<a name="5.0.3"></a>
## [5.0.3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.2...5.0.3) (2024-08-10)

### ✨ Features

- **setup:** add support for Python 3.12 ([b72e9a1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b72e9a178aefdc961e0fe87ece704b9bb5d3d4b2))

### 🎨 Styling

- **main:** declare 'subgroup' variable as '_MutuallyExclusiveGroup' ([3e1842c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3e1842c5be3a189960b05a23a94b93c15dc23e93))

### 🧪 Test

- **setup:** disable sources coverage of the build script ([8e7ce06](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8e7ce0695410df8ebce8a8fd432f38d4e4959062))

### 🚀 CI

- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([47da8d5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/47da8d5369331a2a033f62460428a07e4090c84c))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([2a890ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2a890ac178af80ed080ed5a41b20a40fc5e10b68))


<a name="5.0.2"></a>
## [5.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.1...5.0.2) (2024-08-10)

### ✨ Features

- **gitlab-projects-migrate:** migrate under 'RadianDevCore/tools' group ([50ed087](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50ed087e57116b044692ca2220e6c4ce21018a60))

### 🐛 Bug Fixes

- **settings:** ensure 'Settings' class initializes settings file ([beb96ff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/beb96ff7336b23e248c1a83abb7ce2c2d4c89233))
- **src:** use relative module paths in '__init__' and '__main__' ([79e567e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/79e567e1c2d97d0f7bd48af84cf923fe40bc43eb))


<a name="5.0.1"></a>
## [5.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.0...5.0.1) (2024-08-08)

### 🐛 Bug Fixes

- **cli:** fix syntax of '--reset-entities' argument variable ([5bb61f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5bb61f02646871647dfa78fb22cb565c22e9146c))


<a name="5.0.0"></a>
## [5.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.1.2...5.0.0) (2024-08-08)

### 🛡️ Security

- **🚨 BREAKING CHANGE 🚨 |** **cli:** acquire tokens only from environment variables ([1cca6b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1cca6b8231e7a1bb8860a3033d086f2e38d0d035))

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **cli:** refactor CLI into simpler GitLab URL bound parameters ([495ccf3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/495ccf3b26c2934ffc36c02369547613d9bfd8e8))
- **cli:** implement '--confirm' to bypass interactive user confirmations ([640109c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/640109c63502e57de2c5fa86a5c43ae7b6e9006c))
- **cli:** support 3rd positional argument for '--rename-project' ([23a4e94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/23a4e94245449f3b05b544d0b48ef8dde3524c0b))
- **cli:** add tool identifier header with name and version ([8dfd23f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8dfd23f276f540d3f2bb27d99806e35d0496ca24))
- **cli:** implement '.python-gitlab.cfg' GitLab configurations files ([0782032](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0782032dfa92ebbc29401ca79aa89377df888c2b))
- **cli, argparse:** implement environment variables helpers ([f660b3f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f660b3f3b5308c4b8b2de96a7856274228b5063f))
- **cli, gitlab:** implement '--available-entities' for migration ([c52056a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c52056acae4a24e2cbc26e0a71a71cd0a672d169))
- **🚨 BREAKING CHANGE 🚨 |** **cli, gitlab:** migrate from '--keep-members' to '--exclude-entities' ([fff8a55](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fff8a552ad5dccbf885ded6ebcd6ee2b9246bf38))
- **cli, gitlab:** implement CI job token and public authentications ([c9a78f8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c9a78f88e359cb740afd80855f253b7533acd083))
- **cli, gitlab:** migrate to '--reset-entities' parameter name ([c8d3b19](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c8d3b19dab249a3b4c4ad34b3198db97944e3ab6))
- **entrypoint, gitlab:** implement 'Remove:' and 'Template:' entities ([6d90592](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6d90592a92f928cb6f8a86bbd2a81d35e2d81d63))
- **gitlab:** migrate entities to 'Remove/' and 'Template/' ([91e1942](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/91e1942cb72d61e0a12e3fc606b09e383a22f708))

### 🐛 Bug Fixes

- **environments:** add missing ':' to the README help description ([3ae5b5d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3ae5b5d2cb5355fe39eefedd2fb7d9c7339fe207))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([e8499a9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e8499a949fa5a74ac6231e43c82e345d0923284f))
- **readme:** document '~/.python-gitlab.cfg' configuration file ([07c1d6b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/07c1d6be890c3134da2a074d638aa62c811acad5))
- **readme:** document projects copy and project renaming ([32107fd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/32107fda7276ca59cd402b4c32837fafa91f667d))
- **readme:** document projects as templates copy and entities cleanups ([e525ca3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e525ca323fdbf5d4d9b468381f707d996f8d8d84))

### ⚙️ Cleanups

- **cli/main:** minor codestyle improvement of 'import argparse' ([fcd1716](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fcd171612e83bc5f27419a3b8c7647d8b6bd5528))
- **gitlab:** remove unused 'type: ignore' and resolved TODO 'fixme' ([2905f9f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2905f9f74c2c8e3db8bdd2348d3a730c82d3572d))
- **types:** cleanup inconsistent '()' over base classes ([c0150d6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c0150d66910f5899594e4c04156a94e7b6bb2339))

### 🚀 CI

- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([77bc35b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/77bc35b96566c8dbe71afa455a77bf2d50840325))


<a name="4.1.2"></a>
## [4.1.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.1.0...4.1.2) (2024-08-06)

### 🐛 Bug Fixes

- **entrypoint:** fix already existing checks if renaming project ([20c8268](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/20c8268bdf986cd2ae5a2efacedb74f2d60c98e7))
- **entrypoint:** fix already existing removal if renaming project ([303a798](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/303a798d59c85e09366501e5ca5a25b8330ccbf5))
- **gitlab:** wait 3 seconds after group and project deletions ([9957021](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9957021bea497469c2f30fe723e472b0059dcde2))


<a name="4.1.0"></a>
## [4.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.3...4.1.0) (2024-08-04)

### ✨ Features

- **gitlab:** warn about 'Pipeline triggers', 'Webhooks', 'Project Access Tokens' ([760884f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/760884fe3ca1cef38ad1599ddff99ba7e967225d))

### 🐛 Bug Fixes

- **entrypoint:** fix project checks by path rather than by name ([98f4577](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/98f45779beb93a8f1e48e2bc16c0c944922443e6))


<a name="4.0.3"></a>
## [4.0.3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.2...4.0.3) (2024-06-11)

### 🐛 Bug Fixes

- **gitlab:** fix namespace detections upon '--dry-run' executions ([a331fb8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a331fb87e6732695935290c7979b30a23ddb0f8f))


<a name="4.0.2"></a>
## [4.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.1...4.0.2) (2024-06-10)

### 📚 Documentation

- **chglog:** add 'ci' as 'CI' configuration for 'CHANGELOG.md' ([f2231d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f2231d3015b366cb6815716f0c331777cef58013))

### 🚀 CI

- **gitlab-ci:** support docker pull and push without remote ([9118e38](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9118e3809cc77ac5953a633b6bbec4094c786ee4))
- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([ffca219](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ffca2196436b01ebb9b55b94f5cc469e16f3faa9))
- **gitlab-ci:** change commit messages to tag name ([35b9df0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/35b9df0efa834817ef63be0704cdb6fda644f963))
- **setup:** update Python package keywords hints ([5f36462](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5f364625a50056b7ccd12031a73ece0b9503cdd5))


<a name="4.0.1"></a>
## [4.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.0...4.0.1) (2024-05-27)

### 🐛 Bug Fixes

- **entrypoint:** resolve already existing nested subgroups check ([bf656d0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bf656d0722fdf306e21458c93b17433640033a56))
- **gitlab:** resolve '.variables.list' on old GitLab instances ([483823e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/483823edcd9667bee6d7c732b224b5bb3fe8cbee))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.1.0...4.0.0) (2024-05-26)

### ✨ Features

- **entrypoint:** improve outputs logs upon delections ([8da3ae1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8da3ae126918b512e5b8b8d1245f3b56bccb6c18))
- **entrypoint:** identify already existing project, group, subgroup ([7baf7b3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7baf7b339958d8a72517654915ab42dbd11ebfd6))
- **entrypoint, gitlab:** detect and confirm export limitations ([797e469](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/797e469505d4b685c54701ca7553bb629290c3a8))
- **entrypoint, main:** implement '--rename-project' to rename project ([fdf447f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fdf447f4bce3bff49f6a05df9375b25b9434b892))
- **main:** show newer updates message upon incompatible arguments ([5561849](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5561849746623a127ad4ad5e182619ad4d02221e))
- **main, entrypoint:** implement '--archive-sources' mode ([64dc73a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/64dc73aa16305666d8799f9d7b413a64e6ecabb5))

### 🐛 Bug Fixes

- **gitlab:** fix project import 'path_with_namespace' in dry run ([e4bf8e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e4bf8e28f992d7d0e2ef4876c86623bcd31a61b2))
- **main:** exclusive '--archive-sources' and '--delete-sources' ([f29389e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f29389e59f1faabb61bb573cbe3e63a20dcb94d6))

### 📚 Documentation

- **readme:** add '--archive-sources' and '--delete-sources' examples ([59779ca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/59779ca61361efe303c2be4712cb9bdfc68c921b))

### ⚙️ Cleanups

- **entrypoint:** turn 'confirm' function into generic handler ([5151afa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5151afaa67a217da46bef4f1ad9745c4569198a7))


<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.0.1...3.1.0) (2024-05-17)

### ✨ Features

- **entrypoint:** implement '--archive-exports FOLDER' to keep exports ([2c47fb7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c47fb7850a796c03f5cb07ec17833186f0af2ce))
- **entrypoint:** implement prompt confirmation upon deletions ([3430da0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3430da052200cda1630cfd7a101fe9033c45a678))
- **requirements:** prepare 'questionary' library integration ([1a2877c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1a2877c970adf054f9842be298bab8a3fe439194))

### 🐛 Bug Fixes

- **gitlab:** raise runtime error upon failed project imports ([38ffbb6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/38ffbb6947a0a79e7f38fe3abc116ffe0b0de5a2))
- **gitlab:** restore 'import_project' file argument as BufferedReader ([d2a6eaa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d2a6eaa7dbca713cbccabfb8e28d7290e2c4f9a2))

### ⚙️ Cleanups

- **gitlab:** ignore 'import_project' file argument typing ([edd0867](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/edd08673819429493a7ca3a6ad1f11fb9dbfd038))


<a name="3.0.1"></a>
## [3.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.0.0...3.0.1) (2024-05-15)

### 🐛 Bug Fixes

- **entrypoint:** resolve 'output_namespace' assertion tests ([a7e48c9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7e48c9887ab1691f9ffe70bef5626b969da555b))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/2.1.0...3.0.0) (2024-05-15)

### ✨ Features

- **entrypoint:** always flush progress output logs ([e8067f2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e8067f21fd1b41f27d7f654235da5384f35c9b29))
- **entrypoint, gitlab:** adapt name for '--update-description' ([f3fe725](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f3fe72586753b096cbe00e33ffab02f2dbe75388))
- **entrypoint, gitlab:** add support for user namespace projects ([e5118a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e5118a42e41355596da7c209265e47e39d8d01e7))
- **gitlab:** automatically wait for group and project deletions ([c998605](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c99860531de2495ebadca65943a4b52eae1caeb4))
- **main:** document optional '--' positional arguments separator ([aff6a17](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/aff6a171b1cedcc30bc4e6e916a094f5a7ec2609))
- **main, entrypoint:** implement '--delete-sources' final actions ([140ff3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/140ff3aa69a16c57edff3e657e36ae65057ab7f2))
- **main, settings:** implement 'Settings' from 'gitlabci-local' ([dc36932](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dc3693298446c2d64955b3617d13011b62418a85))
- **main, upgrades:** implement 'Upgrades' from 'gitlabci-local' ([3a1ae89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3a1ae8977feea33b9afb9a33b4ccf2b62b9fec63))
- **namespaces:** migrate 'Helper' class to 'Namespaces' class ([5a82589](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5a82589ff29fff3344f2297d98fe3eba7b7974f6))

### 🐛 Bug Fixes

- **entrypoint:** enforce against missing '.description' values ([9db9037](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9db90379c38df0a25fd763863c13ad60faa9c23b))
- **entrypoint:** detect if GitLab actions can continue ([c1a8d2c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c1a8d2c074f65f23565ab66f5202a353af5303d4))
- **entrypoint:** minor Python codestyle improvement ([2e138e3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2e138e39127afd6a7bd204d460e70f3d45d12987))
- **entrypoint:** use full paths instead of 'id' integer fields ([524eb14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/524eb145846da12f5292024125b84617de6646e9))
- **entrypoint:** refactor to return no error upon final actions ([6367e89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6367e8988236b978197d9f8fefefe6be44665dbe))
- **entrypoint, gitlab:** resolve Python typings new warnings ([393e239](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/393e239134a1bd88d19ce50b92f64cc5f1432c3a))
- **entrypoint, namespaces:** add 'text' to handle empty descriptions ([005b50c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/005b50c12a169dad6aa69a884a8e1e69708c85bb))
- **gitlab:** get all members in 'project_reset_members' ([f2834a2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f2834a241fb07a1415436088b6c52ccc48515be7))
- **gitlab:** fix 'Any' and 'Optional' typings imports ([4af24ba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4af24baed4772b37137d84d69aefde933222dc83))
- **gitlab:** try to get real group before faking in '--dry-run' ([70ea00d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/70ea00d3119f9619161b7c8d2329319bd4d21a23))
- **gitlab:** add 'description' field to fake project in '--dry-run' ([9b7bca1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9b7bca16cccd2772dd4e4cd7bc6d7d6dc51f5adc))
- **gitlab:** accept deletion denials in 'project_reset_members' ([be12ff0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/be12ff0b9c3fd3bfe5380e99d04da37e0d204c61))

### 🧪 Test

- **version:** add 'DEBUG_VERSION_FAKE' for debugging purposes ([ae75971](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ae75971a49ceb55e46760316ab898f5b6a5037ec))

### 🚀 CI

- **gitlab-ci:** move 'readme' job after 'build' and local 'install' ([97d3ed0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/97d3ed02ab08e8db94ebde60ff4d32388c2a3438))
- **gitlab-ci:** handle optional parameters and multiline in 'readme' ([a720e9c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a720e9c9086bfdd92ed8f8dcff03ac3b81818e64))
- **gitlab-ci:** detect 'README.md' issues in 'readme' job ([f817eef](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f817eef04fba14e2a6b97780876f186227d25e71))
- **gitlab-ci:** implement 'images' and use project specific images ([5475393](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5475393610cf67897736f9720da6e4faf10c779b))
- **gitlab-ci:** deprecate requirements install in 'lint' job ([4e03a36](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4e03a365d9c2e7efdb702d8e978bae76f7a8b6b2))
- **gitlab-ci:** support multiple 'METAVAR' words in 'readme' job ([2c571f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c571f66d104faac58c5a8d63eeb99ec09d78b8e))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/2.0.0...2.1.0) (2024-04-28)

### ✨ Features

- **entrypoint:** keep description if already contains group ([4c50766](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4c50766886b6af5c76e1758016640bc00a183646))
- **entrypoint:** sort groups and projects recursively ([90e59a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/90e59a49992aef0809b0d0aaaa3de23a6c89b06e))

### 🐛 Bug Fixes

- **entrypoint:** resolve input group for single project migration ([ce5c66e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce5c66e4722914df467f3a8d6ceada5214a021c9))
- **entrypoint:** resolve input group detection for projects ([96ccad9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/96ccad9be44ab1a1592fd57f65aac9e6da8b05f9))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/1.1.0...2.0.0) (2024-04-28)

### ✨ Features

- **cli:** isolate 'features/migration.py' to 'cli/entrypoint.py' ([b54de48](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b54de488db64bd48447e50631047498de3f27aff))
- **entrypoint:** isolate 'group' function to 'subgroup' ([5436398](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/54363985d3e70493d62eb64073d6a75a7df3e008))
- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.subpath' ([a3d9f28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a3d9f28c4f7872d237eda9c932658d09b503f605))
- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.capitalize' ([7a745e4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7a745e4cce19af66a1b6333007d368f5a67e3ffb))
- **entrypoint, gitlab:** implement output parent group creation ([c9218c3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c9218c383884ea1f9084e8bcc80e6466bde55768))
- **entrypoint, gitlab:** implement groups export/import handlings ([a2e6989](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a2e69896d693013dd127e87311fb5cc73bf0e263))
- **gitlab:** prepare group settings functions for future usage ([167962a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/167962a02f2167ee5c03e702b3c8ad51448182c6))
- **gitlab, migration:** refactor into GitLabFeature functions ([41436ec](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/41436ec1f327c3a5d907d5b8fbbc9603cf10a34c))
- **main:** isolate CLI argument into specific sections ([95ec817](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/95ec817167bef8bf09443909ea2fbfd66c6847ab))
- **main:** enforce 'output_group' value is always passed by CLI ([701c335](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/701c335e3feaefd89aea81d7244fd90c7a2e68fe))
- **main:** align 'RawTextHelpFormatter' to 30 chars columns ([c15bf79](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c15bf79da3523d21747b101acc01a1796015712e))
- **main:** limit '--help' width to terminal width or 120 chars ([3fcaac0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3fcaac09274dadc907b121207424b727a9180f15))
- **main:** add support for 'GITLAB_TOKEN' environment variable ([a8cae39](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a8cae39731cf10df1b227e895cf31a90916c0d80))
- **main, entrypoint:** implement '--exclude-subgroups' filter ([377bff5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/377bff5f8f9479529f1f64a3f3d17a9d526eb482))
- **main, entrypoint:** implement '--exclude-projects' filter ([7c09032](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7c0903269ce3f31a287589e153c5cc582f159651))
- **main, entrypoint:** implement '--exclude-group' filter ([21a513c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/21a513c14941bdc088ef1a0b59bd5a61a19e8b15))
- **main, gitlab, migration:** refactor and add '--dry-run' ([afe7a8d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/afe7a8d60c3781fb6c781a324899ace9dc50e56f))
- **migration:** sort group projects in ascending 'path' order ([23232de](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/23232de186c041ff6692ea6124e545578369d153))
- **migration:** implement support for input project along group ([cd51b98](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cd51b982c954ee81fd0afef5ccc014b276ceaa53))
- **migration:** implement nested projects migration support ([5639fca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5639fca40b9744f3444fec3aa11fee104eafca67))
- **migration:** implement GitLab subgroups creation ([549f600](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/549f600f77c7e047217da0807f0096246f78a8f7))
- **settings:** change project/group descriptions color ([fb41f6c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fb41f6c3761788ce03f90eca36a0fb44a1be9921))

### 🐛 Bug Fixes

- **entrypoint:** safeguard group handlings for '--dry-run' ([8202026](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/82020262e1f927db57b3b9479ea4d19e70a6a11c))
- **entrypoint, gitlab:** implement description to name fallbacks ([5524af7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5524af7b8b9d902436e908ab31e14bc68dd38134))
- **gitlab:** resolve '--dry-run' usage upon projects migration ([65c0cdb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/65c0cdb6307e36992e2b04d18cd88dedf14d58d5))
- **main:** ensure GitLab token has been defined ([5f9cd0a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5f9cd0a4534556a4046ae36fe0c626c032e2f39b))

### 🚜 Code Refactoring

- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.split_namespace' ([ffd519b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ffd519b4b51938c4f2cb122caa516e91c19c9ea4))
- **migration:** refactor into 'entrypoint' main function ([ac9990f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ac9990f2054ca853266433b0fed4c63bbbeb2139))
- **migration:** isolate project migration feature sources ([330fbe4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/330fbe4eaeca1f5d950ab7c9bbd6ec71709cf133))
- **src:** isolate all sources under 'src/' ([7f97146](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7f97146a90627f66d3db435f90e566cc91fa6cfb))

### 📚 Documentation

- **readme:** regenerate '--help' details in 'README.md' ([0209976](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/02099760a523c8d1962c194801fd853f357c725d))
- **readme, cli:** minor project description improvements ([fbbb80a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fbbb80a41c45a5d76dbddf08fa9fcbfcf9af5e16))

### 🎨 Styling

- **main,migration:** minor Python codestyle improvements ([8f4ece8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8f4ece8a00391037f03914a68f6447a33e7e8913))

### ⚙️ Cleanups

- **src:** ignore 'import-error' over '__init__' and '__main__' ([fce4b15](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fce4b152df1368a33a6625a3e22e8b4f412da8dc))

### 🚀 CI

- **gitlab-ci:** implement 'readme' local job to update README details ([02c6fad](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/02c6fad7db2b1acf03bdaeeec5486f32c37a7efe))
- **gitlab-ci:** disable 'typing' mypy caching with 'MYPY_CACHE_DIR' ([e9ce388](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e9ce3887d682ef53c5f028134ded214b26d6b464))
- **gitlab-ci, setup:** migrate to 'src' sources management ([65dac94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/65dac94835db84ac6eb4cc2163d0779a8f8a5761))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/1.0.0...1.1.0) (2024-04-22)

### ✨ Features

- **features, prints:** implement 'colored' outputs colors ([dfdb3bf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dfdb3bf7608e95fa7465ed8950d4f4a930fb3f11))
- **migration:** implement '--overwrite' to delete and reimport ([34a2af5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/34a2af5ad8077564f0a714422ab0782869cc92a5))

### 🐛 Bug Fixes

- **migration:** prevent '--set-avatar' already closed input file ([ef2583f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ef2583f9cc37e13d2f5ee03a9091a8f4694f441c))

### ⚙️ Cleanups

- **migration:** minor output flush improvements ([ece017a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ece017a21d7fe2735dcaede1b9468a51b404055d))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commits/1.0.0) (2024-04-21)

### ✨ Features

- **gitlab-projects-migrate:** initial sources implementation ([89ed62b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/89ed62b74c076a9c49145be0ae366a1aac626933))


