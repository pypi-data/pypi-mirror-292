# Changelog

<a name="10.2.0"></a>
## [10.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/10.1.0...10.2.0) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([f7d3b55](https://gitlab.com/RadianDevCore/tools/gcil/commit/f7d3b55bc77342ce7391bb487ae98f3080a52fa5))

### 📚 Documentation

- **hooks:** create 'pre-commit' hooks documentation for 'gcil' ([f51ae8c](https://gitlab.com/RadianDevCore/tools/gcil/commit/f51ae8c41d19a58f110126176610748eb9f3b8ae))
- **mkdocs:** implement GitLab Pages initial documentation and jobs ([ee58d40](https://gitlab.com/RadianDevCore/tools/gcil/commit/ee58d406f29100b388ba93dbc5d0549661ed81b4))
- **readme:** link against 'pexpect-executor' documentation pages ([f8153f4](https://gitlab.com/RadianDevCore/tools/gcil/commit/f8153f440f4c64110a663c1d7e25663dbd8514c5))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([aac4bc8](https://gitlab.com/RadianDevCore/tools/gcil/commit/aac4bc81205b14474ec3d7545f7daec8a33c4eb7))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([038f710](https://gitlab.com/RadianDevCore/tools/gcil/commit/038f7103782b708b8aaa59a54fd011903b566e3f))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([9883f20](https://gitlab.com/RadianDevCore/tools/gcil/commit/9883f2055b13ba02a9f949db488835ddf7bb1dc9))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([53c4fde](https://gitlab.com/RadianDevCore/tools/gcil/commit/53c4fded5e43e19db5a1f76b4d3c65ca4cf1f5de))
- **pre-commit:** create 'run-gcil-job' template hook to override ([3028b17](https://gitlab.com/RadianDevCore/tools/gcil/commit/3028b17e8bca5fe0a73ed258c5829acac6fa3175))
- **pre-commit:** isolate 'run-gcil-commit' and 'run-gcil-push' hooks ([a58e977](https://gitlab.com/RadianDevCore/tools/gcil/commit/a58e977f50568d29b76888de793825aeb4cb06c7))
- **pre-commit:** improve syntax for 'args' arguments ([9db7ca2](https://gitlab.com/RadianDevCore/tools/gcil/commit/9db7ca21130cef03e87ce16197d00aba266679bf))
- **pre-commit:** improve syntax for 'args' arguments ([1b966b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b966b0e29b64acdac30d389dd82115bee3508d4))
- **pre-commit:** migrate to 'run-gcil-*' templates local hooks ([fdfdbdb](https://gitlab.com/RadianDevCore/tools/gcil/commit/fdfdbdb0b3de8fe687453a68772fcf836a356a77))
- **pre-commit:** update against 'run-gcil-push' hook template ([d537f03](https://gitlab.com/RadianDevCore/tools/gcil/commit/d537f03112be932b40d56d001c95d4cacfee600e))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([81de32c](https://gitlab.com/RadianDevCore/tools/gcil/commit/81de32c35863c41d8fb570c17fd43635134049b5))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([2a83c23](https://gitlab.com/RadianDevCore/tools/gcil/commit/2a83c23d5080f98b91f1f9414d2b2eb6ef279088))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([670c662](https://gitlab.com/RadianDevCore/tools/gcil/commit/670c662f9f62d07d5300c0772e712aac83141c06))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([ae0482d](https://gitlab.com/RadianDevCore/tools/gcil/commit/ae0482daecbb185c56aae83aae23998a508c665d))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([6c6248e](https://gitlab.com/RadianDevCore/tools/gcil/commit/6c6248e66fb14eeecb09846554fb0768aec91bb2))


<a name="10.1.0"></a>
## [10.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/10.0.1...10.1.0) (2024-08-21)

### 🐛 Bug Fixes

- **platform:** always flush on Windows hosts without stdout TTY ([df15142](https://gitlab.com/RadianDevCore/tools/gcil/commit/df15142848073134322784ed01a3a8ecc24f789c))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([d38b60a](https://gitlab.com/RadianDevCore/tools/gcil/commit/d38b60a0d9e5705885966462a74da424d9ccc42c))
- **readme:** migrate to 'RadianDevCore_gcil' project key ([a3df3aa](https://gitlab.com/RadianDevCore/tools/gcil/commit/a3df3aa4a7a8385848621d1b4dc5d25b2bddc75a))

### 🧪 Test

- **requirements:** raise 'pexpect-executor' version to 4.0.1 ([402d449](https://gitlab.com/RadianDevCore/tools/gcil/commit/402d44954e1fff72d22b4aa25a8d8dc8025f1d35))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([5a4a79d](https://gitlab.com/RadianDevCore/tools/gcil/commit/5a4a79dca973d3ec74f5c364f9c5396ddac264ee))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([ed32b81](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed32b817fd33c77edadd1a1394f8ee6041ba0471))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([870d6e3](https://gitlab.com/RadianDevCore/tools/gcil/commit/870d6e37d7f9a16d750f3141517913b61dda6009))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([6b72ff7](https://gitlab.com/RadianDevCore/tools/gcil/commit/6b72ff732a7a8063744cdec24d77bd91d6f07b22))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([75007ed](https://gitlab.com/RadianDevCore/tools/gcil/commit/75007edccb1435d24ad67f6398351175e220cd75))
- **sonar-project:** migrate to 'RadianDevCore_gcil' project key ([90b71f2](https://gitlab.com/RadianDevCore/tools/gcil/commit/90b71f2602bf2f0ee20a79a746a59d14bafd5fe7))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([134a95b](https://gitlab.com/RadianDevCore/tools/gcil/commit/134a95b64ef0697850df70437c0a8da34791f4e9))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([ff48dff](https://gitlab.com/RadianDevCore/tools/gcil/commit/ff48dff286ca9f2f2e110bff79a3098a4109d1d0))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([8d4ba5f](https://gitlab.com/RadianDevCore/tools/gcil/commit/8d4ba5f5a76e4e6e4ae02458ed3e4308b5fd0db5))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([847e1ae](https://gitlab.com/RadianDevCore/tools/gcil/commit/847e1ae277b9564ae62f60f39060335c4c18a176))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([4589793](https://gitlab.com/RadianDevCore/tools/gcil/commit/45897937b0f2104967921101241cf067ef4beceb))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([a1a724b](https://gitlab.com/RadianDevCore/tools/gcil/commit/a1a724b55e3f4eb45c7c70013e5cd3361814dc29))
- **gitlab-ci:** check only Python files in 'typings' job ([7b1e895](https://gitlab.com/RadianDevCore/tools/gcil/commit/7b1e89516c4b22dea1a12ecbbddc2125295ad64c))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([306b8a1](https://gitlab.com/RadianDevCore/tools/gcil/commit/306b8a176ed8ba2bd555ddc3cb182633f4c28e4e))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([326c02c](https://gitlab.com/RadianDevCore/tools/gcil/commit/326c02c02129fd78419a33dd754753a865c0ca9f))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([af4854d](https://gitlab.com/RadianDevCore/tools/gcil/commit/af4854d41fa905a71f205afff29607397732aba0))
- **gitlab-ci:** create 'hooks' local job for maintenance ([62cd96a](https://gitlab.com/RadianDevCore/tools/gcil/commit/62cd96a15a681c49d80ac0dcda33ee8204597d0f))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([2fed3fc](https://gitlab.com/RadianDevCore/tools/gcil/commit/2fed3fc35f9aa34ef8ab222fbaf142b7f0b5e59f))


<a name="10.0.1"></a>
## [10.0.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/10.0.0...10.0.1) (2024-08-16)

### 🐛 Bug Fixes

- **package:** fix package name for 'importlib' version detection ([07ada10](https://gitlab.com/RadianDevCore/tools/gcil/commit/07ada10c068fc0b26d46204fce1b3d47f596f6e4))

### 📚 Documentation

- **readme:** refresh SVG preview for latest 10.0.0 release ([f0eb20d](https://gitlab.com/RadianDevCore/tools/gcil/commit/f0eb20db7c7f450f73361da4dca08cc032ef3c68))

### ⚙️ Cleanups

- **hooks:** implement evaluators and matchers priority parser ([7d6a6d4](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d6a6d46de5b2af266549aa23b22a8e50858a078))


<a name="10.0.0"></a>
## [10.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/9.1.1...10.0.0) (2024-08-15)

### ✨ Features

- **cli:** refactor CLI commands calls into 'entrypoint.py' file ([0bdfcaf](https://gitlab.com/RadianDevCore/tools/gcil/commit/0bdfcaf1bad84f31c5234fcd7930119bd6191f99))
- **cli:** move '--no-color' to internal tools arguments ([fa51999](https://gitlab.com/RadianDevCore/tools/gcil/commit/fa51999d7f6b0a1a0c3b3873962dd216b86ec8e2))
- **gcil:** migrate under 'RadianDevCore/tools' group ([bc7ac72](https://gitlab.com/RadianDevCore/tools/gcil/commit/bc7ac72ef66396d38f85f945fa899dcb93286d2c))
- **gcil:** migrate project path to original project alias 'gcil' ([9195af2](https://gitlab.com/RadianDevCore/tools/gcil/commit/9195af24c058afa2237a5b3127436cc376f71965))
- **🚨 BREAKING CHANGE 🚨 |** **gcil:** migrate to 'gcil' entrypoint and 'gitlabci-local' alias ([ea12ef5](https://gitlab.com/RadianDevCore/tools/gcil/commit/ea12ef5ba736e51a93f45032b534ee1ce143ebdc))
- **main:** align 'RawTextHelpFormatter' to 23 chars columns ([3d6864e](https://gitlab.com/RadianDevCore/tools/gcil/commit/3d6864e4bd91f1586f0e75eb96fd8d48dad83258))
- **main:** limit '--help' width to terminal width or 120 chars ([16f3b7c](https://gitlab.com/RadianDevCore/tools/gcil/commit/16f3b7cb83a7a21d4102e99ba2a29ad0ef3f5f12))
- **main:** document optional '--' positional arguments separator ([7881593](https://gitlab.com/RadianDevCore/tools/gcil/commit/78815939fef51c5bd6630228fa1d32ee86115ed8))
- **requirements:** raise 'questionary' minimal version to 2.0.1 ([811efa9](https://gitlab.com/RadianDevCore/tools/gcil/commit/811efa9e245e7207c3901636da2e5bbc11295a71))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.6 ([ba930f8](https://gitlab.com/RadianDevCore/tools/gcil/commit/ba930f8f6fc367e85958b498132b98de1cb3c921))
- **setup:** add support for Python 3.12 ([9612bb9](https://gitlab.com/RadianDevCore/tools/gcil/commit/9612bb9f175a061fa7275dacfc670313cad65f95))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 due to 'questionary>=2.0.0' ([5cc9560](https://gitlab.com/RadianDevCore/tools/gcil/commit/5cc956010c784e4f54c58569f517dc25ff13cac3))

### 🐛 Bug Fixes

- **cli:** ensure 'Files.clean' is called before exiting entrypoint ([a686405](https://gitlab.com/RadianDevCore/tools/gcil/commit/a6864050f3610803248a1ea45df9c809c8342544))
- **gitlab:** resolve 'possibly-used-before-assignment' warning ([b17d4f5](https://gitlab.com/RadianDevCore/tools/gcil/commit/b17d4f5edfd80455ffe21dd6800c25978d50b52b))
- **gitlab:** resolve '.local: version' SemVer versions comparisons ([eed23ea](https://gitlab.com/RadianDevCore/tools/gcil/commit/eed23ea58c48e55ae26c4292c94eb0999e7c3b4d))
- **gitlab-ci, package, tests:** refactor into 'DEBUG_UPDATES_*' ([60aa866](https://gitlab.com/RadianDevCore/tools/gcil/commit/60aa866e5b0fb55f262951ebd6a8bb5e57408775))
- **menus:** handle 'KeyboardInterrupt' exception from 'questionary' ([f08f567](https://gitlab.com/RadianDevCore/tools/gcil/commit/f08f5674c9d77898d00d85f5cb4a01abbc1ac025))
- **package, tests:** refactor into 'DEBUG_VERSION_FAKE' ([16933a0](https://gitlab.com/RadianDevCore/tools/gcil/commit/16933a0b415c1ab3f618eca560c7bac07fd7b19a))
- **parsers:** ignore recommended version if running from sources ([a4db3c6](https://gitlab.com/RadianDevCore/tools/gcil/commit/a4db3c60d5cc7bb261f907a9a741efb28fd13a98))
- **settings:** ensure 'Settings' class initializes settings file ([a305663](https://gitlab.com/RadianDevCore/tools/gcil/commit/a3056637be985b85508132320becfd6ff8bd2e0c))
- **setup:** refactor 'python_requires' versions syntax ([d3f5bb7](https://gitlab.com/RadianDevCore/tools/gcil/commit/d3f5bb77534d2c3808a748d3a9f09549956f19ec))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 due to 'questionary>=2.0.0' ([7fbb38d](https://gitlab.com/RadianDevCore/tools/gcil/commit/7fbb38d8a18492d12ca458107e26f7da05ff0a2f))
- **setup:** resolve project package and name usage ([cf3f866](https://gitlab.com/RadianDevCore/tools/gcil/commit/cf3f866830901191509fdc40e396b1d6b53b387f))
- **src:** use relative module paths in '__init__' and '__main__' ([857630a](https://gitlab.com/RadianDevCore/tools/gcil/commit/857630a8574734a115d2367a7bc15b59dd5df311))
- **src:** check empty 'environ' values before usage ([4b037c0](https://gitlab.com/RadianDevCore/tools/gcil/commit/4b037c05d97928b267ac6598653265ae122d2369))
- **src:** resolve more Python typings issues ([6aa9d70](https://gitlab.com/RadianDevCore/tools/gcil/commit/6aa9d70e75ca70a9cab059dbc1e18f62964b66fe))
- **src:** refactor jobs parsers into models with Python typings ([11674c5](https://gitlab.com/RadianDevCore/tools/gcil/commit/11674c5ea9cb3853428fcbba736c3521d2ebdb9d))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([87a4192](https://gitlab.com/RadianDevCore/tools/gcil/commit/87a419213d96ad762e3fbeae795f3a8fca57f93f))
- **updates:** fix offline mode and SemVer versions comparisons ([8a612c8](https://gitlab.com/RadianDevCore/tools/gcil/commit/8a612c8fa36d2268f2a09549650724bdc1b3ac64))

### 🚜 Code Refactoring

- **src:** isolate all sources under 'src/' ([bdc4967](https://gitlab.com/RadianDevCore/tools/gcil/commit/bdc4967bde6c9493d6028aa2a94bcf29ddf91771))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([c0a937a](https://gitlab.com/RadianDevCore/tools/gcil/commit/c0a937a2e815a6c757ef6caffb349863bc17638e))
- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([e116bb5](https://gitlab.com/RadianDevCore/tools/gcil/commit/e116bb5c8b525174d1673555ca0f8befccf58555))
- **gitlab-ci, preview:** migrate from 'gitlabci-local' to 'gcil' ([9c47875](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c4787538a6f71860ede9ce0531d1ba08b83b899))
- **license:** update copyright details for 2020-2024 ([4f8fd73](https://gitlab.com/RadianDevCore/tools/gcil/commit/4f8fd73ba75e75de8f0b8ba0c340aebafda7a9d1))
- **readme:** refresh 'README.md' help informations ([40972d2](https://gitlab.com/RadianDevCore/tools/gcil/commit/40972d245776d1fdaa935cddd617452eb41f5763))
- **readme:** add 'Commitizen friendly' badge ([f47adf8](https://gitlab.com/RadianDevCore/tools/gcil/commit/f47adf8d667467f7a0e413a7388895ecd8385808))
- **readme, test:** migrate names from 'gitlabci-local' to 'gcil' ([faa919d](https://gitlab.com/RadianDevCore/tools/gcil/commit/faa919d9bd8071a817f4c4692e017238555287a1))
- **setup:** migrate project name from 'gitlabci-local' to 'gcil' ([b4ed553](https://gitlab.com/RadianDevCore/tools/gcil/commit/b4ed553f81289ad84456f626e1be47361d9ed610))
- **setup:** add 'gitlabci-local' to project keywords hint ([fd9db20](https://gitlab.com/RadianDevCore/tools/gcil/commit/fd9db2058f6eef18dc38e1a32da4f598bf5eee3d))
- **setup:** add 'gitlab' to project keywords hint ([7208d5a](https://gitlab.com/RadianDevCore/tools/gcil/commit/7208d5a70d1d94eeb14cf65821b19c8c4f501282))
- **sonar-project:** use 'gcil' name as SonarCloud project title ([f90ce40](https://gitlab.com/RadianDevCore/tools/gcil/commit/f90ce400126b980bda6b7ba32d7cd08bfdf4a8fd))

### ⚡ Performance Improvements

- **src:** load heavy Python modules only upon use for faster launch ([1b632f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b632f3fad123cf36170bddbfeeb2155419f98de))

### 🎨 Styling

- **cli:** refactor codestyle and cleanup 'add_argument' syntaxes ([f1cadfc](https://gitlab.com/RadianDevCore/tools/gcil/commit/f1cadfc28c8262747144a3b5dde96e600bc1166b))
- **cli:** improve Python arguments codestyle syntax ([d8c758a](https://gitlab.com/RadianDevCore/tools/gcil/commit/d8c758a6f127ccd618c09f234421289e31bee882))
- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([2754b27](https://gitlab.com/RadianDevCore/tools/gcil/commit/2754b271e58c8cdeec0b7e3e6a64c53b02ca2732))
- **features:** improve Python arguments codestyle syntax ([91b1824](https://gitlab.com/RadianDevCore/tools/gcil/commit/91b18241cd2f4951668677717ef4a88e1f471533))
- **files:** minor Python codestyle improvements to 'Files' class ([2530b48](https://gitlab.com/RadianDevCore/tools/gcil/commit/2530b485f4dac1555ef62db6847f1d9385b626d2))
- **jobs:** improve Python arguments codestyle syntax ([3d90826](https://gitlab.com/RadianDevCore/tools/gcil/commit/3d908266255c1a32471d17e91d1017bbd623234f))
- **parsers:** improve Python arguments codestyle syntax ([fd5ada7](https://gitlab.com/RadianDevCore/tools/gcil/commit/fd5ada7424d76af405fa53f6653dbe8ef835e911))
- **pre-commit:** implement 'pre-commit' configurations ([a561ed9](https://gitlab.com/RadianDevCore/tools/gcil/commit/a561ed92a7906e615a98efc019a66c8364dc483b))
- **updates:** ignore coverage of online updates message ([6e32064](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e32064117d95c6bffcc22ef732ba81d8658ab96))

### 🧪 Test

- **console:** resolve '--bash' interactive test timeout times ([d28a834](https://gitlab.com/RadianDevCore/tools/gcil/commit/d28a8341f1b43d84210c680213653c47418e9b6c))
- **interruptions:** add coverage of 'Ctrl+C' job interruptions ([64f57b8](https://gitlab.com/RadianDevCore/tools/gcil/commit/64f57b853977223fe25eed4b6993807ce1d6de60))
- **interruptions:** add coverage of 'Skipped (Interrupted)' job log ([660728d](https://gitlab.com/RadianDevCore/tools/gcil/commit/660728d93ebbd97a9e7f97454ccff2ca64b0db01))
- **menus:** ignore 'Ctrl+C' rare failures upon CI tests executions ([32c4651](https://gitlab.com/RadianDevCore/tools/gcil/commit/32c46518d9b1ea7f6a3affc75e667de679c3e8d2))
- **parallel:** fix missing coverage of 'environ' value access ([00abd64](https://gitlab.com/RadianDevCore/tools/gcil/commit/00abd648e64921741a5eed3bb143042506af1747))
- **permissions:** avoid unsafe user permissions bypass and test ([adad192](https://gitlab.com/RadianDevCore/tools/gcil/commit/adad19269ec885b43199d8e3f7b0f16e774d8fdd))
- **requirements:** raise 'pexpect-executor' minimal version to 3.0.2 ([dc232b7](https://gitlab.com/RadianDevCore/tools/gcil/commit/dc232b76b32b4ebe1f5c3ba1065824c3eaaa97de))
- **requirements:** raise 'pexpect-executor' minimal version to 3.1.0 ([0f337ff](https://gitlab.com/RadianDevCore/tools/gcil/commit/0f337ff1e9402e7293f9472fd4db4853e982a3fc))
- **setup:** disable sources coverage of the build script ([dcc51fe](https://gitlab.com/RadianDevCore/tools/gcil/commit/dcc51fed2fd65c28e12fb676ce9faec03cbf57be))
- **sockets:** reset 'entrypoint' over 'docker:latest' images ([d74ac5f](https://gitlab.com/RadianDevCore/tools/gcil/commit/d74ac5f28df66d9ace93bb5aa4a452ed4f8ae7f6))
- **sockets:** rehost 'docker:27-dind' and use it for specific image ([f7337fe](https://gitlab.com/RadianDevCore/tools/gcil/commit/f7337fe4a826ba91d5093219de195519e78411d1))
- **tests:** migrate from 'gitlabci-local' to 'gcil' in tests ([532a0a8](https://gitlab.com/RadianDevCore/tools/gcil/commit/532a0a804afd64f063da2b7e659ffea2224086cc))
- **windows:** avoid failing upon 'where.exe' as WinPTY fake test ([985f474](https://gitlab.com/RadianDevCore/tools/gcil/commit/985f4747bd34664c2b329591ab7a0c444a5f450f))
- **workdir:** fix 'Job 2' job faulty name quotes ([7461676](https://gitlab.com/RadianDevCore/tools/gcil/commit/7461676cb8e1fa6e33d14d1f9bd092f2cf9e1926))

### ⚙️ Cleanups

- **colors:** resolve 'pragma: no cover' detection ([ac292f5](https://gitlab.com/RadianDevCore/tools/gcil/commit/ac292f597594a3b30017a7fc17793cb888094030))
- **coveragerc:** ignore 'preview.py' and 'setup.py' from coverage ([e4a768a](https://gitlab.com/RadianDevCore/tools/gcil/commit/e4a768a284acd22ddfc5966bd15bd2e08cea5c99))
- **dicts:** minor codestyle typings improvements ([ca15a74](https://gitlab.com/RadianDevCore/tools/gcil/commit/ca15a744b04da572312e9cc336213912a65cff04))
- **docs:** ignore 'line-too-long' warning over URL strips ([7b9ee32](https://gitlab.com/RadianDevCore/tools/gcil/commit/7b9ee32c9dfe3c35a5311130ed1c049623e77e64))
- **docs, setup:** remove faulty '# pragma: exclude file' flag ([5ed94fa](https://gitlab.com/RadianDevCore/tools/gcil/commit/5ed94faf35c29b042e413adbad34c5fd08ab24bd))
- **entrypoint:** merge 'options.pipeline' and 'options.names' ([4c613f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c613f08700dd9a41a11265af12c9f557b475e3d))
- **examples, tests:** add missing new line endings to all files ([1c3be04](https://gitlab.com/RadianDevCore/tools/gcil/commit/1c3be04fb153d5a77ca9683af7cd4dd8e77538a1))
- **files:** ignore coverage of 'kill(getpid(), ...)' call at exit ([93122b2](https://gitlab.com/RadianDevCore/tools/gcil/commit/93122b29a88497178e71d5783d4ed8e3d2edeed0))
- **gitlab, variables:** resolve nested if 'python:S1066' warnings ([276e3b7](https://gitlab.com/RadianDevCore/tools/gcil/commit/276e3b78ed1ee65b4326af07c65821b54bff305c))
- **mypy:** convert 'mypy.ini' configuration to Linux EOL ([fdbf4a9](https://gitlab.com/RadianDevCore/tools/gcil/commit/fdbf4a9e46c9a7cb2020c604eb5761b572c70dcc))
- **platform:** disable coverage of 'SUDO' without write access ([3f3830b](https://gitlab.com/RadianDevCore/tools/gcil/commit/3f3830b9923ce4b15405b129981bcef926da31a4))
- **pre-commit:** disable 'check-xml' unused hook ([ff60937](https://gitlab.com/RadianDevCore/tools/gcil/commit/ff6093793dbae07d802401da4b3e5293af85b682))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([eadd1f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/eadd1f09a698d744ce3c33f67fc2d8db295da955))
- **runner:** ignore coverage of '__GITLAB_CI_LOCAL_DEBUG__' output ([e723718](https://gitlab.com/RadianDevCore/tools/gcil/commit/e7237182c913f27170d7d5462987fa0951d9be4d))
- **setup:** refactor with more project configurations ([68737b1](https://gitlab.com/RadianDevCore/tools/gcil/commit/68737b1939de2fa98e9445cebcca25c9dbb00995))
- **sonar-project:** migrate 'sonar.sources' to 'src' sources ([7673a49](https://gitlab.com/RadianDevCore/tools/gcil/commit/7673a4901d0c33a56806810b59d5eadbf7d1db7b))
- **sonar-project:** remove 'docs' and 'setup.py' sources coverage ([0fb1ef1](https://gitlab.com/RadianDevCore/tools/gcil/commit/0fb1ef1eb95616e23b0ef09d48f3d22660720ec6))
- **src:** ignore 'import-error' over '__init__' and '__main__' ([96fba1f](https://gitlab.com/RadianDevCore/tools/gcil/commit/96fba1f5bff959f40790f5b15050097ef1175bd2))
- **types/yaml:** disable coverage of nested references limitations ([67f5cad](https://gitlab.com/RadianDevCore/tools/gcil/commit/67f5cadcdb3e9211052f6392c4146f2fe7e1ed6c))
- **vscode:** remove illegal comments in 'extensions.json' ([a6afe1a](https://gitlab.com/RadianDevCore/tools/gcil/commit/a6afe1ac96ef6a9af2107e519c556245e3e72cde))

### 🚀 CI

- **gitlab:** support '-p VALUE, --parameter VALUE' in 'readme' job ([1056ac7](https://gitlab.com/RadianDevCore/tools/gcil/commit/1056ac7881204559718d7366ed254c8e3822de7d))
- **gitlab:** configure Git sources safeties for 'sonarcloud' job ([f248f7f](https://gitlab.com/RadianDevCore/tools/gcil/commit/f248f7fa00a83e6750257a44d28f4e4d4eaa5da1))
- **gitlab-ci:** ignore 'docker rmi' local failures if already in use ([e4a859a](https://gitlab.com/RadianDevCore/tools/gcil/commit/e4a859afb93483ed9612b34055336ce6d75c9185))
- **gitlab-ci:** remove 'image:' unused global declaration ([b2b971e](https://gitlab.com/RadianDevCore/tools/gcil/commit/b2b971ee810a125963b951a7ee6085f665f62c26))
- **gitlab-ci:** disable 'typing' mypy caching with 'MYPY_CACHE_DIR' ([a279e82](https://gitlab.com/RadianDevCore/tools/gcil/commit/a279e8252cb0143ec0b72c8841f48d3ced63b8d1))
- **gitlab-ci:** implement 'readme' local job to update README details ([11d30c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/11d30c263414964544583a41abd96e3572e5210d))
- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([78e4a00](https://gitlab.com/RadianDevCore/tools/gcil/commit/78e4a00d990d53565e13afcf53ac1dc2ff5e3d89))
- **gitlab-ci:** change commit messages to tag name ([3ecee97](https://gitlab.com/RadianDevCore/tools/gcil/commit/3ecee971adba46895a24a70153d338b916ab9538))
- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([165b23c](https://gitlab.com/RadianDevCore/tools/gcil/commit/165b23c32cfcffedf26ee3fea0559b0e3f944265))
- **gitlab-ci:** support docker pull and push without remote ([49dbcea](https://gitlab.com/RadianDevCore/tools/gcil/commit/49dbceae310e04a74bcead9d58c3c37a197fc719))
- **gitlab-ci:** fix 'coverage:*' jobs for module sources in 'src' ([bcc7c9c](https://gitlab.com/RadianDevCore/tools/gcil/commit/bcc7c9c60bd755d114eade8a7cb71cd862b842c3))
- **gitlab-ci:** install 'util-linux-misc' for 'more' in preview image ([3a54a08](https://gitlab.com/RadianDevCore/tools/gcil/commit/3a54a08ca3b85496177f8603b40dcf2e1c8b8977))
- **gitlab-ci:** enable 'PYTHONUNBUFFERED' in 'preview' to unbuffer outputs ([b33aebc](https://gitlab.com/RadianDevCore/tools/gcil/commit/b33aebc73f0b50e5faa9e0285044e1dd7b9896da))
- **gitlab-ci:** enable 'PYTHONUNBUFFERED' in tests to unbuffer outputs ([575b7c1](https://gitlab.com/RadianDevCore/tools/gcil/commit/575b7c17064adf25ffcdd9a858c51576b0f158bb))
- **gitlab-ci:** migrate Windows tests to Python 3.10 using 'pywine:3.10' ([ff6c186](https://gitlab.com/RadianDevCore/tools/gcil/commit/ff6c186f7be09cef017bc95936bce9eb6557187b))
- **gitlab-ci:** migrate to 'pipx' installations on hosts tests ([684f745](https://gitlab.com/RadianDevCore/tools/gcil/commit/684f745c987c34fe400b707abe39a4779c3f2861))
- **gitlab-ci:** ignore 'docker rm' command result codes ([c4a5617](https://gitlab.com/RadianDevCore/tools/gcil/commit/c4a5617793365a40b83f1f5f1b6173076d2edebb))
- **gitlab-ci:** raise oldest Python test images from 3.6 to 3.7 ([eae00a6](https://gitlab.com/RadianDevCore/tools/gcil/commit/eae00a65feba64d561726b64b905905833c24480))
- **gitlab-ci:** define 'DOCKER_TLS_CERTDIR' to default empty value ([dab3fab](https://gitlab.com/RadianDevCore/tools/gcil/commit/dab3fab368e8001da757c52f952977a070b41e8f))
- **gitlab-ci:** revert to Docker in Docker without TLS certificates ([8fcd8e3](https://gitlab.com/RadianDevCore/tools/gcil/commit/8fcd8e3d69b8b1a9a11924a584f8fbb9cd6e7d2c))
- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([db7705c](https://gitlab.com/RadianDevCore/tools/gcil/commit/db7705c3e625413decc7e414822262fdc75ad061))
- **gitlab-ci:** raise oldest Python test images from 3.7 to 3.8 ([9299f27](https://gitlab.com/RadianDevCore/tools/gcil/commit/9299f27bacc68769fbb17a4076e9d49e64dc386e))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([8a5f29c](https://gitlab.com/RadianDevCore/tools/gcil/commit/8a5f29c8218ef3e343a70241ec97418a60b3181f))
- **gitlab-ci:** install 'bash' in the ':preview' image ([850da49](https://gitlab.com/RadianDevCore/tools/gcil/commit/850da49986d159ba8f1be800c2d1cb0992cf37a9))
- **gitlab-ci:** remove 'DOCKER_TLS_VERIFY' value for disabled state ([df93567](https://gitlab.com/RadianDevCore/tools/gcil/commit/df93567a5684fa5f98d922d13b49d1e779644d89))
- **gitlab-ci:** migrate to Docker in Docker with TLS certificates ([813733e](https://gitlab.com/RadianDevCore/tools/gcil/commit/813733e7f151fdf634eefa14365edaa953928311))
- **gitlab-ci:** set 'FORCE_COLOR' and 'USER' for 'preview' job ([443fbb8](https://gitlab.com/RadianDevCore/tools/gcil/commit/443fbb8c776e6777ecfb93c1c63723219324e333))
- **gitlab-ci:** install 'docker' CLI packages in Docker tests images ([899ec54](https://gitlab.com/RadianDevCore/tools/gcil/commit/899ec54502ae7de18466cb53a0a76506e89745dc))
- **gitlab-ci:** raise unit tests jobs timeout to 25 minutes ([127329f](https://gitlab.com/RadianDevCore/tools/gcil/commit/127329f92108552a75afa3558ee42912089cfdb8))
- **gitlab-ci:** watch for 'codestyle' and 'lint' jobs success ([27c49f8](https://gitlab.com/RadianDevCore/tools/gcil/commit/27c49f891eabc489b1cea62ec732152992902961))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([0b032f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b032f3750cbbe39080557451d55e8613333b5bc))
- **gitlab-ci:** watch for 'typings' job success ([dc9fbbf](https://gitlab.com/RadianDevCore/tools/gcil/commit/dc9fbbf065fa11b3a40587b50adae5a0ddbbeb47))
- **gitlab-ci:** disable 'PYTHONDONTWRITEBYTECODE' for 'coverage:*' tests ([686540e](https://gitlab.com/RadianDevCore/tools/gcil/commit/686540e0843b08fc1a72f4de92835ad4a5346ac5))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([aed8f31](https://gitlab.com/RadianDevCore/tools/gcil/commit/aed8f316b79eb3f2716bd31a1333c0953185c274))
- **gitlab-ci, README, setup:** migrate to 'main' delivery branch ([07bfc3f](https://gitlab.com/RadianDevCore/tools/gcil/commit/07bfc3f2bf80042885df712fddc91708a4306f23))
- **gitlab-ci, setup:** migrate to 'src' sources management ([7cbe17d](https://gitlab.com/RadianDevCore/tools/gcil/commit/7cbe17d9f976a4e3d3e56640f7d9decdfa731180))
- **gitlab-ci, tests:** use rehosted 'docker:dind' image for tests ([e4dcbdf](https://gitlab.com/RadianDevCore/tools/gcil/commit/e4dcbdfc7d562009405ccfb97cf47fae0cab5fd8))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([e7214a0](https://gitlab.com/RadianDevCore/tools/gcil/commit/e7214a04e3650b97188b8d0938a741143a9e9157))
- **hooks:** implement 'prepare-commit-msg' template generator ([1f6ac50](https://gitlab.com/RadianDevCore/tools/gcil/commit/1f6ac503f37e8c248f1ede6cbbfa8f499331777b))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([345b8b9](https://gitlab.com/RadianDevCore/tools/gcil/commit/345b8b912a8cb6fa4e40ce6b5d4f05e685bfb47d))


<a name="9.1.1"></a>
## [9.1.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/9.1.0...9.1.1) (2024-04-21)

### 📚 Documentation

- **setup:** resolve 'Statistics' URL for PyPI documentation ([53faf0c](https://gitlab.com/RadianDevCore/tools/gcil/commit/53faf0c5ca315e89baaad07ac93bdff968c195ce))

### ⚙️ Cleanups

- **run.sh:** minor sed readability codestyle improvements ([11ac316](https://gitlab.com/RadianDevCore/tools/gcil/commit/11ac316067503cfa2c68b9094fb83755653eab6d))

### 🚀 CI

- **gitlab-ci:** create 'clean' local cleanup job with 'sudo' ([06c0341](https://gitlab.com/RadianDevCore/tools/gcil/commit/06c0341777120f0b96035830dd710a151702a5fa))
- **gitlab-ci:** explicit 'docker' service and isolate 'DOCKER_HOST' ([2c409fe](https://gitlab.com/RadianDevCore/tools/gcil/commit/2c409fe9f9a70f4f8ad5300acc280c509e47f1e4))
- **gitlab-ci:** use '/certs/client' TLS certificates from DinD ([3400ea4](https://gitlab.com/RadianDevCore/tools/gcil/commit/3400ea4dbafa0cd3d53216118d3d2ced50ff8bf2))
- **gitlab-ci:** fail 'typings' job if latest changes raise warnings ([86e302c](https://gitlab.com/RadianDevCore/tools/gcil/commit/86e302c71a3f04c3dc23aec4b0dfd373b7654877))
- **gitlab-ci:** resolve 'typings' job for newly created sources ([a81953c](https://gitlab.com/RadianDevCore/tools/gcil/commit/a81953cb84dd946d4660b36d7ac18607fea6c273))


<a name="9.1.0"></a>
## [9.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/9.0.0...9.1.0) (2023-12-10)

### ✨ Features

- **histories:** prepare #273 by improving interrupted jobs history ([e39204f](https://gitlab.com/RadianDevCore/tools/gcil/commit/e39204f5c57a48a4562b0e30d5797a9f4c4720e3))
- **runner:** prepare #273 by parsing runner script real result ([ca22713](https://gitlab.com/RadianDevCore/tools/gcil/commit/ca227130e9d8d6236504320874d04b43b847f686))
- **runner:** implement #273 by using script result if interrupted ([a789afc](https://gitlab.com/RadianDevCore/tools/gcil/commit/a789afcbff922edf440d774caf372457f930acce))

### 🐛 Bug Fixes

- **parsers:** resolve #272 with parameters values in 'matrix' ([6e26997](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e26997f50bc66bd4cb7030ce5d33a3886f4a947))
- **parsers:** resolve #271 through 'matrix' string values support ([a2cd938](https://gitlab.com/RadianDevCore/tools/gcil/commit/a2cd938c41fb803aa6b558b02b9096b87edd2bdf))
- **podman:** resolve #274 by handling empty 'stdout' results ([725b3c5](https://gitlab.com/RadianDevCore/tools/gcil/commit/725b3c51fe8671f9d991d1b41c678ec755caaa53))

### 🧪 Test

- **console:** finish #273 by testing '--debug' success results ([4130ac4](https://gitlab.com/RadianDevCore/tools/gcil/commit/4130ac43488b6be65894e301abeb4dcd992dc405))
- **console:** finish #273 by accepting 'SIGTERM' result code ([28a771d](https://gitlab.com/RadianDevCore/tools/gcil/commit/28a771de2315fd70214c9b25e8a92a0c332e4ca1))
- **console, notify, simple:** kill after timeout in '--{bash,debug}' ([0ef04e9](https://gitlab.com/RadianDevCore/tools/gcil/commit/0ef04e956ecf14fd754b7cf073780da0f175b76b))
- **parallel:** prepare #272 by fixing missing error detection ([4246a0a](https://gitlab.com/RadianDevCore/tools/gcil/commit/4246a0a04ac8020476f77afc66a5f8184868b964))

### ⚙️ Cleanups

- **run.sh:** refactor with multiple jobs input support ([20fc0d7](https://gitlab.com/RadianDevCore/tools/gcil/commit/20fc0d769204cc92206cf4c3e9d9af868ef9086d))
- **runner:** add missing empty lines in the runner jobs' scripts ([02e3d2d](https://gitlab.com/RadianDevCore/tools/gcil/commit/02e3d2dc0b2df22d325d949525a5246a314f126f))
- **vscode:** configure 'shc' Shell scripts formatting options ([4688850](https://gitlab.com/RadianDevCore/tools/gcil/commit/46888507069f6d7c48fad99bfa71602f30d9323c))

### 🚀 CI

- **gitlab-ci:** uninstall current package first in 'development' ([a6166a1](https://gitlab.com/RadianDevCore/tools/gcil/commit/a6166a1d138bf3fbe5abbd424f7c4d009fb37239))
- **gitlab-ci:** fix stage for 'install' local installation job ([6bc6202](https://gitlab.com/RadianDevCore/tools/gcil/commit/6bc6202f6d95a83393c95f51729bd58d0286d2ec))
- **gitlab-ci:** migrate from 'only: local' to 'rules: if: $CI_LOCAL' ([dc10f86](https://gitlab.com/RadianDevCore/tools/gcil/commit/dc10f8695f8580fc76c2afa7e588f4baf4c17b2d))
- **gitlab-ci:** migrate from './setup.py' to 'python3 -m build' ([da65744](https://gitlab.com/RadianDevCore/tools/gcil/commit/da6574479f4662cc933d723ec8bdbab27564dbb4))
- **gitlab-ci:** deprecate 'development' for 'build' + 'install' ([cdc2b50](https://gitlab.com/RadianDevCore/tools/gcil/commit/cdc2b50cad38584a46dabeeeb478ac2e642eec2d))
- **gitlab-ci:** deprecate 'dependencies' job using pip3 install ([05a2a33](https://gitlab.com/RadianDevCore/tools/gcil/commit/05a2a331aec40ae3491b6e12b4966b67e3f5ad96))
- **gitlab-ci:** migrate 'deploy:*' from 'dependencies:' to 'needs:' ([5752fb9](https://gitlab.com/RadianDevCore/tools/gcil/commit/5752fb96c16a599a52e4382eed102136a77e42e9))
- **gitlab-ci:** create specific 'codestyle' image for 'prepare' jobs ([d5bb596](https://gitlab.com/RadianDevCore/tools/gcil/commit/d5bb596294089733320ad0cdf6f22966399a4522))
- **gitlab-ci:** create specific 'build' image for 'build' job ([7a30d9a](https://gitlab.com/RadianDevCore/tools/gcil/commit/7a30d9a2f8a51d5064397b3cc3231e52d59eaf35))
- **gitlab-ci:** create specific 'deploy' image for 'deploy' jobs ([80c8865](https://gitlab.com/RadianDevCore/tools/gcil/commit/80c886545268c16ee761d765879c455107142498))
- **gitlab-ci:** migrate from YAML '&/*' anchors to CI '!reference' ([461af5e](https://gitlab.com/RadianDevCore/tools/gcil/commit/461af5e35bae14222787645f47cf545c65d07167))
- **gitlab-ci:** disable pip cache directory in built images ([6c7ea42](https://gitlab.com/RadianDevCore/tools/gcil/commit/6c7ea42c3203f954d6508d0e1aba1208056f991f))
- **gitlab-ci:** allow using 'IMAGE' variable to filter 'images' ([e57557d](https://gitlab.com/RadianDevCore/tools/gcil/commit/e57557d6b9ef9b943e4bf5c75fb6b088f2096130))
- **gitlab-ci:** pull the previously built images first in 'images' ([9078cad](https://gitlab.com/RadianDevCore/tools/gcil/commit/9078cadf3cbbe45abd4297719b0f1e2c1b171779))
- **gitlab-ci:** install 'docs' and 'tests' requirements in ':preview' ([5c79dfd](https://gitlab.com/RadianDevCore/tools/gcil/commit/5c79dfd00e6d04e31b02678d406598af7739c932))
- **gitlab-ci:** refactor all 'test' jobs into prebuilt images ([9731083](https://gitlab.com/RadianDevCore/tools/gcil/commit/97310838a8dae83af282e5770fe38a590ecf6742))
- **gitlab-ci:** add missing 'needs' sequences for 'deploy:*' jobs ([7d7a099](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d7a099238572c8d9945cd0e65100b2e628dd7b1))
- **gitlab-ci:** migrate changelog commit to 'docs(changelog):' type ([8a0166e](https://gitlab.com/RadianDevCore/tools/gcil/commit/8a0166e74393d7013c42117dfe23c4149009356d))


<a name="9.0.0"></a>
## [9.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/8.1.0...9.0.0) (2023-12-03)

### ✨ Features

- **jobs:** implement #267 by adding 'CI_JOB_NAME_SLUG' variable ([71160f2](https://gitlab.com/RadianDevCore/tools/gcil/commit/71160f2d3f62450d8ee470ed21516f265ddf6bf8))
- **jobs, parsers:** implement #269 with 'CI_BUILDS_DIR' as parent dir ([250617b](https://gitlab.com/RadianDevCore/tools/gcil/commit/250617b6d2b041357467f2b4c6053576d9f42baf))
- **package:** implement #262 through 'pipx' update support ([7487420](https://gitlab.com/RadianDevCore/tools/gcil/commit/748742069c45300066c2975ec5d9bdb27cca0da5))

### 🐛 Bug Fixes

- **parsers:** resolve #270 with global 'image: variables expansion ([2f236f9](https://gitlab.com/RadianDevCore/tools/gcil/commit/2f236f9a833e6f23c60359ff7a8a85dd7d6534c7))
- **parsers:** finish #270 through preserved applied environment ([9953e7d](https://gitlab.com/RadianDevCore/tools/gcil/commit/9953e7d655f3106c395e302931d5ef2f2d46394d))
- **parsers:** resolve #270 by expanding jobs 'tags' lists ([263f10f](https://gitlab.com/RadianDevCore/tools/gcil/commit/263f10f69921df63a4bbc0e954798485eb19fc98))

### 📚 Documentation

- **preview:** deprecate preview of the 'configurations' features ([7d1112f](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d1112fb2db1c0c62afd75073916a5a622469bfe))
- **preview:** improve timings and transitions of the preview ([848326f](https://gitlab.com/RadianDevCore/tools/gcil/commit/848326f4719dd2060fd1c142a45e8e371dbda16d))
- **preview:** add '--bash' and '--debug' preview examples ([9fc5558](https://gitlab.com/RadianDevCore/tools/gcil/commit/9fc5558e4dd3ea22b393191839c4f336c7b04b4d))
- **readme:** improve the documentation and parameters readability ([b96483f](https://gitlab.com/RadianDevCore/tools/gcil/commit/b96483fcbcd01c025005ddf05eaa1c001578d3b0))
- **test:** prepare #262 by using 'pipx' for local installs ([5e05ff9](https://gitlab.com/RadianDevCore/tools/gcil/commit/5e05ff96350eeb6d3cb7e5f9b809f966b68db25e))
- **test:** fix URL links codestyle with Markdown syntax ([732460a](https://gitlab.com/RadianDevCore/tools/gcil/commit/732460adc1ac4415228aa04e684df8064b766c16))
- changelog: regenerate release tag changes history ([66f8fd3](https://gitlab.com/RadianDevCore/tools/gcil/commit/66f8fd3cd0c3e8f81825864a1955bcaf3208b828))

### 🧪 Test

- **examples:** fix duplicated 'Job 3 - 4' job name ([99b8f3b](https://gitlab.com/RadianDevCore/tools/gcil/commit/99b8f3b01c8a66c365882970655be80e677f1f74))
- **examples:** resolve #255 by migrating to templates 'extends' ([3221c10](https://gitlab.com/RadianDevCore/tools/gcil/commit/3221c10b60807e339d0bef9a33dd15b5df5a6262))
- **examples:** reduce the amount of jobs and simplify for preview ([43394a5](https://gitlab.com/RadianDevCore/tools/gcil/commit/43394a56b8697547c25fa5bfb0a2e48dee0b3043))
- **sockets:** allow 'mirror.gcr.io' unreliable pulls to fail ([e559a85](https://gitlab.com/RadianDevCore/tools/gcil/commit/e559a85df5ed5338920fea585062e829f85ee585))
- **sockets:** use the self-hosted 'docker:dind' image instead ([7716b30](https://gitlab.com/RadianDevCore/tools/gcil/commit/7716b300208655c3d76e72d4041e4666b80f441e))
- **variables:** test #270 with global 'image:' variables usage ([497246c](https://gitlab.com/RadianDevCore/tools/gcil/commit/497246c2d9c0060177f1dc6615ea75410606e55a))

### ⚙️ Cleanups

- **jobs:** finish #267 with minor Python codestyle improvement ([a140b6b](https://gitlab.com/RadianDevCore/tools/gcil/commit/a140b6b1bfcd363af1aad2212af656f8133248e1))
- **package:** finish #262 by ignoring lines coverage checks ([c385922](https://gitlab.com/RadianDevCore/tools/gcil/commit/c38592243d4b4b28493dbee3a0bc80963d47b1c8))
- **parsers, types:** minor Python typings syntax improvements ([7b8dc49](https://gitlab.com/RadianDevCore/tools/gcil/commit/7b8dc49f4c4e83093e55c44d5ea52c7d4d4ab98b))
- **run:** migrate to 'group:name' job names without quotes ([2c75e90](https://gitlab.com/RadianDevCore/tools/gcil/commit/2c75e903934ef4ef4d430cb75bafccd042ccda50))

### 🚀 CI

- **chglog:** allow 'ci' as 'CI' Conventional Commits types ([47854f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/47854f0a2dc512cb9dd8fd38c6f5233206a424a7))
- **gitlab-ci:** migrate 'git-chglog' from 0.9.1 to 0.15.4 ([3c2aaf3](https://gitlab.com/RadianDevCore/tools/gcil/commit/3c2aaf3d3791531f14e52709854b62397ad4595d))
- **gitlab-ci:** hide 'Typings' permanent failed errors as warnings ([0b01d6c](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b01d6c8d80f2e3a433a54e8f078799ef485ec0f))
- **gitlab-ci:** raise minimal 'gitlabci-local' version to 8.0 ([16dfe58](https://gitlab.com/RadianDevCore/tools/gcil/commit/16dfe586c0748e4c6263c323c1eb6683e71fcb16))
- **gitlab-ci:** refactor jobs names lowercase and 'group:name' ([37563c1](https://gitlab.com/RadianDevCore/tools/gcil/commit/37563c18e72e25a863299ebfc0afea05ae2385fe))
- **gitlab-ci:** create 'gitlabci-local:preview' image with 'docker' ([749c62b](https://gitlab.com/RadianDevCore/tools/gcil/commit/749c62bffce908f6e05159a6b94a8c77248fd169))
- **gitlab-ci:** raise minimal 'gitlabci-local' version to '9.0' ([9861c52](https://gitlab.com/RadianDevCore/tools/gcil/commit/9861c5246f4721ffed9fc23ad4bd6da33de0674c))
- **gitlab-ci:** prepare #262 by using 'pipx' for local installs ([b68cf90](https://gitlab.com/RadianDevCore/tools/gcil/commit/b68cf90d24478bed30c9abf07c2f109db955a015))
- **gitlab-ci:** isolate 'changelog.sh' to '.chglog' folder ([e3a2b5a](https://gitlab.com/RadianDevCore/tools/gcil/commit/e3a2b5a761db2ceba4426fb9e7aa1b2a0065d6ba))
- **gitlab-ci:** deprecate 'py3.11:preview' job ([9416c62](https://gitlab.com/RadianDevCore/tools/gcil/commit/9416c6245fe7dc8dc8c9589b9a556086c87c2f12))


<a name="8.1.0"></a>
## [8.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/8.0.0...8.1.0) (2023-09-17)

### ✨ Features

- implement #266: add support for Python 3.11 ([d56d2dc](https://gitlab.com/RadianDevCore/tools/gcil/commit/d56d2dc6f1e24f90fa42271240b247f69e03f558))

### 🐛 Bug Fixes

- resolve #261: strip 'BOLD' and 'RESET' colors last for boxes ([629c917](https://gitlab.com/RadianDevCore/tools/gcil/commit/629c917595276745e6219748734afd3fa133b703))
- prepare #264: detect empty included files like GitLab ([ab1e3d4](https://gitlab.com/RadianDevCore/tools/gcil/commit/ab1e3d4c7e156fc50c6459d222b71980a059001c))
- resolve #260: implement 'include:' wildcard paths support ([ee7af1a](https://gitlab.com/RadianDevCore/tools/gcil/commit/ee7af1a70595212cfe4b86ecccf5236cebf83391))
- resolve #265: allow execution in PermissionError paths ([e003254](https://gitlab.com/RadianDevCore/tools/gcil/commit/e003254731e9a93c96cce044c9fec9d1dcae5ff8))
- resolve #258: catch 'Engine' PermissionError rare failures ([68694c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/68694c2025d01ae312725e030ca2657baca644a0))
- finish #266: add 'runroot/graphroot' to fix Podman Python 3.11 ([16967bf](https://gitlab.com/RadianDevCore/tools/gcil/commit/16967bf5c4005a26ff37eb64dcab3920e5963fc4))

### 📚 Documentation

- changelog: regenerate release tag changes history ([d2b147d](https://gitlab.com/RadianDevCore/tools/gcil/commit/d2b147dd1ce2c46e6e786edc64f1e85c4790a04e))

### ⚙️ Cleanups

- finish #260: ignore coverage of failure cases in '__merges' ([23e06c4](https://gitlab.com/RadianDevCore/tools/gcil/commit/23e06c47e53e6f3f247de6cf16972312fd6268f7))
- resolve #263: make missing engines hints easier ([a1e077a](https://gitlab.com/RadianDevCore/tools/gcil/commit/a1e077ae98eb035c89414d71e20e0f7b4bc8eb96))
- finish #265: disable coverage of rare fallback cases ([10a9ed6](https://gitlab.com/RadianDevCore/tools/gcil/commit/10a9ed62bba8939508eba574c04694c9f4089bba))


<a name="8.0.0"></a>
## [8.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/7.2.0...8.0.0) (2023-07-26)

### ✨ Features

- implement #257: default to Docker engine even if Podman exists ([c1d05ac](https://gitlab.com/RadianDevCore/tools/gcil/commit/c1d05ac99f795c3f7196235384dcdd17ef0aae70))

### 🐛 Bug Fixes

- resolve #256: merge all dict templates upon includes ([c30e028](https://gitlab.com/RadianDevCore/tools/gcil/commit/c30e0280d5884d4ff216b79c672ef882ade91e19))

### 📚 Documentation

- readme: hide more sections behind an expand section header ([6d5fd10](https://gitlab.com/RadianDevCore/tools/gcil/commit/6d5fd108c3ecf49a8317f2c4bacfdd59b89a98ce))
- changelog: regenerate release tag changes history ([10653e9](https://gitlab.com/RadianDevCore/tools/gcil/commit/10653e99d35f61bac34dccf328877460f3854931))


<a name="7.2.0"></a>
## [7.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/7.1.0...7.2.0) (2023-07-08)

### 🐛 Bug Fixes

- resolve #252: fix support for 'include: /' root relative paths ([264add6](https://gitlab.com/RadianDevCore/tools/gcil/commit/264add656073fff2b03a449362d6d203a08722b4))

### 📚 Documentation

- changelog: regenerate release tag changes history ([588cf87](https://gitlab.com/RadianDevCore/tools/gcil/commit/588cf87ec1d50d99233667eabe48c186df280bc6))

### 🧪 Test

- prepare #252: add 'includes' tests for correct relative paths ([bbe61a3](https://gitlab.com/RadianDevCore/tools/gcil/commit/bbe61a33872bebf07efc8457d9248507b2d6f836))

### ⚙️ Cleanups

- coverage: use '_' for unused in 'DockerEngine' and 'Boxes' ([2324702](https://gitlab.com/RadianDevCore/tools/gcil/commit/2324702d35eca6b9555ab230b44ec68c0b6a6ca8))


<a name="7.1.0"></a>
## [7.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/7.0.1...7.1.0) (2023-07-08)

### 🐛 Bug Fixes

- resolve #251: add support for 'include: List[str]' items ([a9b8537](https://gitlab.com/RadianDevCore/tools/gcil/commit/a9b8537ba433987114d6121f9e3ee05c63c6ea4c))
- prepare #254: allow 'colored' library to be missing or unusable ([21406cf](https://gitlab.com/RadianDevCore/tools/gcil/commit/21406cf3a7ebe9d783a86e6baa524f16df1eafec))
- resolve #254: fix compatibility with Colored 2.x versions ([6dd1791](https://gitlab.com/RadianDevCore/tools/gcil/commit/6dd17914393cfeb3f79ef16bae4f9a4df06c8f50))
- finish #254: simplify 'colored' library usage without wrappers ([71ff5c0](https://gitlab.com/RadianDevCore/tools/gcil/commit/71ff5c0010a95370950e3c353a737a41e40a443d))
- gitlab-ci: avoid relying on CI/CD defined 'DOCKER_HOST' value ([9280ec6](https://gitlab.com/RadianDevCore/tools/gcil/commit/9280ec6dcb6b79ca197e4fe78d555edbf00d2a71))

### 📚 Documentation

- changelog: regenerate release tag changes history ([74db723](https://gitlab.com/RadianDevCore/tools/gcil/commit/74db723a1042b45822e9e6112714bc584913de6e))

### 🧪 Test

- prepare #250: create 'when: manual' only jobs simple tests ([aecba10](https://gitlab.com/RadianDevCore/tools/gcil/commit/aecba109ac03a7ff1ead1955c9438656900f3a03))


<a name="7.0.1"></a>
## [7.0.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/7.0.0...7.0.1) (2023-04-17)

### ✨ Features

- implement #249: support merging '.local: volumes' lists ([5a49f4b](https://gitlab.com/RadianDevCore/tools/gcil/commit/5a49f4bba35c26b8ab1ecfd0b97dec8f4a91ca88))

### 📚 Documentation

- changelog: regenerate release tag changes history ([e4c7b52](https://gitlab.com/RadianDevCore/tools/gcil/commit/e4c7b523e9fae4fae2a10065243091ac156b68ca))

### ⚙️ Cleanups

- gitlab-ci: add 'Install' local job to install built '.whl' ([c10e9e4](https://gitlab.com/RadianDevCore/tools/gcil/commit/c10e9e4ab1244ac5aa212831000f4eba09321c17))
- gitlab-ci: cleanup intermediates and refactor local paths ([133ad42](https://gitlab.com/RadianDevCore/tools/gcil/commit/133ad42adf959d30e71c0813046a3d386edb42b4))
- setup: add 'setup.py' script shebang header ([41012ae](https://gitlab.com/RadianDevCore/tools/gcil/commit/41012ae2fde43c5a1a53861316e71dc8003e4163))
- typings: minor typings fixes and improvements ([2fcb415](https://gitlab.com/RadianDevCore/tools/gcil/commit/2fcb415cd5c7f62607b8f5555028640df5c6f571))


<a name="7.0.0"></a>
## [7.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/6.0.0...7.0.0) (2023-04-08)

### ✨ Features

- finish #239: implement '--no-color' and related settings ([56ec0c0](https://gitlab.com/RadianDevCore/tools/gcil/commit/56ec0c061f74951106c790587a52a905bfd997b3))
- implement #243: allow setting 'no_verbose' for jobs scripts ([e7876ec](https://gitlab.com/RadianDevCore/tools/gcil/commit/e7876ec7e05fe30e1da27b70dd3e2bef0c7534bb))
- implement #244: allow .local: image: entrypoint overrides ([2e4c369](https://gitlab.com/RadianDevCore/tools/gcil/commit/2e4c369735ea3515ccb8cef8ff2847ad56414e42))
- implement #245: add 'CI_LOCAL_USER_HOST_{GID,UID,USERNAME}' ([cd10c43](https://gitlab.com/RadianDevCore/tools/gcil/commit/cd10c4370d17ebf107172bb2c56fd803547a8abb))
- implement #246: support merging '.local' included nodes ([66bb2a6](https://gitlab.com/RadianDevCore/tools/gcil/commit/66bb2a67e969ef335491265c81567cc0c6645cb1))
- prepare #247: recommend installation of version '>=VERSION' ([5d9c445](https://gitlab.com/RadianDevCore/tools/gcil/commit/5d9c445211bc2c64917dc0d022481a819fd172bb))
- implement #247: implement recommended '.local' version ([ddcf5b3](https://gitlab.com/RadianDevCore/tools/gcil/commit/ddcf5b37fd767e80a6dabfcd9dab7c717b16c470))
- implement #248: add support for standard '__version__' ([6504618](https://gitlab.com/RadianDevCore/tools/gcil/commit/65046188ab2a15d71cd58c779e76866b6589290b))

### 🐛 Bug Fixes

- prepare #238: resolve using wrong working directory for nested includes using `include:project` ([ae6802c](https://gitlab.com/RadianDevCore/tools/gcil/commit/ae6802c3965358012816a6fd68c47437fa7ff7a1))
- resolve #239: ensure 'NO_COLOR' also avoids questionary colors ([eee751a](https://gitlab.com/RadianDevCore/tools/gcil/commit/eee751a9f88aff7a563c23bee56152a1d0826753))
- prepare #240: ensure 'prompt-toolkit' is explicitly updated ([59b255b](https://gitlab.com/RadianDevCore/tools/gcil/commit/59b255b9a865c7d2b75e748a9c5e4894586e5f6c))
- implement #241: improve bool settings and unset with 'UNSET' ([50d0327](https://gitlab.com/RadianDevCore/tools/gcil/commit/50d0327c4519dbbfa196ed4e4fa3b91749b06fe5))
- finish #240: depend to 'prompt-toolkit' like 'questionary' ([c72d24a](https://gitlab.com/RadianDevCore/tools/gcil/commit/c72d24a8ba72f370a8da427564697e56f7b63aab))
- prepare #238: ensure merged included data respect its order ([2585f26](https://gitlab.com/RadianDevCore/tools/gcil/commit/2585f26e9d42c44b037b6c6d72d19161bc689c18))
- finish #238: handle nested local directories and add tests ([799c224](https://gitlab.com/RadianDevCore/tools/gcil/commit/799c2249d962c0b58a4b58e6b4f2e3856669ef43))
- resolve #242: make declared local include:project mandatory ([14bef7a](https://gitlab.com/RadianDevCore/tools/gcil/commit/14bef7a3ba6650d26df32ecc93d8ee223b3ff088))

### 📚 Documentation

- finish #240: refactor and document '<4.6.0' update issues ([a0dcc7c](https://gitlab.com/RadianDevCore/tools/gcil/commit/a0dcc7c1450800f54d0ce30d953493359b373f74))
- readme: refactor the '.local' node with proper documentation ([2fdb441](https://gitlab.com/RadianDevCore/tools/gcil/commit/2fdb4412866ec4d173abdab66811a56c7c7e3b34))
- readme: hide less relevant information in expandable details ([a22f8f2](https://gitlab.com/RadianDevCore/tools/gcil/commit/a22f8f2140d60e1fa6b50ba645ad20ddfcdc7e2c))
- changelog: regenerate release tag changes history ([7e43fa4](https://gitlab.com/RadianDevCore/tools/gcil/commit/7e43fa4ce8374227f06968b7315e324522f77805))

### 🧪 Test

- finish #236: fix interactive console tests and simulation ([b355e68](https://gitlab.com/RadianDevCore/tools/gcil/commit/b355e68987da4568b6ae76d1e62b018bf1986942))
- finish #236: workaround Podman leftover scripts for now ([5f7555b](https://gitlab.com/RadianDevCore/tools/gcil/commit/5f7555b8f0367e6779d19216a47b976e9c0ed628))
- coverage: cover untested lines of colors and includes errors ([8dbe2b4](https://gitlab.com/RadianDevCore/tools/gcil/commit/8dbe2b42bee491939f0278891af0d3192a650e22))

### ⚙️ Cleanups

- finish #238: minor codestyle and comments changes ([ecdbe9b](https://gitlab.com/RadianDevCore/tools/gcil/commit/ecdbe9b9a17dbc5f110e3d5c36b535c9c94adac2))
- gitlab-ci: make 'apk' Alpine 'Typing' installation quiet ([1863c52](https://gitlab.com/RadianDevCore/tools/gcil/commit/1863c528692e3eda4634eff20b4ca21e72335186))
- prepare #240: support CLI only usage without 'questionary' ([8eca7f1](https://gitlab.com/RadianDevCore/tools/gcil/commit/8eca7f17c563cfbf3465dd50b37157d9679cf7d4))
- prepare #239: evaluate and prepare colors only upon use ([e170490](https://gitlab.com/RadianDevCore/tools/gcil/commit/e1704905d38992321f1a8c7e4b6309cb0ff31e07))
- gitlab-ci: enable mypy colored outputs for readability ([4185ab3](https://gitlab.com/RadianDevCore/tools/gcil/commit/4185ab3fb62559fad94121cf872a979e4f077433))
- gitlab-ci: ensure jobs run upon 'requirements/*' changes ([2513299](https://gitlab.com/RadianDevCore/tools/gcil/commit/2513299c9dc977646542f7f229aa2570b1153145))
- gitlab-ci: use the self hosted 'alpine/git' container image ([912a46b](https://gitlab.com/RadianDevCore/tools/gcil/commit/912a46b5433d5fe67ba1dd909755ce516223937e))
- finish #238: minor lint codestyle improvement ([957b25c](https://gitlab.com/RadianDevCore/tools/gcil/commit/957b25c8c4b93c1d1baf7239bf41e1a2cdb21b9d))
- coverage: missing modules fallbacks coverage improvements ([237e094](https://gitlab.com/RadianDevCore/tools/gcil/commit/237e094f3d5157a98b25352963b7a11314325ba7))
- package: import 'UpdateChecker' libraries only upon use ([91420dd](https://gitlab.com/RadianDevCore/tools/gcil/commit/91420dd2cf072f29d1855382c0485d33382210d4))
- prepare #247: make the 'Updates.message' API a staticmethod ([a41b165](https://gitlab.com/RadianDevCore/tools/gcil/commit/a41b1651b9d5c61917257d50f2ee455b106a96bd))
- gitlab-ci: enable signoff of changelog commits ([a733e82](https://gitlab.com/RadianDevCore/tools/gcil/commit/a733e82d9564e41419a6554b8b061967a98261c4))


<a name="6.0.0"></a>
## [6.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.5.0...6.0.0) (2023-02-22)

### ✨ Features

- prepare #237: migrate 'CI_LOCAL_NO_GIT_SAFETIES' to settings ([93ce0bd](https://gitlab.com/RadianDevCore/tools/gcil/commit/93ce0bd63f52bc990774f46cb416b205081f7dcc))
- prepare #237: migrate 'CI_LOCAL_NO_SCRIPT_FAIL' to settings ([c3e424b](https://gitlab.com/RadianDevCore/tools/gcil/commit/c3e424b06667aa5e1eba369d6c85ba10ce56fd20))
- implement #237: create '--set GROUP KEY VAL' settings access ([a9fbf53](https://gitlab.com/RadianDevCore/tools/gcil/commit/a9fbf53020bfcc5f214f5e6bb960d94a389f9711))
- prepare #236: add 'Interrupted' mode for jobs interruptions ([af6a74d](https://gitlab.com/RadianDevCore/tools/gcil/commit/af6a74d38ff860f3e7258301cc5460e18ce2e81e))
- implement #236: implement inline shell console with settings ([6336c46](https://gitlab.com/RadianDevCore/tools/gcil/commit/6336c46f8f109900894b52c4a83547a2fe5cc2b7))
- finish #236: add '.local: no_console' configuration support ([c695762](https://gitlab.com/RadianDevCore/tools/gcil/commit/c695762aecdabd1ae492b655cab015ac2b2c5340))

### 📚 Documentation

- changelog: regenerate release tag changes history ([a52fe5f](https://gitlab.com/RadianDevCore/tools/gcil/commit/a52fe5ff0b6648ce43dbb51d01744e9f0578d83f))

### ⚙️ Cleanups

- prepare #237: improve settings getter handlings and syntax ([bc0546c](https://gitlab.com/RadianDevCore/tools/gcil/commit/bc0546cad29237fbdcd8ecba3da50c92130ef0e5))
- finish #236: improve result text issue raised by SonarQube ([35a10cb](https://gitlab.com/RadianDevCore/tools/gcil/commit/35a10cb875dec2765ad019dd2ebb63a0bbc37aae))


<a name="5.5.0"></a>
## [5.5.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.4.1...5.5.0) (2023-02-16)

### ✨ Features

- implement #235: pass commands with '-C' over 'script:' ([19fa178](https://gitlab.com/RadianDevCore/tools/gcil/commit/19fa1785c333370cb2b129961201dfaa4d4c5dbd))

### 📚 Documentation

- changelog: regenerate release tag changes history ([3b426bc](https://gitlab.com/RadianDevCore/tools/gcil/commit/3b426bc8587dea63985d69ef88ef51e5b91718ac))

### ⚙️ Cleanups

- vscode: configure default formatters for YAML and Markdown ([7885601](https://gitlab.com/RadianDevCore/tools/gcil/commit/78856015dc6e3c30002e8d5246ba2e4c4889e958))
- pylint: resolve 'superfluous-parens' new warnings ([6c07d3e](https://gitlab.com/RadianDevCore/tools/gcil/commit/6c07d3ea79306732d050926f7e516c7d18740b17))


<a name="5.4.1"></a>
## [5.4.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.4.0...5.4.1) (2023-01-22)

### 🐛 Bug Fixes

- finish #234: respect global 'image' before defaulting to ruby ([1dce511](https://gitlab.com/RadianDevCore/tools/gcil/commit/1dce511d408d543ab9b53795b3a0c69825d32040))

### 📚 Documentation

- changelog: regenerate release tag changes history ([9391abb](https://gitlab.com/RadianDevCore/tools/gcil/commit/9391abb03438d341b46303578b4c26289f942dbe))


<a name="5.4.0"></a>
## [5.4.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.3.0...5.4.0) (2023-01-15)

### ✨ Features

- implement #234: add support for default ruby:3.1 image ([4a0e44c](https://gitlab.com/RadianDevCore/tools/gcil/commit/4a0e44cba6641ab626a8c161a8b385f3209f45ca))
- prepare #233: refactor and migrate from 'oyaml' to 'PyYAML' ([c7f851b](https://gitlab.com/RadianDevCore/tools/gcil/commit/c7f851bc2be6a5c362f3b86b5b0872b3418f0346))
- implement #233: add support for '!reference' YAML resolving ([a955b28](https://gitlab.com/RadianDevCore/tools/gcil/commit/a955b28a59c2a36becdbb83d96984dd842200dbd))

### 🐛 Bug Fixes

- continue #170: resolve 'Dicts.find' coverage mismatch issue ([031a6ff](https://gitlab.com/RadianDevCore/tools/gcil/commit/031a6ffd5361939dc7375349ef6de734759cc36c))

### 📚 Documentation

- finish #233: add '!reference' examples in supported features ([7ccccbb](https://gitlab.com/RadianDevCore/tools/gcil/commit/7ccccbb992b314c446fe212b25e593cd539f81cc))
- changelog: regenerate release tag changes history ([29a8799](https://gitlab.com/RadianDevCore/tools/gcil/commit/29a8799196c8061e238568f0d2cc966b58591a53))

### 🎨 Styling

- continue #170: minor typings improvements in 'gitlab.py' ([b88c31a](https://gitlab.com/RadianDevCore/tools/gcil/commit/b88c31aed8133b83e7f418594de511d0e7e003b0))

### 🧪 Test

- finish #232: coverage of double 'include: project:' nodes ([b81af59](https://gitlab.com/RadianDevCore/tools/gcil/commit/b81af59d4a7a4ece7813c0bd59c04faf778b09de))
- finish #234: fix 'CI_LOCAL_IMAGE_DEFAULT' vars for coverage ([7e4833c](https://gitlab.com/RadianDevCore/tools/gcil/commit/7e4833cf03ffc5f97343c913688190f4095c5390))

### ⚙️ Cleanups

- gitlab-ci: run mypy Typings on modified files first ([58d7d48](https://gitlab.com/RadianDevCore/tools/gcil/commit/58d7d489f79ec839c4bd9e789e44e5ec92963d77))
- gitlab-ci: raise unit tests timeout to 20 minutes ([8e9af83](https://gitlab.com/RadianDevCore/tools/gcil/commit/8e9af8334bc4047e44c095f185047bf8654a883c))
- finish #233: add coverage filters of fallback conditions ([cc908d3](https://gitlab.com/RadianDevCore/tools/gcil/commit/cc908d3d44a658b35ddef6d6d180b5ea5ecb92f5))


<a name="5.3.0"></a>
## [5.3.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.2.0...5.3.0) (2023-01-10)

### ✨ Features

- implement #229: add 'CI_LOCAL_HOST' for host runner env ([af5362a](https://gitlab.com/RadianDevCore/tools/gcil/commit/af5362a0fb459392a7862b391166e1d59696d4b5))
- implement #230: allow filtering for jobs or stages names ([a313f53](https://gitlab.com/RadianDevCore/tools/gcil/commit/a313f53aec635736d0e35831e2f3c4d163aa1bb7))
- resolve #231: avoid notify events with bash / debug / CTRL+C ([6ec88a7](https://gitlab.com/RadianDevCore/tools/gcil/commit/6ec88a74db6948a7ac1c990cfeb1314ca5f4c15c))
- implement #232: support 'include: project:' local clones ([06dda84](https://gitlab.com/RadianDevCore/tools/gcil/commit/06dda84cf8fbaf86d1cae94c5df1c42f30c699c2))

### 📚 Documentation

- changelog: regenerate release tag changes history ([6302910](https://gitlab.com/RadianDevCore/tools/gcil/commit/6302910e8eca2557b1000a745565d2c912890898))

### ⚙️ Cleanups

- gitlab-ci: add tests successful output and sudo preparation ([5ceccfe](https://gitlab.com/RadianDevCore/tools/gcil/commit/5ceccfecc9714dffbf4c6a3921998a33fbb35769))
- continue #170: implement 'NamedTuple' typed classes ([8ebf17f](https://gitlab.com/RadianDevCore/tools/gcil/commit/8ebf17f949f7e6e06b8b937e26540eeb668b3fcf))
- continue #170: refactor engines with typing codestyle ([ce49642](https://gitlab.com/RadianDevCore/tools/gcil/commit/ce4964200da20d14b5a64bc79886e75b0db41349))
- continue #170: minor simple typing codestyle improvements ([a190f77](https://gitlab.com/RadianDevCore/tools/gcil/commit/a190f77ce0c0bd9ab2cf239f32a1cd78f62ef070))


<a name="5.2.0"></a>
## [5.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.1.0...5.2.0) (2022-12-03)

### ✨ Features

- implement #227: allow mounting SSH keys as a specific user ([5d2b716](https://gitlab.com/RadianDevCore/tools/gcil/commit/5d2b716d752576daeb624870b101bd0d3734fe4a))

### 🐛 Bug Fixes

- resolve #228: fix SSH keys mounting path and support ([e7c350a](https://gitlab.com/RadianDevCore/tools/gcil/commit/e7c350a926449e5f9671aa04b2fbfb71a9a841e7))

### 📚 Documentation

- changelog: regenerate release tag changes history ([3c0b53c](https://gitlab.com/RadianDevCore/tools/gcil/commit/3c0b53cab78cf924bff5afe532aedc510020bee2))

### ⚙️ Cleanups

- prepare #227: isolate arguments default values in Bundle ([92d2ede](https://gitlab.com/RadianDevCore/tools/gcil/commit/92d2ede32186f9ef57aec8ae5e42a8ff755a99d1))
- prepare #227: always set arguments explicit 'store' actions ([9c2e5f4](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c2e5f4b96c0f6ec90723808f3a7e265134d05bf))
- finish #225: resolve 'Platform.display()' return typing ([a63f3bd](https://gitlab.com/RadianDevCore/tools/gcil/commit/a63f3bdd9450af56297ec6b1c8a93a32ffe36400))


<a name="5.1.0"></a>
## [5.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/5.0.0...5.1.0) (2022-11-30)

### ✨ Features

- implement #223: add support for '.local: variables:' node ([55167d3](https://gitlab.com/RadianDevCore/tools/gcil/commit/55167d3b077c547b5fc2c8e3d7291903cc914f4b))
- implement #224: add ".local: shell:" for bash/debug ([bd7dd90](https://gitlab.com/RadianDevCore/tools/gcil/commit/bd7dd90aa5429fb68bc42b7b7b54597283e7b987))
- implement #225: add ".local: display:" DISPLAY binding ([d09a27a](https://gitlab.com/RadianDevCore/tools/gcil/commit/d09a27a097ae96111f045942fbf1f9b2b775fb5d))
- implement #226: add ".local: notify:" notifications support ([ba05b8b](https://gitlab.com/RadianDevCore/tools/gcil/commit/ba05b8b7dd5768eab36082acf282fe6c78a4f71f))

### 🐛 Bug Fixes

- resolve #223: refactor and resolve environment vars priority ([73745ba](https://gitlab.com/RadianDevCore/tools/gcil/commit/73745ba0541ee645105cdccdaa412b4c20715184))
- finish #223: remove unused globals setter ([a680b0f](https://gitlab.com/RadianDevCore/tools/gcil/commit/a680b0f9e673ff5621cc5b5012c1f583ccc9354d))

### 📚 Documentation

- changelog: regenerate release tag changes history ([3a5986e](https://gitlab.com/RadianDevCore/tools/gcil/commit/3a5986e781c61ff22fe8c3c574da6b6b9599b717))

### ⚙️ Cleanups

- coverage: minor sources coverage improvements ([a88c5ca](https://gitlab.com/RadianDevCore/tools/gcil/commit/a88c5ca1b2832895477e31c46e28e681b601119c))
- finish #170: resolve 'PermissionError' failure raising ([791b3e2](https://gitlab.com/RadianDevCore/tools/gcil/commit/791b3e28b89ceb1ca2a75a2670916aafa26ebeae))
- typings: minor sources typings improvements ([ecbfaf1](https://gitlab.com/RadianDevCore/tools/gcil/commit/ecbfaf1519f430fb81d91f8159a50e9471c0738e))
- prepare #223: implement GitLab job 'Variant' type wrapper ([1da0c50](https://gitlab.com/RadianDevCore/tools/gcil/commit/1da0c50ea09ee9e825c645f1f2e2a95e8c6d9319))
- typings: more minor sources typings improvements ([178ded4](https://gitlab.com/RadianDevCore/tools/gcil/commit/178ded4baceda6cd47143adc78103b0af118c9f5))


<a name="5.0.0"></a>
## [5.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.8.1...5.0.0) (2022-11-16)

### ✨ Features

- implement #221: add '.local: no_regex' configuration support ([2441b41](https://gitlab.com/RadianDevCore/tools/gcil/commit/2441b41330b385b77ccaab8da7aa5318e433c409))
- implement #219: implement support for nested includes ([1075259](https://gitlab.com/RadianDevCore/tools/gcil/commit/1075259730c1861ca3f52a81a2ca93e096487bbd))

### 🐛 Bug Fixes

- resolve #220: avoid "VAR=$VAR_NAME" expand failures ([437fa9c](https://gitlab.com/RadianDevCore/tools/gcil/commit/437fa9c12ffa5070077e28596d523e2da52e15ca))
- resolve #222: preserve stage in multiple 'extends:' array ([8846a01](https://gitlab.com/RadianDevCore/tools/gcil/commit/8846a01deded71ff44747eb29c4df8f4f9cc6872))

### 📚 Documentation

- changelog: regenerate release tag changes history ([78e7516](https://gitlab.com/RadianDevCore/tools/gcil/commit/78e7516b611d1f88495ad824b519052b0dbd967d))

### 🎨 Styling

- prepare #170: implement mypy Python linting features job ([bac4ad9](https://gitlab.com/RadianDevCore/tools/gcil/commit/bac4ad91c45f0cd59ca2177705fa30fcf8da4ba2))
- prepare #170: sort 'menus.py' and 'gitlab.py' methods ([65683a5](https://gitlab.com/RadianDevCore/tools/gcil/commit/65683a5cfb1ecf64f946850e7031fc2c4d0fc711))
- resolve #170: implement simple standard Python typings ([fb7c23c](https://gitlab.com/RadianDevCore/tools/gcil/commit/fb7c23cbd2060b2b3495f7ea623d582addb68ab8))


<a name="4.8.1"></a>
## [4.8.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.8.0...4.8.1) (2022-10-19)

### 🐛 Bug Fixes

- resolve #218: config runner jobs' variables before expansions ([abb3b43](https://gitlab.com/RadianDevCore/tools/gcil/commit/abb3b439601b940ad3bfe6b43514049b677cc598))

### 📚 Documentation

- changelog: regenerate release tag changes history ([8efb5ae](https://gitlab.com/RadianDevCore/tools/gcil/commit/8efb5ae8dc6351bbebed6c3540f30f6f7a372cb8))

### 🧪 Test

- prepare #218: use 'CI_COMMIT_*' inside job variables ([7a6fb3f](https://gitlab.com/RadianDevCore/tools/gcil/commit/7a6fb3f9369a36b748f84472e80b3e4d53b057b2))

### ⚙️ Cleanups

- gitlab-ci: make 'apk add' Alpine installations quiet ([20ceb75](https://gitlab.com/RadianDevCore/tools/gcil/commit/20ceb75b547e8893f70c765c72dcba8c40b548e6))


<a name="4.8.0"></a>
## [4.8.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.7.3...4.8.0) (2022-09-19)

### ✨ Features

- implement #215: add support for GIT_CLONE_PATH workdirs ([3e8747e](https://gitlab.com/RadianDevCore/tools/gcil/commit/3e8747e2bf17611e4bb91d21088cca11a99a64de))
- implement #216: implement SSH and SSH agent binds ([95e78fd](https://gitlab.com/RadianDevCore/tools/gcil/commit/95e78fd06c2036e8629719daaea3798ffae601cc))

### 📚 Documentation

- changelog: regenerate release tag changes history ([a767aef](https://gitlab.com/RadianDevCore/tools/gcil/commit/a767aefd1750c1bfd3ecd0987cda96cc2ca1a158))

### 🧪 Test

- finish #216: resolve ~/.ssh existence for Podman jobs ([89d8bba](https://gitlab.com/RadianDevCore/tools/gcil/commit/89d8bba3aa808b8473ab93eb852588287d0d31ea))

### ⚙️ Cleanups

- finish #216: refactor job options into a properties class ([526fb2c](https://gitlab.com/RadianDevCore/tools/gcil/commit/526fb2c804954b397daf35ecb9676fbaceb2e389))
- finish #216: resolve 'SSH_AUTH_SOCK' code coverage ([209c9d9](https://gitlab.com/RadianDevCore/tools/gcil/commit/209c9d9b01a1703b3a821a44802fd6c7c96e4598))


<a name="4.7.3"></a>
## [4.7.3](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.7.2...4.7.3) (2022-09-06)

### 🐛 Bug Fixes

- resolve #214: fix stage issues when using unknown templates ([f754a8e](https://gitlab.com/RadianDevCore/tools/gcil/commit/f754a8eae137bef45c18806fa26054326000fb80))

### 📚 Documentation

- changelog: regenerate release tag changes history ([5238362](https://gitlab.com/RadianDevCore/tools/gcil/commit/523836259db17aa85fa48d3b4ddd96a9350f1cce))


<a name="4.7.2"></a>
## [4.7.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.7.1...4.7.2) (2022-09-06)

### 📚 Documentation

- resolve #213: fix the GitLab owner path URLs for PyPI ([49f3179](https://gitlab.com/RadianDevCore/tools/gcil/commit/49f3179a163597f675726bc848ded3e79cfe6e93))
- changelog: regenerate release tag changes history ([faaae16](https://gitlab.com/RadianDevCore/tools/gcil/commit/faaae1625d08f26b51ca70d6f32f8f15adbd7b0a))


<a name="4.7.1"></a>
## [4.7.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.7.0...4.7.1) (2022-09-05)

### ✨ Features

- resolve #212: allow incomplete 'script' templates by default ([23a65e2](https://gitlab.com/RadianDevCore/tools/gcil/commit/23a65e247dc74a31805cd6fc02b2f9e688992379))

### 🐛 Bug Fixes

- resolve #211: resolve unknown self-nested variables loops ([d803be9](https://gitlab.com/RadianDevCore/tools/gcil/commit/d803be9bfa65d58320c347920780ff105c7c5bea))

### 📚 Documentation

- changelog: regenerate release tag changes history ([ffcfe25](https://gitlab.com/RadianDevCore/tools/gcil/commit/ffcfe25362e73bc6e579fe0528568cc936374011))


<a name="4.7.0"></a>
## [4.7.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.6.2...4.7.0) (2022-09-02)

### 🐛 Bug Fixes

- resolve #210: resolve self-nested variables loops ([cf4cc37](https://gitlab.com/RadianDevCore/tools/gcil/commit/cf4cc37713104d4b1c43b6a085cbb688e6c9c610))

### 📚 Documentation

- changelog: regenerate release tag changes history ([39ed5f5](https://gitlab.com/RadianDevCore/tools/gcil/commit/39ed5f5d6693a05b5d267b056a9dc3000b056d9f))

### ⚙️ Cleanups

- tests: resolve 'colored' forced colors in CI tests ([e6c0520](https://gitlab.com/RadianDevCore/tools/gcil/commit/e6c052011aab0cffa860b5d41a1fab512167a26d))
- vscode: minor old .gitignore leftover cleanup ([19bcd92](https://gitlab.com/RadianDevCore/tools/gcil/commit/19bcd9235b2aad1271ae31069e4db82fdc68c0c9))
- setup: refactor and unify projet build with constants ([35d2eff](https://gitlab.com/RadianDevCore/tools/gcil/commit/35d2effc3d9c90f318d1b705e4482078229e42f7))

### Parsers

- implement !5: add support for prefilled variables ([67763e4](https://gitlab.com/RadianDevCore/tools/gcil/commit/67763e412a90b5b7baaa1a4897799e9d699f107e))


<a name="4.6.2"></a>
## [4.6.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.6.1...4.6.2) (2022-08-09)

### ✨ Features

- implement #209: add 'CI_PROJECT_NAME' env variable ([bed4906](https://gitlab.com/RadianDevCore/tools/gcil/commit/bed490675b8ec6d92ed0a6dec55a94fecbbd2232))
- implement #209: add 'CI_COMMIT_REF_{NAME,SLUG}' env variable ([cb7f58a](https://gitlab.com/RadianDevCore/tools/gcil/commit/cb7f58a2572fcb9fceb0ba8509d0f809bd1f25fb))
- implement #209: add 'CI_PROJECT_NAMESPACE' env variable ([7b4a105](https://gitlab.com/RadianDevCore/tools/gcil/commit/7b4a1056ee158e5d9438f9801f80fa4bb949f9e7))

### 📚 Documentation

- document #209: add references for the new 'CI_*' variables ([b6cd0a6](https://gitlab.com/RadianDevCore/tools/gcil/commit/b6cd0a67fb8c113be95d419a398b21a7396b95ce))
- changelog: regenerate release tag changes history ([18d5909](https://gitlab.com/RadianDevCore/tools/gcil/commit/18d59093d37dcfda0a44c491b10c45eb33209499))

### ⚙️ Cleanups

- finish #208: minor SonarCloud codestyle improvement ([e2de2d8](https://gitlab.com/RadianDevCore/tools/gcil/commit/e2de2d8c207ac955e3e4c2c0a75c2b38bf594805))
- finish #209: resolve CI Git variables SonarCloud coverage ([82b15c0](https://gitlab.com/RadianDevCore/tools/gcil/commit/82b15c0a8a9db073786f92597cdae7cfaea948b7))
- finish #207: fix silent 'after_script' SonarCloud coverage ([15bc1a7](https://gitlab.com/RadianDevCore/tools/gcil/commit/15bc1a7783ab599ce3f1db6a878bd825247a8fbd))


<a name="4.6.1"></a>
## [4.6.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.6.0...4.6.1) (2022-08-09)

### 🐛 Bug Fixes

- resolve #207: resolve 'local' handling as being silent ([b58c37e](https://gitlab.com/RadianDevCore/tools/gcil/commit/b58c37e800e2c130389e39ab4c4fbc15a71f4f37))
- resolve #206: handle images nested environment variables ([c1c7bf3](https://gitlab.com/RadianDevCore/tools/gcil/commit/c1c7bf3a577d7192d291045703a1a562895ac09d))
- resolve #208: handle unknown variables in Environment.expand ([74f33c7](https://gitlab.com/RadianDevCore/tools/gcil/commit/74f33c7f5e14f6b93392f8f11dee4b13b967814a))

### 📚 Documentation

- changelog: regenerate release tag changes history ([4920980](https://gitlab.com/RadianDevCore/tools/gcil/commit/492098083af51589f5f3c17fe70732c58d6542fb))

### 🧪 Test

- finish #208: fix 'project' expecting broken nested variables ([9c40904](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c409048ce9cfbed211b326ce02d3a513218a28c))

### ⚙️ Cleanups

- finish #75: resolve coverage of unknown configuration types ([3f9747f](https://gitlab.com/RadianDevCore/tools/gcil/commit/3f9747f491d2a06ebd41d948def8a5d144a18ecf))
- gitlab-ci: enforce unknown 'SUITE' filtering unknown suites ([1bdbf70](https://gitlab.com/RadianDevCore/tools/gcil/commit/1bdbf70b0e7f3536d1bd03851977ef7e95ccc0f4))


<a name="4.6.0"></a>
## [4.6.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.5.2...4.6.0) (2022-08-01)

### ✨ Features

- prepare #75: migrate from 'PyInquirer' to 'questionary' ([6555a03](https://gitlab.com/RadianDevCore/tools/gcil/commit/6555a030c238677e5152adf1cb8eb0d5148893ea))
- resolve #205: migrate to Python 3.10 version and images ([8987db7](https://gitlab.com/RadianDevCore/tools/gcil/commit/8987db700ced29fb7b4be90444b8c4b9f14fea11))

### 📚 Documentation

- preview: refresh the SVG for the latest 4.6.0 release ([bbc3e91](https://gitlab.com/RadianDevCore/tools/gcil/commit/bbc3e9109fa75c501aaab50893c86d65803458fe))
- changelog: regenerate release tag changes history ([6d5b483](https://gitlab.com/RadianDevCore/tools/gcil/commit/6d5b483ee35068d8660790cad5445239888f17ab))

### ⚙️ Cleanups

- gitlab-ci: minor 'pip3' syntax improvement ([e6fdcd0](https://gitlab.com/RadianDevCore/tools/gcil/commit/e6fdcd02003b37d50856fae5659c61a70a457158))
- package: minor Python codestyle improvement on str.split() ([63d3373](https://gitlab.com/RadianDevCore/tools/gcil/commit/63d3373161c39213b49f3a04cc2c9499222fe82f))
- requirements: enforce version 5.6 of 'gitlab-release' ([0022529](https://gitlab.com/RadianDevCore/tools/gcil/commit/00225293531a4f255dd28b1f76661faf6c31c936))
- requirements: upgrade to 'pexpect-executor' version 2.1.0 ([3a6d62f](https://gitlab.com/RadianDevCore/tools/gcil/commit/3a6d62f7e23fe88dd4102ffae6ae156515cb5387))


<a name="4.5.2"></a>
## [4.5.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.5.1...4.5.2) (2022-07-30)

### ✨ Features

- prepare #203: add section comments to the entrypoint script ([22a4ee9](https://gitlab.com/RadianDevCore/tools/gcil/commit/22a4ee92e8aabf13bc19a17bde290188038cbc01))
- prepare #203: implement entrypoint printer with '--scripts' ([645d968](https://gitlab.com/RadianDevCore/tools/gcil/commit/645d9683ff2976e275cb5ced534fbea6d725912a))
- implement #203: add support for new Git safeties safeguards ([34df7c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/34df7c28b62200ef4d20c77eff4a26dc534f0bc9))

### 🐛 Bug Fixes

- prepare #203: ensure flushed script file is actually open ([4efb31c](https://gitlab.com/RadianDevCore/tools/gcil/commit/4efb31c16fbe656134bad6fd0451d25c92ab81df))

### 📚 Documentation

- changelog: regenerate release tag changes history ([92f9f2a](https://gitlab.com/RadianDevCore/tools/gcil/commit/92f9f2a5d9b105725743bb5e85a7f216bad0e809))

### 🧪 Test

- validate #203: add tests for Git safeties implementation ([a962848](https://gitlab.com/RadianDevCore/tools/gcil/commit/a96284832c85a48c15b8bf5ee64c84f4d6559143))


<a name="4.5.1"></a>
## [4.5.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.5.0...4.5.1) (2022-07-30)

### ✨ Features

- finish #202: implement jobs list if PyInquirer is missing ([30f4e6c](https://gitlab.com/RadianDevCore/tools/gcil/commit/30f4e6c22f95436c65d5376fa18cd300e45c47e2))

### 📚 Documentation

- changelog: regenerate release tag changes history ([81ac5a8](https://gitlab.com/RadianDevCore/tools/gcil/commit/81ac5a8be7b19a826f2696471e245f6da2b7ec7c))

### 🧪 Test

- registry: migrate from DockerHub to GitLab project images ([99f9abf](https://gitlab.com/RadianDevCore/tools/gcil/commit/99f9abf5265c0ee746418eb3ba5a326a40edf739))

### ⚙️ Cleanups

- cleanup #202: minor codestyle improvements from SonarCloud ([4372765](https://gitlab.com/RadianDevCore/tools/gcil/commit/43727655b8c3a17eb1f85a46abd76314a440d378))
- parsers: minor codestyle improvements from SonarCloud ([b84e805](https://gitlab.com/RadianDevCore/tools/gcil/commit/b84e805266f4f94cd23f5c136bd5312fb4460f06))
- cli, package: minor codestyle improvements from SonarCloud ([be30d24](https://gitlab.com/RadianDevCore/tools/gcil/commit/be30d240c8b4c05317387b48699d27c2f333fafd))
- sonar: declare Python versions for SonarCloud settings ([e19e15d](https://gitlab.com/RadianDevCore/tools/gcil/commit/e19e15da6384ec9b8d22b36b39916df1b9c04f37))
- coverage: disable coverage of missing PyInquirer imports ([48e333b](https://gitlab.com/RadianDevCore/tools/gcil/commit/48e333b2a3b3c665d87f2fd86b07c06b3a9d1d1d))
- engines: resolve SonarCloud warnings with a base interface ([c11be43](https://gitlab.com/RadianDevCore/tools/gcil/commit/c11be4353c460659f17769b6af6dc2180777188e))
- coverage: resolve coverage issues for SonarCloud analysis ([d6dc023](https://gitlab.com/RadianDevCore/tools/gcil/commit/d6dc0238d7665e243b59c6bdedc05c5cf768fef5))


<a name="4.5.0"></a>
## [4.5.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.4.0...4.5.0) (2022-07-29)

### 🐛 Bug Fixes

- resolve #202: make PyInquirer optional for Python 3.10 use ([60ca8a9](https://gitlab.com/RadianDevCore/tools/gcil/commit/60ca8a944f4186601b552a17c80426d1902961c1))

### 📚 Documentation

- changelog: regenerate release tag changes history ([9489525](https://gitlab.com/RadianDevCore/tools/gcil/commit/94895250377336534899a3b0cf64f5cedc91d39d))

### 🧪 Test

- prepare #202: add Python 3.10 Docker job test ([ed5a0a9](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed5a0a94f2d56df7a061171b03483293f1fdbf05))

### ⚙️ Cleanups

- gitlab-release: migrate back to upstream gitlab-release 5.6 ([8d4b054](https://gitlab.com/RadianDevCore/tools/gcil/commit/8d4b054f50f59e4f50cb35c8e77cfc71ceca0df3))
- vscode: cleanup deprecated Visual Studio Code extensions ([b5812db](https://gitlab.com/RadianDevCore/tools/gcil/commit/b5812db1f8af2cdc35b3dbec0ac66826620c50bc))
- lint: resolve PyLint warnings and codestyle improvements ([20c1f42](https://gitlab.com/RadianDevCore/tools/gcil/commit/20c1f42949cfcaaf8010f663de0d8f7891b40310))


<a name="4.4.0"></a>
## [4.4.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.3.0...4.4.0) (2022-04-09)

### ✨ Features

- implement #200: add support for '.pre' and '.post' stages ([54ffc26](https://gitlab.com/RadianDevCore/tools/gcil/commit/54ffc2689d6e57196788e2d9bd65e34528173b1a))

### 🐛 Bug Fixes

- resolve #201: handled nested 'extends' incomplete jobs ([b1cfdd1](https://gitlab.com/RadianDevCore/tools/gcil/commit/b1cfdd1c8e809b13503966074ed1b251eec89484))

### 📚 Documentation

- changelog: regenerate release tag changes history ([545070e](https://gitlab.com/RadianDevCore/tools/gcil/commit/545070ef66fa697c2d8cd2e5fb1b041204e56f99))


<a name="4.3.0"></a>
## [4.3.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.2.0...4.3.0) (2022-03-22)

### ✨ Features

- implement #194: handle 'matrix' nodes as job nodes variants ([853ea69](https://gitlab.com/RadianDevCore/tools/gcil/commit/853ea696f64ff65039b33e2480161620d5398cce))

### 🐛 Bug Fixes

- implement #199: handle 'bash' entrypoints if available ([b3406d8](https://gitlab.com/RadianDevCore/tools/gcil/commit/b3406d8fd00f5db034958c74ff7baf192d63cc16))
- gitlab-release: import from Git commit 0aeba58a for tests ([025b9b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/025b9b0ca0952d9df1dac6a2076b7a188935e567))

### 📚 Documentation

- document #194: add 'parallel: matrix:' references in README ([e40e1f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/e40e1f01272b49c835ffdd87e98a61f1577df2da))
- changelog: regenerate release tag changes history ([1ae392e](https://gitlab.com/RadianDevCore/tools/gcil/commit/1ae392e7c430dcd7cddd9be6a485a85a55cad9c8))

### 🧪 Test

- finish #194: ensure explicit job matrix names can be called ([0b2976d](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b2976d2383a69e53f2757d8f8e2b79da10fa38c))
- finish #194: drop 'PYTHON_VERSION' from CI jobs before tests ([59bbfbf](https://gitlab.com/RadianDevCore/tools/gcil/commit/59bbfbf398bc998df5e89d7afe608e62ef5e23a8))

### ⚙️ Cleanups

- finish #194: minor codestyle and lint cleanups ([ed93056](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed93056e41e5ab93ebbabc7973de9f288cf560ae))
- gitlab-ci: adapt 'prepare' and 'build' jobs to '3.9-alpine' ([3249867](https://gitlab.com/RadianDevCore/tools/gcil/commit/3249867fc58021eeb7225fece43fcf4fbec0eaef))
- tests: migrate 'parallel' jobs to 'python:*-alpine' images ([7e4b318](https://gitlab.com/RadianDevCore/tools/gcil/commit/7e4b318ca2f79b5eb0999fef8f246596fdc2f4dd))
- gitlab-ci: use 'tobix/pywine:3.7' for 'Coverage Windows' ([6aeb02a](https://gitlab.com/RadianDevCore/tools/gcil/commit/6aeb02a97626d60840e5e347f24eb89ae298238f))
- gitlab-ci: resolve 'Deploy Release' Alpine missing packages ([76d52ae](https://gitlab.com/RadianDevCore/tools/gcil/commit/76d52ae9da8f88be69c114c4fd77e299bce33a26))


<a name="4.2.0"></a>
## [4.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.1.3...4.2.0) (2022-03-09)

### ✨ Features

- implement #198: add support for 'CI_LOCAL_NETWORK' env var ([c30853c](https://gitlab.com/RadianDevCore/tools/gcil/commit/c30853c4f704ae366593020e8469bf4c9e675891))

### 🐛 Bug Fixes

- resolve #193: link against 'Releases' instead of 'Tags' ([2b23222](https://gitlab.com/RadianDevCore/tools/gcil/commit/2b23222fb20e4b044a4d82448b1d82537b5d3ad1))
- resolve #195: expand environment vars in 'services:' nodes ([c52d850](https://gitlab.com/RadianDevCore/tools/gcil/commit/c52d850f6f7e7fb900b4259471ac3d06a28012a0))
- resolve #196: resolve infinite colors loops in 'Strings.wrap' ([41952f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/41952f02375cf95257e12871c8714cb40b593e89))
- resolve #197: detect Podman containers 'start' failures ([d961e39](https://gitlab.com/RadianDevCore/tools/gcil/commit/d961e395997cdfeebca53a8d5a65794be1b48b4b))
- gitlab-release: fix release creation with gitlab-release 5.2 ([b4f6338](https://gitlab.com/RadianDevCore/tools/gcil/commit/b4f63380fe3be1364549db2e2b4432012cfd779d))

### 📚 Documentation

- changelog: regenerate release tag changes history ([d80eebb](https://gitlab.com/RadianDevCore/tools/gcil/commit/d80eebb787f2f33cfba939ac737e793817d7cea5))

### 🧪 Test

- prepare #197: accept missing workdir folder fails on Podman ([2e0d1ef](https://gitlab.com/RadianDevCore/tools/gcil/commit/2e0d1ef8ba26fb38dd7dd38f1d1f1334ccca21e4))
- coverage: ensure 'colored' wraps are tested in 'Boxes.print' ([15f4ada](https://gitlab.com/RadianDevCore/tools/gcil/commit/15f4adaff1221c61d227b412fe30d21f2bb6e1b9))
- prepare #197: accept the 'bridge' network fails with Podman ([03a7e85](https://gitlab.com/RadianDevCore/tools/gcil/commit/03a7e852c67db2fc055d768173d9409880079632))
- prepare #197: accept unknown workdir folder fails on Podman ([f7d3950](https://gitlab.com/RadianDevCore/tools/gcil/commit/f7d3950391ed327bd3bfbab01698fa8ce5e8a21b))
- finish #198: extend coverage for 'CI_LOCAL_NETWORK' env var ([b0fb19c](https://gitlab.com/RadianDevCore/tools/gcil/commit/b0fb19ce466e41c83139d0c9d3371dd013f756cf))
- prepare #197: accept faulty workdir folder fails on Podman ([7a1725a](https://gitlab.com/RadianDevCore/tools/gcil/commit/7a1725a056b88629f8b42c5f515d2525df840433))
- finish #196: ensure all colored outputs pass the coverage CI ([726fa0f](https://gitlab.com/RadianDevCore/tools/gcil/commit/726fa0f242087cf37f012a4148fafe1ae5ac3047))

### ⚙️ Cleanups

- requirements: migrate back to gitlab-release 5.2 and higher ([eaae566](https://gitlab.com/RadianDevCore/tools/gcil/commit/eaae5662e6a5098162d1eb95beaa190336466af3))
- gitlabci-local: lint warnings and Python 3.6 f-strings ([a53c5d3](https://gitlab.com/RadianDevCore/tools/gcil/commit/a53c5d3ddb6a47a47e3b7ef497cead6bcde95dbc))
- requirements: upgrade to Docker 5.0.3 and enforce requests ([f52800b](https://gitlab.com/RadianDevCore/tools/gcil/commit/f52800b2dfc12ce606f6d4fbbdbe085355d20fe2))
- gitlab-ci: resolve Podman tests due to libseccomp2 version ([6e14d4d](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e14d4d00b772853c41328e1a094596ead5bfbd7))
- gitlab-ci: resolve Podman unqualified docker.io images pull ([095b30b](https://gitlab.com/RadianDevCore/tools/gcil/commit/095b30b864f017e51aa60b9aef73bc1e847f6024))
- gitlab-ci: use 'log_driver = "k8s-file"' and 'storage.conf' ([0b63896](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b638968c15ae54622e37bd67b9e1c3d373ebb6a))
- gitlab-ci: use 'host' network mode for all Podman tests ([8209f24](https://gitlab.com/RadianDevCore/tools/gcil/commit/8209f24cd9223cf2b292b54a245d205698125299))
- coverage: ignore the unused 'Strings.random' method ([6e83d8a](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e83d8ac75d0e5700fad3412671dc8e6b7212f78))


<a name="4.1.3"></a>
## [4.1.3](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.1.2...4.1.3) (2021-07-12)

### 🐛 Bug Fixes

- finish #187: properly detect the UTF-8 stdout encoding ([29723c3](https://gitlab.com/RadianDevCore/tools/gcil/commit/29723c314113d223e7071ac4ae3ac35c3f531470))

### 📚 Documentation

- resolve #189: explicit support for Git Bash / CMD on Windows ([3e75cb2](https://gitlab.com/RadianDevCore/tools/gcil/commit/3e75cb233087cb9301d04a159f9bb976e4dde72c))
- changelog: regenerate release tag changes history ([6827fb1](https://gitlab.com/RadianDevCore/tools/gcil/commit/6827fb169dd5f342bbba2cfeefbb6925951c5c12))

### ⚙️ Cleanups

- coverage: remove unused function 'docker / _container' ([3e897e5](https://gitlab.com/RadianDevCore/tools/gcil/commit/3e897e5bfdc79d09bbdd04e1264eb0f0190440fd))


<a name="4.1.2"></a>
## [4.1.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.1.1...4.1.2) (2021-07-11)

### 🐛 Bug Fixes

- resolve #187: check support for non-UTF-8 boxes outputs ([1b9f858](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b9f8589783fb0808dc0f9d2ed6fbc19e6b5a85a))
- resolve #187: check support for non-UTF-8 histories outputs ([9f683c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/9f683c29cf275217d73dda733ad8ce86199d8fdf))

### 📚 Documentation

- changelog: regenerate release tag changes history ([55c7142](https://gitlab.com/RadianDevCore/tools/gcil/commit/55c71424ba791eb3823ddd5a162880f28a7880d4))

### ⚙️ Cleanups

- gitlab-ci: restore needs: 'Coverage Windows' for SonarCloud ([aefa37d](https://gitlab.com/RadianDevCore/tools/gcil/commit/aefa37de47a594c3097eca7226bbfa61dda81cf9))


<a name="4.1.1"></a>
## [4.1.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.1.0...4.1.1) (2021-07-11)

### ✨ Features

- implement #184: add support for the 'default:' node ([d745112](https://gitlab.com/RadianDevCore/tools/gcil/commit/d745112f6433db989fa099a847896820d695abd7))

### 🐛 Bug Fixes

- resolve #192: support empty included files merges ([bcc11f7](https://gitlab.com/RadianDevCore/tools/gcil/commit/bcc11f73701860b1d809a834f9ea1360893baade))
- resolve #192: also merge the 'default' node as additions ([28847eb](https://gitlab.com/RadianDevCore/tools/gcil/commit/28847eb1d8da7a55ad07881d6b59858b0a309ab7))

### 📚 Documentation

- changelog: regenerate release tag changes history ([5698509](https://gitlab.com/RadianDevCore/tools/gcil/commit/5698509939785165a4c45486dce70845c3275f83))

### 🧪 Test

- finish #191: run 'includes/variables' test and run on host ([3abbfe7](https://gitlab.com/RadianDevCore/tools/gcil/commit/3abbfe7a2cb5874de5d36a22939d0681f448dbbd))

### ⚙️ Cleanups

- prepare #184: refactor '__globals' without iterators ([b05c211](https://gitlab.com/RadianDevCore/tools/gcil/commit/b05c2115a948c2f38a6de286e0c68b934c991413))
- lint: resolve all new pylint warnings in the sources ([632a0ef](https://gitlab.com/RadianDevCore/tools/gcil/commit/632a0ef890ea93c667a7a96bbf1cbea4dbd59eef))
- lint: reduce and resolve some pylint disabled rules ([ffaa8eb](https://gitlab.com/RadianDevCore/tools/gcil/commit/ffaa8eb7848204eeb77e2b7b7b5471e9c8eaef89))
- tests: run the 'disabled' tests on the native host ([ad11818](https://gitlab.com/RadianDevCore/tools/gcil/commit/ad118184363e2d7800fe4b5506c9b0d6f5dd3c70))
- requirements: use my fixed 'gitlab-release' personal fork ([839562a](https://gitlab.com/RadianDevCore/tools/gcil/commit/839562a3d1d955275679316cff4ed274e95d8486))
- gitlab-ci: fix 'Coverage Windows' issues with pip and wheel ([c2a5ec0](https://gitlab.com/RadianDevCore/tools/gcil/commit/c2a5ec01a2179bc383ec76d310454ddac5fea344))


<a name="4.1.0"></a>
## [4.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/4.0.0...4.1.0) (2021-07-08)

### ✨ Features

- implement #183: pull the containers images of 'services:' ([0b3e2d6](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b3e2d6d377c46b44f797d0cfe3a492e284d7663))
- implement #182: add support for migration paths in 'Updates' ([f09b751](https://gitlab.com/RadianDevCore/tools/gcil/commit/f09b751f49907f03c2acf94829d064ac74dce357))
- prepare #181: bind DinD sockets if services are unsupported ([c181cdb](https://gitlab.com/RadianDevCore/tools/gcil/commit/c181cdb9d4cafd13e88d206d87dac6686d3b43a7))
- resolve #191: add support for 'variables:' includes ([4fe0138](https://gitlab.com/RadianDevCore/tools/gcil/commit/4fe0138865f91a09488aaa50bbb2f966959b7bf0))

### 🐛 Bug Fixes

- resolve #183: ensure multiple global services are all added ([baef11a](https://gitlab.com/RadianDevCore/tools/gcil/commit/baef11a36289ca93f35064df056a17d0c61850cd))
- resolve #185: use the 'podman' binary variable in 'cmd_exec' ([4c4bedf](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c4bedf424c1e2c80fc912d779abb25ea58c4232))
- prepare #181: drop support for engine partial name inputs ([e68827c](https://gitlab.com/RadianDevCore/tools/gcil/commit/e68827c24a9ecf1c0b80439fb2320dd46cfe86aa))

### 📚 Documentation

- changelog: regenerate release tag changes history ([db61990](https://gitlab.com/RadianDevCore/tools/gcil/commit/db619902b3d4ef3986229b37b13f9bf3b1532dc7))

### 🧪 Test

- finish #183: pull existing image in sockets services tests ([85aab56](https://gitlab.com/RadianDevCore/tools/gcil/commit/85aab569f4a87e09a355b181e88507598bcc6e6d))

### ⚙️ Cleanups

- gitlab-ci: minor codestyle cleanups of requirements ([e852aca](https://gitlab.com/RadianDevCore/tools/gcil/commit/e852aca56271190e65b0d6ce34411d5756257a6a))
- gitlab-ci: use the standard 'docker:dind' service image ([f3d0d56](https://gitlab.com/RadianDevCore/tools/gcil/commit/f3d0d5685a792639b3cbf54656ba0f5532d9fce4))
- markdownlint: extend line lengths to 150 characters max ([7940b7e](https://gitlab.com/RadianDevCore/tools/gcil/commit/7940b7e3f5aa9517650cb171fc92606ef9d58309))
- platform: minor codestyle improvement for print flush ([ed7e9aa](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed7e9aab57c8e522770da1f68cf7e70fa56c961e))
- prepare #183: hold services name in a data dictionnary ([06ff3cf](https://gitlab.com/RadianDevCore/tools/gcil/commit/06ff3cfdcd5c41626f1741d9a6d8ead1ea493b0d))
- prepare #183: extract the services 'alias' key as well ([6494771](https://gitlab.com/RadianDevCore/tools/gcil/commit/649477190f7bbdf0bc7f8b44d81f4f9820802ad3))
- prepare #185: import engine modules per class directly ([123f964](https://gitlab.com/RadianDevCore/tools/gcil/commit/123f9642e6e185698e77061ce37ebf7238e8f524))
- prepare #185: use 'name' and 'folder' as Scripts properties ([d63d9c7](https://gitlab.com/RadianDevCore/tools/gcil/commit/d63d9c77baf8f684feee477f996f695b4dc26cb1))
- prepare #185: isolate Volumes string builder to 'stringify' ([54a607a](https://gitlab.com/RadianDevCore/tools/gcil/commit/54a607a8a165ee1f315cb6f90932fec1603f7b99))
- prepare #181: get 'random' strings with letters and digits ([91c5a13](https://gitlab.com/RadianDevCore/tools/gcil/commit/91c5a1323fcfdca031bedc958be58c1423628d9d))
- prepare #181: add 'quote' method for the Strings class ([b7a9fc7](https://gitlab.com/RadianDevCore/tools/gcil/commit/b7a9fc7ad64893491dbdba189af4bc8b644b56c8))
- gitlab-ci: ignore Pylint 'duplicate-code' warnings ([9cfd862](https://gitlab.com/RadianDevCore/tools/gcil/commit/9cfd862f353b0a82280798731a595b22483d80ca))
- gitlab-ci: use 'needs' instead of 'dependencies' for tests ([3af9ef7](https://gitlab.com/RadianDevCore/tools/gcil/commit/3af9ef79df3ad2cf90588438a7f2aa50e13fe3a9))
- gitlab-ci: migrate to Podman 3.0.x configuration files ([44bc735](https://gitlab.com/RadianDevCore/tools/gcil/commit/44bc7352620db38fc1a44b80e5e018beffe11769))
- finish #185: refactor with container members and properties ([b5149ff](https://gitlab.com/RadianDevCore/tools/gcil/commit/b5149ffc2768a52ab896d50ee30640632c99687d))
- prepare #181: pass 'services' and script folder to 'run()' ([455f691](https://gitlab.com/RadianDevCore/tools/gcil/commit/455f69152c2f7e4ebba96f7301497188b5238025))
- prepare #185: handle the 'sockets' feature at engine level ([219121c](https://gitlab.com/RadianDevCore/tools/gcil/commit/219121c2c5c9bf6c54562352fbe2a7d43e5e0745))
- cleanup #181: drop the unused 'engine.services' property ([ec5c93d](https://gitlab.com/RadianDevCore/tools/gcil/commit/ec5c93dad09067c97ed64b00a6b6d235a069e32f))
- types: disable coverage of Windows specific or unused codes ([f30ebc7](https://gitlab.com/RadianDevCore/tools/gcil/commit/f30ebc79ff94f4bada620dd9a69f913fe4928be3))
- gitlab-ci: run tests only on Python 3.6 (old) and 3.9 (new) ([c5ba6dc](https://gitlab.com/RadianDevCore/tools/gcil/commit/c5ba6dc2f6808612746a096de197fe58f4a078d1))
- gitlab-ci: ensure 'Build' runs without jobs dependencies ([4b76f9f](https://gitlab.com/RadianDevCore/tools/gcil/commit/4b76f9fa9d04121a59ea0b4aecbd27f4c671d97f))
- finish #185: avoid the unreliable __del__ 'remove()' calls ([d6150f6](https://gitlab.com/RadianDevCore/tools/gcil/commit/d6150f6345b724c4317efab241b33b40675780c8))
- gitlab-ci: improve 'Python Local' tests with sudo installs ([79dee6d](https://gitlab.com/RadianDevCore/tools/gcil/commit/79dee6d505f67ecd78be2aec162797b655c43184))
- gitlab-ci: add tests execution times with a 'time' wrapper ([3a8fa50](https://gitlab.com/RadianDevCore/tools/gcil/commit/3a8fa5099bd7df91b21f2ad1ab06296b171d5b71))
- tests: configure 'pexpect-executor' delays to reduce times ([da1fcc6](https://gitlab.com/RadianDevCore/tools/gcil/commit/da1fcc66e02e05716fc2cad1aec5976986864188))
- histories: use fake durations for 'time' coverage tests ([234567b](https://gitlab.com/RadianDevCore/tools/gcil/commit/234567bc68e716f58648adce71cbecf47f9e92b4))
- tests: reduce some tests duration with native runs ([467a01b](https://gitlab.com/RadianDevCore/tools/gcil/commit/467a01b6aaf4d9106f81b91e694ea87488c96422))
- vscode: ensure Prettier formatters use single quotes only ([917296a](https://gitlab.com/RadianDevCore/tools/gcil/commit/917296ad0d929488303ab34164c88514f33fb859))
- gitlab-ci: disable 'Coverage Windows' for the moment ([30ac9c6](https://gitlab.com/RadianDevCore/tools/gcil/commit/30ac9c659119b5ac2e2321fc1d944c575400cc9a))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.1.2...4.0.0) (2021-02-21)

### ✨ Features

- implement #160: enable the sockets option with dind services ([9ce6257](https://gitlab.com/RadianDevCore/tools/gcil/commit/9ce625708605c892ecd1e042cca8a79989828bed))
- resolve #166: add support for DOCKER_HOST sockets ([61da4b3](https://gitlab.com/RadianDevCore/tools/gcil/commit/61da4b3df8a77c9914eb9a16c927cb7d49ab6481))
- resolve #161: add support for Docker sockets on Windows ([3043894](https://gitlab.com/RadianDevCore/tools/gcil/commit/304389429e9d8a5b07f59c10c845e91606c39b22))
- resolve #165: handle empty job stages and missing stages ([cfd3cd8](https://gitlab.com/RadianDevCore/tools/gcil/commit/cfd3cd8a98b2292485c44ce17e7a08ea7b9231a9))
- implement #167: support Podman default network interface ([367e5b8](https://gitlab.com/RadianDevCore/tools/gcil/commit/367e5b85f4321c8ed5d32cebe0c0ef79e0f48e73))
- resolve #168: explicitly use docker.io registry for Podman ([4694738](https://gitlab.com/RadianDevCore/tools/gcil/commit/4694738f5a5ca5da5f4a5f6ff9d180ff523b2226))
- implement #169: add pipeline / jobs histories and refactor ([b191579](https://gitlab.com/RadianDevCore/tools/gcil/commit/b191579fe275eb8b59520a8735c97637cefd1cae))
- implement #174: set CI_COMMIT_SHA and CI_COMMIT_SHORT_SHA ([3292b40](https://gitlab.com/RadianDevCore/tools/gcil/commit/3292b408ec88d4f5dd106325a3d35f6280d882ee))
- resolve #176: share DOCKER_CERT_PATH and DOCKER_TLS_VERIFY ([99c2c73](https://gitlab.com/RadianDevCore/tools/gcil/commit/99c2c7369283e3c9aae57d051662c07caec26753))
- prepare #118: add an 'EXPERIMENTAL' to enable Docker sockets ([92e2e57](https://gitlab.com/RadianDevCore/tools/gcil/commit/92e2e57b9d3874c28800bd55cbcd290dc7711402))

### 🐛 Bug Fixes

- resolve #163: handle APIError fails in docker.supports() ([21ab0b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/21ab0b072b211a603990287b0c56aaee3d4d3c41))
- resolve #164: avoid --debug features if interrupted by Ctrl+C ([f62902a](https://gitlab.com/RadianDevCore/tools/gcil/commit/f62902a053cde71e8b666c1ab24420fa2ecbc877))
- prepare #165: consider nodes containing 'script' as jobs ([0548f44](https://gitlab.com/RadianDevCore/tools/gcil/commit/0548f4409f95ecf5aa3ff701bf2024dfaaa7e57c))
- resolve #172: fix one part .local:volumes items ([b6d050d](https://gitlab.com/RadianDevCore/tools/gcil/commit/b6d050d4b9c5fe6283c76b342565ea599faba61c))
- resolve #173: expand variables from the workdir value ([71a1eaa](https://gitlab.com/RadianDevCore/tools/gcil/commit/71a1eaa61264eff2efaef18130032f91d231aa09))
- finish #160: add support for the name: variant of 'services:' ([11f6387](https://gitlab.com/RadianDevCore/tools/gcil/commit/11f63871b2896a657a038ea8ad57731cf813c98e))
- resolve #175: ensure when: always jobs always run ([5f115a1](https://gitlab.com/RadianDevCore/tools/gcil/commit/5f115a10ce6b8fe86105ad91a6d51833fa8d2713))
- finish #174: add 'git' environment path and run local tests ([4284059](https://gitlab.com/RadianDevCore/tools/gcil/commit/4284059aaf99a946646d19ebdf4ba8b6a990078b))
- resolve #177: prepare version values only if needed ([bb9aed8](https://gitlab.com/RadianDevCore/tools/gcil/commit/bb9aed83f1732d261c170a7ab4d5a6e1e1985972))
- finish #177: add coverage for daily checks after a pipeline ([78817aa](https://gitlab.com/RadianDevCore/tools/gcil/commit/78817aade5cca86131125b07caddfe99d356f028))
- finish #160: fix handlings of 'dict' or 'str' services lists ([457c0ab](https://gitlab.com/RadianDevCore/tools/gcil/commit/457c0ab3198798f64f978b029780d57ab8ca3224))
- finish #160: add coverage of all environment variables ([e0b122c](https://gitlab.com/RadianDevCore/tools/gcil/commit/e0b122cfb8b69756abf87c8c916f0f6eac6014bb))
- finish #177: add coverage after daily checks with a pipeline ([e077be2](https://gitlab.com/RadianDevCore/tools/gcil/commit/e077be2745a726f2b5dc18a316b37df9ed7e0cb6))
- finish #160: remove unneeded 'dict' iterator on services type ([f77a0c8](https://gitlab.com/RadianDevCore/tools/gcil/commit/f77a0c891eb2ac2bbd40617fc350f07559388712))
- resolve #178: support all types of include: configurations ([9f228c5](https://gitlab.com/RadianDevCore/tools/gcil/commit/9f228c5568e7df7589e222475bbf8b2297a52114))
- resolve #179: expand home paths for volumes and workdir ([3ffdba4](https://gitlab.com/RadianDevCore/tools/gcil/commit/3ffdba49f8297ec4eb2d0439dbca0260b8bc6c37))
- finish #179: avoid resolving ~ on Windows hosts and refactor ([629a6e7](https://gitlab.com/RadianDevCore/tools/gcil/commit/629a6e741c2a6faf7902e0ab71fa32cbfb15c1b4))
- resolve #171: resolve support of Windows paths volumes mounts ([1797f40](https://gitlab.com/RadianDevCore/tools/gcil/commit/1797f40f66b18940f424d0ace72c6762f7bde49c))
- finish #171: support ';' separated git-bash paths expansions ([ba88d62](https://gitlab.com/RadianDevCore/tools/gcil/commit/ba88d62560ea05f3418ab5b6103a7897ac9a4ee8))
- finish #171: fixup MSYS paths translations upon volumes parse ([bb0fefc](https://gitlab.com/RadianDevCore/tools/gcil/commit/bb0fefcc1a9608ead2057729d11a3281c23b1174))

### 📚 Documentation

- finish #174: document CI_COMMIT_SHA and CI_COMMIT_SHORT_SHA ([621e245](https://gitlab.com/RadianDevCore/tools/gcil/commit/621e24531beebf22d3bdc3aa760f46f59be7237b))
- finish #160: document the 'services:' supported nodes ([4c42e4f](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c42e4f097d357169da104b598489e7382ef7a99))
- finish #178: document the 'include:' supported nodes ([c73bc58](https://gitlab.com/RadianDevCore/tools/gcil/commit/c73bc58b2f0ee1caced969d3c1ccea4b254ca3d6))
- preview: refresh the SVG for the latest 4.0.0 release ([bd54f4f](https://gitlab.com/RadianDevCore/tools/gcil/commit/bd54f4fbe4a1e966fa68b282682c7a82b5ef08c6))
- changelog: regenerate release tag changes history ([9f15702](https://gitlab.com/RadianDevCore/tools/gcil/commit/9f157023408c757594917a3232dd9f2b08a6eb4d))

### 🧪 Test

- test #160: run sockets tests only Docker supported hosts ([10c23c8](https://gitlab.com/RadianDevCore/tools/gcil/commit/10c23c884010ca388c33c0624f2fe35de599f703))
- test #167: add a coverage test for engine network modes ([a993aa4](https://gitlab.com/RadianDevCore/tools/gcil/commit/a993aa4fa3d2aec323491077a01f6e146c7cf65c))
- test #160: ensure DOCKER_HOST points to a working deamon ([3f2dba7](https://gitlab.com/RadianDevCore/tools/gcil/commit/3f2dba762730c4402af9034c2e19a4658f16e96b))
- test #160: adapt DOCKER_HOST for GitLab CI tests ([1c73bfb](https://gitlab.com/RadianDevCore/tools/gcil/commit/1c73bfb4a10e6ecf41938afc3bf4a6643a9ed385))
- test #160: resolve DinD pull executions without a timeout ([2f8f978](https://gitlab.com/RadianDevCore/tools/gcil/commit/2f8f9785663e0040a01a4726489226f57667064c))
- test #160: resolve the DOCKER_HOST hostname to IP for DinD ([7e9a98b](https://gitlab.com/RadianDevCore/tools/gcil/commit/7e9a98bf655c0d1bc552e704c2240853d3517264))
- finish #165: add 'trigger:' coverage with a faulty 'script:' ([70324cd](https://gitlab.com/RadianDevCore/tools/gcil/commit/70324cdc8feeffa87c32dd403b614bb2cf866171))
- test #178: validate all types of include: configurations ([ed15528](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed1552872b3eb50475c16c225dcbc04f03221420))
- finish #179: add a test with the "${PWD}" absolute path env ([a78bb87](https://gitlab.com/RadianDevCore/tools/gcil/commit/a78bb87e845d4ba0916d405632188a90b1ef61b9))
- finish #179: minor fixes of 'home' tests with /root workdir ([414938c](https://gitlab.com/RadianDevCore/tools/gcil/commit/414938c4ce270828a915d37301aaee78e39fb32f))

### ⚙️ Cleanups

- document #160: mention sockets are enabled by dind services ([565bf18](https://gitlab.com/RadianDevCore/tools/gcil/commit/565bf18ac0d8b1a2bae57ccddbec6e3f291a76b8))
- resolve #162: specific warnings about unsupported features ([6e4b64c](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e4b64c4028a58e5b993ea666de0edfcc95737f0))
- finish #162: mention real paths are available on macOS ([d66af16](https://gitlab.com/RadianDevCore/tools/gcil/commit/d66af166af0219dd576398bbd3baf9a8d78362a8))
- gitlab-ci: always push to SonarCloud on develop / master ([35865d7](https://gitlab.com/RadianDevCore/tools/gcil/commit/35865d7eeeb833be600a6065b703b78e8838d3ac))
- finish #160: unify the configurations cleanup in a function ([e514635](https://gitlab.com/RadianDevCore/tools/gcil/commit/e5146354f17f516cb7c4768eb23c87aa5dbffa32))
- finish #166: disable coverage of DOCKER_HOST offline cases ([8af1c4e](https://gitlab.com/RadianDevCore/tools/gcil/commit/8af1c4ef2971b16aed1cfe14c78722d0555d506f))
- features: isolate the pipelines filter into a function ([7abcc8f](https://gitlab.com/RadianDevCore/tools/gcil/commit/7abcc8f2dda06d5ddc8e69d93b2502b115c17ed4))
- finish #160: cleanup 'null' empty configurations fields ([4c005f2](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c005f290a65c6ea12fa69c5f05a4519080bf6b2))
- finish #169: use integer durations to avoid '1 seconds' ([c8df243](https://gitlab.com/RadianDevCore/tools/gcil/commit/c8df243b820c843711f267683e996678b65fa5a4))
- gitlab-ci: add 'Python DinD' local tests job with DinD ([7112003](https://gitlab.com/RadianDevCore/tools/gcil/commit/7112003b8e70815e6b158f8b87eb326dd2600f01))
- finish #169: remove the unused 'StageHistory.get' function ([05a54f7](https://gitlab.com/RadianDevCore/tools/gcil/commit/05a54f7444eee69993f457c970f83e2eb6a92900))
- finish #160: disable coverage of function 'Outputs.warning' ([ae4d8b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/ae4d8b0021ace8c52edc922217ea2ff57580d2cc))
- coverage: disable coverage of Windows specific sections ([35d9b39](https://gitlab.com/RadianDevCore/tools/gcil/commit/35d9b396738564d905396dac9387eb62880f8995))

### ◀️ Revert

- finish #168: let fixed Podman resolve short-names again ([8a23830](https://gitlab.com/RadianDevCore/tools/gcil/commit/8a2383009aa38820c25f5906fec177503af89919))


<a name="3.1.2"></a>
## [3.1.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.1.1...3.1.2) (2021-02-09)

### 🐛 Bug Fixes

- resolve #159: support nested anchor scripts syntaxes ([b065b47](https://gitlab.com/RadianDevCore/tools/gcil/commit/b065b477a2ba783ce9378a5b41ef1855b023aef0))

### 📚 Documentation

- changelog: regenerate release tag changes history ([da12ffe](https://gitlab.com/RadianDevCore/tools/gcil/commit/da12ffef162447da168153ad956cf119474ea66b))


<a name="3.1.1"></a>
## [3.1.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.1.0...3.1.1) (2021-01-31)

### 🐛 Bug Fixes

- resolve #158: prevent regex matches in interactive menus ([a82bd73](https://gitlab.com/RadianDevCore/tools/gcil/commit/a82bd737859204498a158b9871e359acaa6db67b))

### 📚 Documentation

- changelog: regenerate release tag changes history ([4e17da1](https://gitlab.com/RadianDevCore/tools/gcil/commit/4e17da1b844e52017dc5e15d616b95a069aa6c49))


<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.0.2...3.1.0) (2021-01-30)

### ✨ Features

- implement #157: see the job name upon result for readability ([41248b5](https://gitlab.com/RadianDevCore/tools/gcil/commit/41248b517df8cab3a6e59f05a1464a32924551ca))

### 🐛 Bug Fixes

- resolve #156: expand nested variables values like GitLab CI ([4c6bd45](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c6bd45124651615eabec76fccbf04456fff4142))

### 📚 Documentation

- changelog: regenerate release tag changes history ([ac5b27b](https://gitlab.com/RadianDevCore/tools/gcil/commit/ac5b27bdaf83587494b9adf8d2edd854007b3410))

### 🧪 Test

- gitlab-ci: raise libseccomp2 to 2.5.1-1 for Podman tests ([e40c8c9](https://gitlab.com/RadianDevCore/tools/gcil/commit/e40c8c9b38e84d4b77179b693a993be8a7533759))
- test #156: resolve 'project' variables being now handled ([2e92347](https://gitlab.com/RadianDevCore/tools/gcil/commit/2e92347bed5309579e38ba43edc7f06b46643e33))
- gitlab-ci: fix Podman VFS storage driver with STORAGE_DRIVER ([c6eb01e](https://gitlab.com/RadianDevCore/tools/gcil/commit/c6eb01e417485887bf772050ec1357dd3816b698))

### ⚙️ Cleanups

- run: handle scripts failures upon job lines executions ([d9b032d](https://gitlab.com/RadianDevCore/tools/gcil/commit/d9b032db8b0c1bbe15bb84c0cf65739ddad379d6))
- test: minor codestyle improvements in TEST.md ([818a0bf](https://gitlab.com/RadianDevCore/tools/gcil/commit/818a0bf80b133f01c7701787caebed5097408556))
- gitlab-ci: remove unnecessary 'wget' for 'Coverage Windows' ([96dd975](https://gitlab.com/RadianDevCore/tools/gcil/commit/96dd9759bc01e17f1cfb1b825616e5527a69330b))
- gitlab-ci: allow to use the 'SUITE' for regular tests jobs ([67f2264](https://gitlab.com/RadianDevCore/tools/gcil/commit/67f2264597c1b47cfcabb9ca6a56867c8785cc29))
- readme: resolve a minor typo about --settings in README ([667e380](https://gitlab.com/RadianDevCore/tools/gcil/commit/667e380c45da2fab591efaa706044e74cdd89bc5))
- readme, test: add Android 11 to the tested environments ([02a3065](https://gitlab.com/RadianDevCore/tools/gcil/commit/02a30657d0fb813c739f1ff0b9f5585131154a80))
- gitlab-ci: synchronize stderr outputs with stdout outputs ([c667947](https://gitlab.com/RadianDevCore/tools/gcil/commit/c6679471a6d063dc9013c774987127ffeab93647))
- docs: refresh the preview SVG for the latest 3.1.0 release ([36a8e7a](https://gitlab.com/RadianDevCore/tools/gcil/commit/36a8e7a9afef946d22b024f9bd95851c6fe015be))


<a name="3.0.2"></a>
## [3.0.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.0.1...3.0.2) (2020-12-23)

### 🐛 Bug Fixes

- resolve #121: handle broken pipe upon logs outputs ([6b31aee](https://gitlab.com/RadianDevCore/tools/gcil/commit/6b31aee601ca732ec2396e7bdf2e9a9bbbc4a6ac))

### 📚 Documentation

- changelog: regenerate release tag changes history ([7502f1e](https://gitlab.com/RadianDevCore/tools/gcil/commit/7502f1e2f25f4ba3291480977607b9f4dc950c1c))

### 🧪 Test

- regex,simple: rename the jobs' stages to match the tests ([56aa90c](https://gitlab.com/RadianDevCore/tools/gcil/commit/56aa90cb48abe4ef8526f2b3e1946ad6b86d093f))

### ⚙️ Cleanups

- gitlab-ci: run develop pipeline upon 'CHANGELOG.md' changes ([fadb506](https://gitlab.com/RadianDevCore/tools/gcil/commit/fadb5063efc207b7caad2f942a48b010119a5d75))
- features: turn the 'launcher' into a pipeline feature class ([828ef07](https://gitlab.com/RadianDevCore/tools/gcil/commit/828ef07f018df9a57ec2ac8fc393e99013048047))
- parsers: isolate 'parser.read' to a 'Parsers' class ([9c8b5e6](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c8b5e6ce33dd8fe64c8563520b723ef583759ac))
- parsers: isolate 'parse' and 'stage' to the 'GitLab' class ([ab0f7da](https://gitlab.com/RadianDevCore/tools/gcil/commit/ab0f7dac68b8c9df0b76b29f636f87f6310c671c))
- features: fix 'PipelinesFeature' feature class name ([46b6367](https://gitlab.com/RadianDevCore/tools/gcil/commit/46b6367faa6d073f99d9cf3ea80406cceb8f7bcd))
- features: isolate 'select' and 'configure' to 'Menus' class ([be25868](https://gitlab.com/RadianDevCore/tools/gcil/commit/be2586829932b23603576f7d7956d3dcd8dedfac))
- features: rename 'jobs' feature to 'ConfigurationsFeature' ([dc398d3](https://gitlab.com/RadianDevCore/tools/gcil/commit/dc398d37ee12497449fcaf92eaaa6c382fc4028e))
- jobs: isolate 'runner' function to a 'Jobs' class ([c881aa8](https://gitlab.com/RadianDevCore/tools/gcil/commit/c881aa853666b1876aec38b8d0f3ff5fd95ad807))
- jobs: isolate script sources to a 'Scripts' class ([64a4324](https://gitlab.com/RadianDevCore/tools/gcil/commit/64a4324fc2e13844698a416669f1a3e885d044ba))
- bundle,jobs: isolate env binary paths and jobs variables ([b69f8fc](https://gitlab.com/RadianDevCore/tools/gcil/commit/b69f8fc73064a784d50257e715530507b81a2a4d))
- vscode: ignore '.ropeproject' folder from tracked files ([d3a80e3](https://gitlab.com/RadianDevCore/tools/gcil/commit/d3a80e327eff357c2f8e65795278bb0b79980631))
- jobs: refactor 'run()' into an 'Outputs' class and methods ([027b355](https://gitlab.com/RadianDevCore/tools/gcil/commit/027b355f1ade41eba864cb00e7bef46a4b3fafd6))
- parsers: refactor 'parse()' into separated methods ([ebf19ed](https://gitlab.com/RadianDevCore/tools/gcil/commit/ebf19ed88e85915a631e414677995c98455d6252))


<a name="3.0.1"></a>
## [3.0.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/3.0.0...3.0.1) (2020-12-22)

### ✨ Features

- implement #155: add arguments categories for readability ([b741d82](https://gitlab.com/RadianDevCore/tools/gcil/commit/b741d8263996c3f484678bf3c993e2a110883588))

### 📚 Documentation

- changelog: regenerate release tag changes history ([977b949](https://gitlab.com/RadianDevCore/tools/gcil/commit/977b9491b7a2c58c523ca203b94961ca4a4414a3))

### ⚙️ Cleanups

- prints: isolate PyInquirer themes into a 'Menus' class ([50c485b](https://gitlab.com/RadianDevCore/tools/gcil/commit/50c485b24a41ea7fcbb913df697724dab3a415b3))
- cli: isolate the CLI main entrypoint to a cli/ submodule ([1d8c83a](https://gitlab.com/RadianDevCore/tools/gcil/commit/1d8c83a1e7b1aa90e149d14bff323c467b63b75f))
- types: reduce unrequired nested if conditions ([a9c32d0](https://gitlab.com/RadianDevCore/tools/gcil/commit/a9c32d0e4a26452326dcf94fb6661d9cba7daaaa))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.3.0...3.0.0) (2020-12-22)

### 🐛 Bug Fixes

- resolve #151: enforce WinPTY and improve coverage ([7bcd334](https://gitlab.com/RadianDevCore/tools/gcil/commit/7bcd33424b19fdcf2bfaad5c8d55212a2b02ed18))
- resolve #151: configurable WinPTY and limited coverage checks ([ced507b](https://gitlab.com/RadianDevCore/tools/gcil/commit/ced507bce00880718c52992f95b3110e1869f1d3))
- resolve #152: avoid sudoer access from root user ([7435544](https://gitlab.com/RadianDevCore/tools/gcil/commit/7435544a333b91ecdf096b07e21eca3391aa18cb))
- resolve #153: ensure signals are restored and reraised ([77ec442](https://gitlab.com/RadianDevCore/tools/gcil/commit/77ec44262dc082cbb897c0da0c3a1346f385446f))
- resolve #154: preserve variables priority and override order ([ab677a7](https://gitlab.com/RadianDevCore/tools/gcil/commit/ab677a79a5087981c15889d4317dfc62e67c6819))

### 📚 Documentation

- readme: minor codestyle cleanups of the Linux support table ([ec4e24e](https://gitlab.com/RadianDevCore/tools/gcil/commit/ec4e24e0dd5f9983871fdfde19f6912080e3d303))
- readme: add missing modules dependencies and references ([bb0093c](https://gitlab.com/RadianDevCore/tools/gcil/commit/bb0093cb3291cadc3124bf65c9a6ae1501848594))
- changelog: regenerate release tag changes history ([8754fa3](https://gitlab.com/RadianDevCore/tools/gcil/commit/8754fa3f9140b4b4b387433441bb08a438fb9c0e))

### 🧪 Test

- images: use pexpect-executor to pull with an interactive TTY ([8e47309](https://gitlab.com/RadianDevCore/tools/gcil/commit/8e4730974a6b39e8ef3a5ad8fe710f4b0b9745a0))

### ⚙️ Cleanups

- changelog: add a cleanup option to hide changelog commits ([962fc7d](https://gitlab.com/RadianDevCore/tools/gcil/commit/962fc7d8d9ef852fea1c5b50da58dacb1d62a56e))
- changelog: configure groups titles detailed map for chglog ([6709055](https://gitlab.com/RadianDevCore/tools/gcil/commit/67090552cd2cb5ddabcb36c4980f371e2b06d2b0))
- vscode: disable chords terminal features to allow Ctrl+K ([26eecb1](https://gitlab.com/RadianDevCore/tools/gcil/commit/26eecb19dd7401fc0f1fab424a67b853673db19f))
- gitlab-ci: set host and tool envs for pexpect-executor ([ce50a96](https://gitlab.com/RadianDevCore/tools/gcil/commit/ce50a96c4642fc38dc6cc1d3f93657234fbae2a9))
- gitlab-ci: use updated 'docker:19-dind' image for 19.03.14 ([b9e0aef](https://gitlab.com/RadianDevCore/tools/gcil/commit/b9e0aeffe9b73f82e141d6d64005e657014b8f05))
- gitlab-ci: hide pip warnings and coverage report errors ([c28199b](https://gitlab.com/RadianDevCore/tools/gcil/commit/c28199ba513394b3310a3bcb80cbbc4579498ec8))
- prepare #149: add simulated macOS environment and cleanup ([6b0171e](https://gitlab.com/RadianDevCore/tools/gcil/commit/6b0171e313dd5ea23fc1b14f410853f5e9833e3b))
- implement #149: handle simulated settings for virtual tests ([52aa362](https://gitlab.com/RadianDevCore/tools/gcil/commit/52aa362d016e5d0f8df105952dc4ef836a8e12bf))
- test #149: add macOS simulated test for settings coverage ([c7e2963](https://gitlab.com/RadianDevCore/tools/gcil/commit/c7e2963ffb59d09a248299a5a95926a92ec92c36))
- coverage: ignore safety unused code lines ([b3e23af](https://gitlab.com/RadianDevCore/tools/gcil/commit/b3e23af80daac4a2036e67dc73cb0ca2e2937cb5))
- vscode: ignore '.tmp.entrypoint.*' files in VSCode ([5bfe05a](https://gitlab.com/RadianDevCore/tools/gcil/commit/5bfe05aa8913ed948ae663fa485fc018e9b48036))
- engines: refactor 'help' into 'cmd_exec' for coverage tests ([d785f52](https://gitlab.com/RadianDevCore/tools/gcil/commit/d785f52de320e74ae9403d07e4bd486f5d599699))
- coverage: add '.coveragerc' to strip Linux / Windows paths ([661daef](https://gitlab.com/RadianDevCore/tools/gcil/commit/661daef96fb80bcf07c59dbe1ee3a5a6dff828e2))
- gitlab-ci: add 'Coverage Windows' tests with PyWine image ([2b384a1](https://gitlab.com/RadianDevCore/tools/gcil/commit/2b384a14b9f2cd103c183cac9a65e12f55498277))
- resolve #150: restrict Dicts iterators and improve coverage ([957d35f](https://gitlab.com/RadianDevCore/tools/gcil/commit/957d35f3a63257f5d84b435732988dd624a1dff7))
- test: add sudoer '--debug' Podman engine test ([0ecd180](https://gitlab.com/RadianDevCore/tools/gcil/commit/0ecd1806fb8bc9469da8c7b4cdcc08254121b1a0))
- gitlab-ci: ensure coverage XML files use relative sources ([750a3f7](https://gitlab.com/RadianDevCore/tools/gcil/commit/750a3f776271001d2cc3cc1b4f2931955117773d))
- types: ignore 'Volumes' Windows case from coverage results ([9693b22](https://gitlab.com/RadianDevCore/tools/gcil/commit/9693b2249173fd13699f0fda598576b5274f178c))
- gitlab-ci: unify local VSCode coverage to a common XML file ([cdd8da7](https://gitlab.com/RadianDevCore/tools/gcil/commit/cdd8da7a79b4d929a25fa807cc4a9e139d8a0ae4))
- test #152: implement permissions tests for temp files ([a4d60ed](https://gitlab.com/RadianDevCore/tools/gcil/commit/a4d60ede1e3ae5d245ddaf7225b86c9be599c359))
- engines: ignore 'exec()' from coverage rather than comment ([a87dab8](https://gitlab.com/RadianDevCore/tools/gcil/commit/a87dab80c123f58a49b8960e09e75c1ed923d237))
- gitlab-ci: unify template scripts and add stages comments ([4b7ed17](https://gitlab.com/RadianDevCore/tools/gcil/commit/4b7ed1793368f8f9a1f9a0553fe7793a0d3bd5ee))
- test #153: test reraised signals and 'Files.clean' coverage ([f67a5d0](https://gitlab.com/RadianDevCore/tools/gcil/commit/f67a5d03e5c54705cddd42f51a68335131c5aea4))
- gitlab-ci: use 'pip3' instead of 'pip' in tests template ([acb55f1](https://gitlab.com/RadianDevCore/tools/gcil/commit/acb55f1389a81e1bef180c1ad1409d570b9c884c))
- run: adapt 'run.sh' to missing sudo and wine support ([2cdf805](https://gitlab.com/RadianDevCore/tools/gcil/commit/2cdf8055c2dde699781e2de3cad7bedeb644767f))
- finish #151: support non-WinPTY execution environments ([921c465](https://gitlab.com/RadianDevCore/tools/gcil/commit/921c465fd09b05dd9c3c6752ea62988b2013a749))
- test: add '--sockets' and host failures coverage tests ([3210416](https://gitlab.com/RadianDevCore/tools/gcil/commit/321041683222cc074ebec4cbae94059e8ebf36d1))
- test: add empty '{before,after}_script' and 'script' tests ([b2cc355](https://gitlab.com/RadianDevCore/tools/gcil/commit/b2cc355dca35db9e7cc7abe602d7af45e901c9a7))
- test: finish 'extends' coverage with two 'variables:' nodes ([93af8b7](https://gitlab.com/RadianDevCore/tools/gcil/commit/93af8b73680344a4965fc32ac536e643e3b55a4b))
- test: finish 'variables' coverage of environment overrides ([00b6764](https://gitlab.com/RadianDevCore/tools/gcil/commit/00b67641c5143c52e6cd6c25563b48ceeacd62ea))
- gitlab-ci: support ',' separated SUITE values for coverage ([2755229](https://gitlab.com/RadianDevCore/tools/gcil/commit/27552296704adbac7e79ad25227c90d41566e2aa))
- test: finish parser coverage of .env environment override ([3c5d2d5](https://gitlab.com/RadianDevCore/tools/gcil/commit/3c5d2d5c1eb5f7e3c7c7c58de9eed756a69609a8))
- docs: use pexpect-executor 1.2.0 to hold the final prompt ([4b6ec6a](https://gitlab.com/RadianDevCore/tools/gcil/commit/4b6ec6a12e60cf088db646911baad6b72012b878))
- gitlab-ci: add a job-specific report to 'Coverage' jobs ([c66bb66](https://gitlab.com/RadianDevCore/tools/gcil/commit/c66bb66411859c263c533c18304ca0be4947d2b5))
- docs: refactor the 'Preview' job into a 'termtosvg' job ([5774040](https://gitlab.com/RadianDevCore/tools/gcil/commit/5774040d0b6ceece8dd2b14a25eaeabbb1fb3dca))


<a name="2.3.0"></a>
## [2.3.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.2.3...2.3.0) (2020-12-14)

### ✨ Features

- implement #142: add --rmi to remove container images ([fd18760](https://gitlab.com/RadianDevCore/tools/gcil/commit/fd187601ac95cc71af6b3d770f2e9705623d61d3))
- implement #143: add --force to force pull container images ([31effc3](https://gitlab.com/RadianDevCore/tools/gcil/commit/31effc302598c3eeef20c8d4a92a978957a5875c))
- implement #144: add -i to ignore jobs name case distinctions ([a0f3e0b](https://gitlab.com/RadianDevCore/tools/gcil/commit/a0f3e0ba539343e9f56fa598a8fbff19f01e9d18))
- finish #144: add missing regex check for -i case option ([532683c](https://gitlab.com/RadianDevCore/tools/gcil/commit/532683c021cbbbc2dc8ad2f883b7b7c98f9a38d4))
- updates: improve updates colors and embed new test flags ([24a4c84](https://gitlab.com/RadianDevCore/tools/gcil/commit/24a4c84fdbd4a9ff724a5d6e3f19eb5c809422b7))

### 🐛 Bug Fixes

- finish #137: delete temporary files only if they still exist ([23bcb26](https://gitlab.com/RadianDevCore/tools/gcil/commit/23bcb26bebfa67fab72cb20c9c0731d2da26cb58))
- resolve #145: Handle configurations Dicts index out of range ([4028e53](https://gitlab.com/RadianDevCore/tools/gcil/commit/4028e53e16f914521bb52391c4a27313b82b520b))
- resolve #147: default YAML or JSON value if non-interactive ([6410eec](https://gitlab.com/RadianDevCore/tools/gcil/commit/6410eec5b0210f71bbe0f4190a425cabe07d9e14))
- resolve #146: ensure before_script really checks for issues ([c3f1c78](https://gitlab.com/RadianDevCore/tools/gcil/commit/c3f1c78e3102bee2c8ed56dbf51ee0b7ea5ec62f))
- resolve #148: handle JSON or YAML string as unique choice ([6ce036a](https://gitlab.com/RadianDevCore/tools/gcil/commit/6ce036a80497762e0d14b0926c6ba13af2f39e0d))

### 📚 Documentation

- changelog: regenerate release tag changes history ([c0ac01e](https://gitlab.com/RadianDevCore/tools/gcil/commit/c0ac01eb52c18876a5bf85d41bb07e8741be3bec))

### ⚙️ Cleanups

- resolve #141: refactor and fix SonarQube issues in parser ([6d6af33](https://gitlab.com/RadianDevCore/tools/gcil/commit/6d6af33475797cd5a9d791c0afbbaf2475b2a049))
- resolve #141: refactor and fix SonarQube issues for except: ([385cb2f](https://gitlab.com/RadianDevCore/tools/gcil/commit/385cb2f7a8ba9bfbc5148006f817f6c5e76bbe44))
- requirements: isolate all requirements to a folder ([0d97689](https://gitlab.com/RadianDevCore/tools/gcil/commit/0d9768921c1b6d1d62bc09305d020b0c82d32836))
- gitlab-ci: wrap preview.py delay out of the preview script ([0c2395d](https://gitlab.com/RadianDevCore/tools/gcil/commit/0c2395d192aa754f7329634fb479e4b450b5f5c5))
- readme: format the markdown sources automatically ([50a8d1a](https://gitlab.com/RadianDevCore/tools/gcil/commit/50a8d1adaa21e51b599acfe0d2090cdc2eb1c51f))
- gitlab-ci: create YAML anchors to reuse templates scripts ([2030f01](https://gitlab.com/RadianDevCore/tools/gcil/commit/2030f0144b7ba9b8f8fab977f3d4b99144c42855))
- gitlab-ci: add --settings and wrapped --update-check tests ([24b2e2a](https://gitlab.com/RadianDevCore/tools/gcil/commit/24b2e2a3ba7a1c6e3bbe2927a19155b6a7b11ef6))
- tests: add 'engines' tests from arguments and environment ([248ba92](https://gitlab.com/RadianDevCore/tools/gcil/commit/248ba92e482e77726d6ab3cf5e4e7b8fe893ecd8))
- engine: add support for -E '' as being default engines ([e101727](https://gitlab.com/RadianDevCore/tools/gcil/commit/e101727631148d0e8afd679727d2c24f70acdb8c))
- finish #142: isolate pull and rmi into a feature class ([e2322c8](https://gitlab.com/RadianDevCore/tools/gcil/commit/e2322c8094301e1b5fb53c4fb362ebe6337f1a84))
- version: support non-packaged sources version fallback ([ac1f920](https://gitlab.com/RadianDevCore/tools/gcil/commit/ac1f920a4e214df1e6c0094c3640e3be584b8d19))
- tests: refactor and isolate all unit tests ([f5a6f12](https://gitlab.com/RadianDevCore/tools/gcil/commit/f5a6f1280bf115667b02fb9c8a026d4c0069a581))
- parser: cleanup duplicated environment file checks ([84dd18c](https://gitlab.com/RadianDevCore/tools/gcil/commit/84dd18c39f07d7a5e62e269e80ad24ac5fb81a17))
- docs: migrate to the isolated 'pexpect-executor' package ([ab4498d](https://gitlab.com/RadianDevCore/tools/gcil/commit/ab4498d590f52f2406ddce511c75e5a539789e53))
- gitlab-ci: add 'Py3.9 Preview' test of ./docs/preview.py ([a04df51](https://gitlab.com/RadianDevCore/tools/gcil/commit/a04df516481dbb00b4228915602c3fe154fe0578))
- gitlab-ci: implement Python coverage reports for SonarCloud ([c436539](https://gitlab.com/RadianDevCore/tools/gcil/commit/c436539b6f68f7d8e1816e671f7d838bc8804849))
- coverage: ignore coverage of unreachable input securities ([f8a8d90](https://gitlab.com/RadianDevCore/tools/gcil/commit/f8a8d9047e955d87db2d08a8af080c79dc2aa4ea))
- vscode: migrate to 'brainfit.vscode-coverage-highlighter' ([4fb60a4](https://gitlab.com/RadianDevCore/tools/gcil/commit/4fb60a4cb78fbcfbd7e78ac398b9e8989d35f609))
- vscode: exclude intermediate files from the project view ([38d41a3](https://gitlab.com/RadianDevCore/tools/gcil/commit/38d41a3356038d3b002da4f96fba3b903cdd3b44))
- gitlab-ci: resolve 'SonarCloud' changes rules on develop ([ab2da73](https://gitlab.com/RadianDevCore/tools/gcil/commit/ab2da7386e58bee90f5d65ff67085570d68048b5))
- gitlab-ci: isolate coverage databses and allow suite tests ([98c6d99](https://gitlab.com/RadianDevCore/tools/gcil/commit/98c6d998e8ee291fdebe339c66169b600f3e70af))
- engine: disable the engine.exec command until required ([9674e61](https://gitlab.com/RadianDevCore/tools/gcil/commit/9674e61ed3873bbf2dda93a533050c55f869f564))
- tests: add 'gitlabci-local -c ./folder/' arguments test ([075048b](https://gitlab.com/RadianDevCore/tools/gcil/commit/075048bbf1990aeb4ffe98d81052419afa984868))
- gitlab-ci: remove 'mount' command execution in all tests ([a182a42](https://gitlab.com/RadianDevCore/tools/gcil/commit/a182a42183f492d8fce8ebe76e726056ae8d6882))
- tests: add 'gitlabci-local -i' with regex name tests ([c341e8f](https://gitlab.com/RadianDevCore/tools/gcil/commit/c341e8f2acd0d9f56347c666e808461f624689de))
- tests: add missing or incompatible Podman engine tests ([f65fed0](https://gitlab.com/RadianDevCore/tools/gcil/commit/f65fed01023c24a21db06fbe325badc21d6672c6))
- tests: add '--settings' specific tests and install 'sudo' ([e7b13c1](https://gitlab.com/RadianDevCore/tools/gcil/commit/e7b13c1131f38664b2e0463335166bf421bcf9aa))
- gitlab-ci: silent and hide all installation irrelevant logs ([d45c75b](https://gitlab.com/RadianDevCore/tools/gcil/commit/d45c75b27e4d76a5c8f4b0029067d6e79b52137f))
- gitlab-ci: run coverage and SonarCloud upon tests/ changes ([f483baa](https://gitlab.com/RadianDevCore/tools/gcil/commit/f483baa816ff823fb9b7624ae0621dd619679a37))
- version: exclude version '0.0.0' fallback from coverage ([99c6285](https://gitlab.com/RadianDevCore/tools/gcil/commit/99c62852419211a85f45a366eeca1b063027a3d6))
- gitlab-ci: unify coverage reports, unify and common scripts ([97f07c1](https://gitlab.com/RadianDevCore/tools/gcil/commit/97f07c1daf285e6945a9d220a6986f3c8231dcf7))
- tests: add unknown configurations test and raise error ([b6ac268](https://gitlab.com/RadianDevCore/tools/gcil/commit/b6ac2683b27f350df5628e82ade27a88e208072c))
- parser: handle 'FileNotFoundError' upon file parser ([354c4e4](https://gitlab.com/RadianDevCore/tools/gcil/commit/354c4e48a78f62493551fb01a96444da5f29e587))
- tests: add multiple unit tests to improve sources coverage ([b9495e4](https://gitlab.com/RadianDevCore/tools/gcil/commit/b9495e4c72da10743816a35e0ab906e6d1ce9620))
- tests: add time tests for 60+ seconds pipelines coverage ([1b2ae21](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b2ae21a93b04e7bccd2e4e8f4f37e61b544a913))
- tests: use 'ubuntu:20.04' for --bash/--debug for bash tests ([b907ef1](https://gitlab.com/RadianDevCore/tools/gcil/commit/b907ef1580e9b661d8be58b46b24c183c6185f98))
- runner: remove unused engine logs reader and try except ([2899282](https://gitlab.com/RadianDevCore/tools/gcil/commit/2899282aa95dab7e82e22b685f9c5234b97f8b6f))
- features: isolate 'dumper' into a 'Jobs' feature ([6f34d38](https://gitlab.com/RadianDevCore/tools/gcil/commit/6f34d38d82e5280ede6df213de34bf15b9afa76d))
- tests: migrate to pexpect-executor 1.0.1 with tests support ([cf9bed8](https://gitlab.com/RadianDevCore/tools/gcil/commit/cf9bed8120f5f617289643076c8f52ea42cb45ac))
- features: prevent YAML dump outputs lines from wrapping ([bbf418a](https://gitlab.com/RadianDevCore/tools/gcil/commit/bbf418a107ccc49e49c7152c8229123a02bbbf79))
- lint: isolate and identify 'Modules libraries' imports ([b2596fa](https://gitlab.com/RadianDevCore/tools/gcil/commit/b2596fa9390996652338e4d7eada210dfcb3debe))
- docs: resolve configurations test's 12th value support ([d9691f8](https://gitlab.com/RadianDevCore/tools/gcil/commit/d9691f8cf63ab4ecfae514c763b76d85eb710a96))
- tests: add interactive unit tests with pexpect-executor ([d6623a3](https://gitlab.com/RadianDevCore/tools/gcil/commit/d6623a313822f1eba1332432f5f4881317b0b497))
- coverage: ignore unused PyInquirer patcher lines coverage ([b0a6ada](https://gitlab.com/RadianDevCore/tools/gcil/commit/b0a6ada6ccd3d4a9cd2ae45ff55308fa7babc187))
- gitlab-ci: raise interactive tests timeout to 15 minutes ([1215e97](https://gitlab.com/RadianDevCore/tools/gcil/commit/1215e97ed2c0b30d70b60e009812779dba05c5bd))


<a name="2.2.3"></a>
## [2.2.3](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.2.2...2.2.3) (2020-12-10)

### 📚 Documentation

- changelog: regenerate release tag changes history ([9f6008b](https://gitlab.com/RadianDevCore/tools/gcil/commit/9f6008b69cd52af499162e9d2fa4f55eb4f41d01))

### ⚙️ Cleanups

- gitlab-ci: run build and tests jobs only if needed ([c024e01](https://gitlab.com/RadianDevCore/tools/gcil/commit/c024e01c8b720650bc0888a096929ddb41ffaf3c))
- gitlab-ci.yml: add support for SonarCloud analysis ([fe45ab5](https://gitlab.com/RadianDevCore/tools/gcil/commit/fe45ab5b4127afb734f0e433bcb34bd866558301))
- resolve #141: resolve SonarQube issue in engines.wait ([34aaae9](https://gitlab.com/RadianDevCore/tools/gcil/commit/34aaae9b1b3bf872d81ca82e2771a179c16ef3b5))
- resolve #141: minor codestyle cleanups raised by SonarCloud ([fb78f90](https://gitlab.com/RadianDevCore/tools/gcil/commit/fb78f900fc5080db337031d3929112f1c9602a96))
- readme: add pipeline and SonarCloud badges ([a1aff75](https://gitlab.com/RadianDevCore/tools/gcil/commit/a1aff75ecc8322612649254f2234170ebbff6c4e))
- gitlab-ci: prevent Podman unit tests to use Docker host ([918ae1f](https://gitlab.com/RadianDevCore/tools/gcil/commit/918ae1fe8f5f115cf106f160fc81e1240c0fd4ec))
- gitlab-ci: resolve Podman 2.2.1 issues in Debian 10.6 ([bcc759e](https://gitlab.com/RadianDevCore/tools/gcil/commit/bcc759e33c5629fe35b3df7cfd5a2c344bdcf477))


<a name="2.2.2"></a>
## [2.2.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.2.1...2.2.2) (2020-12-08)

### 🐛 Bug Fixes

- resolve #138: reset colors once the boxes are printed ([82f650c](https://gitlab.com/RadianDevCore/tools/gcil/commit/82f650c962ce3d4bdd558e450d5a9e786058cfee))
- resolve #139: support readonly parent folders for entrypoints ([b93643d](https://gitlab.com/RadianDevCore/tools/gcil/commit/b93643dad7f9902cc5b6e30ad500d4af24c5535c))
- resolve #137: ensure temporary scripts are always deleted ([db0e21b](https://gitlab.com/RadianDevCore/tools/gcil/commit/db0e21b1d7888d752aa60d4856cc9c4c355c8d63))

### 📚 Documentation

- prepare #140: add installation steps for all test platforms ([f06835d](https://gitlab.com/RadianDevCore/tools/gcil/commit/f06835dae9da296a6ee2fd81a47c30d9926ed890))
- resolve #140: mention Android native engine with Termux ([e16c8ef](https://gitlab.com/RadianDevCore/tools/gcil/commit/e16c8ef332f252701f6ae3b93d777415645b1064))
- resolve #140: add Android test environment explanations ([d651ca5](https://gitlab.com/RadianDevCore/tools/gcil/commit/d651ca5b4816728fe21ce058cb6e2da06c0f7dfd))
- changelog: regenerate release tag changes history ([8e52f5c](https://gitlab.com/RadianDevCore/tools/gcil/commit/8e52f5c70a5b3f28f778e23c85d4fedbf7ec6355))

### ⚙️ Cleanups

- resolve #140: add 'Platform.IS_ANDROID' unused constant ([42d662d](https://gitlab.com/RadianDevCore/tools/gcil/commit/42d662d1040361a8870c708f91682be183343f07))
- gitlab-ci: ignore Podman issues until podman-2.2.1 is fixed ([1d913aa](https://gitlab.com/RadianDevCore/tools/gcil/commit/1d913aa4d5055fb5b9202894c835bec4d80d3e0e))


<a name="2.2.1"></a>
## [2.2.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.2.0...2.2.1) (2020-12-07)

### ✨ Features

- resolve #136: adapt update hint to sudo-installed packages ([02add16](https://gitlab.com/RadianDevCore/tools/gcil/commit/02add16e768b1aa88d83b0b4a081324e24870aa0))

### 🐛 Bug Fixes

- resolve #135: wrap colored strings and adapt boxes dimensions ([bc72715](https://gitlab.com/RadianDevCore/tools/gcil/commit/bc727158d490b194fbd2e0308993a735ba8948bb))

### 📚 Documentation

- changelog: regenerate release tag changes history ([caa86da](https://gitlab.com/RadianDevCore/tools/gcil/commit/caa86dabb19e8ecb68b2bcd6c5a4054a3f0e6eab))

### ⚙️ Cleanups

- prepare #135: isolate string manipulators to 'Strings' type ([9a7e718](https://gitlab.com/RadianDevCore/tools/gcil/commit/9a7e7182f76004d1a69642410b42166dcbd9870a))


<a name="2.2.0"></a>
## [2.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.1.2...2.2.0) (2020-12-06)

### ✨ Features

- prepare #132: provide IS_USER_SUDO and USER_SUDO constants ([f620717](https://gitlab.com/RadianDevCore/tools/gcil/commit/f6207179a8bea55532629a3aa42545af8596a27a))
- implement #132: use the original userspace if using sudo ([2ea3521](https://gitlab.com/RadianDevCore/tools/gcil/commit/2ea352153a3aa390f83df0394935872356a8e974))
- implement #131: check for updates without delay upon exit ([d8bb431](https://gitlab.com/RadianDevCore/tools/gcil/commit/d8bb431fe696f1af6c8238856e7069c6d8448752))
- implement #133: add 'center' and 'strip' string manipulators ([cb3f75f](https://gitlab.com/RadianDevCore/tools/gcil/commit/cb3f75f3dc3fd6430f9da2377e731712474ebe96))
- prepare #131: create 'Boxes' class to create boxed messages ([9081f16](https://gitlab.com/RadianDevCore/tools/gcil/commit/9081f164451f741d27f3623e91ad5d3db65c22ca))
- implement #131: refactor the updates message with hints ([318822c](https://gitlab.com/RadianDevCore/tools/gcil/commit/318822cdbf3b21c2cf19e8c7b319995419630818))

### 📚 Documentation

- prepare #118: add supported macOS versions and update TEST ([b9ab913](https://gitlab.com/RadianDevCore/tools/gcil/commit/b9ab91360a860e34412c231c8516e74412dfeab6))
- changelog: regenerate release tag changes history ([2231dce](https://gitlab.com/RadianDevCore/tools/gcil/commit/2231dce7fd836146e8c1486015ea406ce2a97fa9))

### ⚙️ Cleanups

- readme: add 'native' local jobs as supported engine ([05ed640](https://gitlab.com/RadianDevCore/tools/gcil/commit/05ed640440e5c119019cb13dd8769510963b71fc))
- implement #133: isolate all colors attributes into a class ([a5f25b1](https://gitlab.com/RadianDevCore/tools/gcil/commit/a5f25b15e75191263f221e9639be0ec76a6c82d0))
- prepare #131: add 'REPOSITORY' GitLab URL link constant ([eb71493](https://gitlab.com/RadianDevCore/tools/gcil/commit/eb71493ac3af694d02cab28de91475bba9d999d9))
- resolve #134: isolate package names to a 'Bundle' class ([e3abae4](https://gitlab.com/RadianDevCore/tools/gcil/commit/e3abae4d3d0e10180bbaa66d86b1dd1e6310eba6))
- resolve #134: isolate environment variables inside 'Bundle' ([570db6b](https://gitlab.com/RadianDevCore/tools/gcil/commit/570db6b11af81749accb984078ca01cb388d38e6))
- changelog: create a CHANGELOG version description extractor ([02368d8](https://gitlab.com/RadianDevCore/tools/gcil/commit/02368d8bf3c7651c18a48feb3787e300bd194592))
- gitlab-ci: implement 'gitlab-release' to fill tags releases ([43e9d5e](https://gitlab.com/RadianDevCore/tools/gcil/commit/43e9d5e8e8af25fa1286652a8f9541963efe623d))


<a name="2.1.2"></a>
## [2.1.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.1.1...2.1.2) (2020-12-05)

### ✨ Features

- prepare #129: add '--settings' to show the path and contents ([8fa58c3](https://gitlab.com/RadianDevCore/tools/gcil/commit/8fa58c36a6e5ba83e86bb84e193b9c4f1903b202))

### 🐛 Bug Fixes

- resolve #129: import modules libraries before components ([6f43910](https://gitlab.com/RadianDevCore/tools/gcil/commit/6f43910ce1583b45e542b10bde4a8912eb01eb19))
- resolve #130: respect list selector single choice inputs ([a26ed72](https://gitlab.com/RadianDevCore/tools/gcil/commit/a26ed7227d6d46916cf0d46d2a77cca193be3957))

### 📚 Documentation

- resolve #129: document the settings configurations and goals ([96806db](https://gitlab.com/RadianDevCore/tools/gcil/commit/96806db6c491009665fe9b3abf9bb714ff11f498))
- changelog: regenerate release tag changes history ([ffa3773](https://gitlab.com/RadianDevCore/tools/gcil/commit/ffa37736cac736d1440eb2d5b3fe77137fa91937))

### ⚙️ Cleanups

- types: turn 'Paths' class methods into static methods ([0653d42](https://gitlab.com/RadianDevCore/tools/gcil/commit/0653d427761be01673135d9563cc856fe7c34cc7))
- readme: drop the unreadable and old usage short help header ([a53aa8a](https://gitlab.com/RadianDevCore/tools/gcil/commit/a53aa8ab58e71be394f99ca1cd4acfcaa133ca98))
- readme: add command usage entrypoint and shortcuts table ([3cf8ec2](https://gitlab.com/RadianDevCore/tools/gcil/commit/3cf8ec24ab18b44c1a0a44f0f1f7fa377e4bdf34))
- types: refactor 'Dicts.find' without regex dependency ([deaf512](https://gitlab.com/RadianDevCore/tools/gcil/commit/deaf512c3dd2852d8271f26beb3fa2f77ea296db))
- tests: add 'images' test job for native and container jobs ([c9c03f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/c9c03f0b01225c1d63ad707a4a77707b1a4b7433))


<a name="2.1.1"></a>
## [2.1.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.1.0...2.1.1) (2020-12-05)

### ✨ Features

- prepare #118: restrict Docker sockets mounts to Linux only ([149c484](https://gitlab.com/RadianDevCore/tools/gcil/commit/149c4843d7f8d33f58ca6d58fc4974c0ecb9303c))
- prepare #118: add Platform.IS_MAC_OS platform detection ([a966f7f](https://gitlab.com/RadianDevCore/tools/gcil/commit/a966f7f4bdeb4f515ca2df4794e1f9ef72ae21d1))
- prepare #118: support macOS paths, userspace and real paths ([fdf576d](https://gitlab.com/RadianDevCore/tools/gcil/commit/fdf576d9fe27f654beeab916e46479eca8361e69))
- prepare #122: allow expanding CI_LOCAL in variables values ([491424a](https://gitlab.com/RadianDevCore/tools/gcil/commit/491424af7bd89c12f1ba8b3c3fe8d30c1648de1f))
- resolve #122: add CI_JOB_NAME and CI_PROJECT_DIR definitions ([930a6f4](https://gitlab.com/RadianDevCore/tools/gcil/commit/930a6f4678e16904069b7a811c080f3e4c3c2ffb))
- implement #128: store and read default engines in settings ([2ec1321](https://gitlab.com/RadianDevCore/tools/gcil/commit/2ec132111bd09c4e330771258c88e96409e239bc))

### 🐛 Bug Fixes

- resolve #127: evaluate host project directories correctly ([dff661c](https://gitlab.com/RadianDevCore/tools/gcil/commit/dff661c9baa5916a7db0557fe773223e23faedc7))
- prepare #121: isolate print flushes and allow only on TTY out ([d497a7c](https://gitlab.com/RadianDevCore/tools/gcil/commit/d497a7c719b04b1f7244c93bbecc20afff8f38da))

### 📚 Documentation

- prepare #118: add macOS references in README and TEST ([dfb1858](https://gitlab.com/RadianDevCore/tools/gcil/commit/dfb18583079feceeaad53f448d389fa7e1ac2821))
- changelog: regenerate release tag changes history ([864c7cb](https://gitlab.com/RadianDevCore/tools/gcil/commit/864c7cb334dbfa47629c5afdc7070f8408360827))

### 🧪 Test

- validate #122: create specific test cases for CI projects ([7c9651b](https://gitlab.com/RadianDevCore/tools/gcil/commit/7c9651b863f013eb4a8ab8d86c981ce751efdc91))

### ⚙️ Cleanups

- vscode: configure VSCode telemetry and privacy settings ([636891a](https://gitlab.com/RadianDevCore/tools/gcil/commit/636891a1c1c1904c7804944c8c7ef6e6c4f7a78b))
- vscode: always format files upon editor saves ([9ecf9ea](https://gitlab.com/RadianDevCore/tools/gcil/commit/9ecf9ea9626ce5b79ed87c330a1e07b1b4b22151))
- vscode: add recommended VSCode extensions list ([062a55f](https://gitlab.com/RadianDevCore/tools/gcil/commit/062a55fe15b5d42f03af67510f955d850995cb02))
- vscode: ensure YAML use single quotes formatting ([19bd100](https://gitlab.com/RadianDevCore/tools/gcil/commit/19bd1000004a686de908c0d27acadf1a24e80f48))
- vscode: disable terminal app insights telemetry ([477bf8e](https://gitlab.com/RadianDevCore/tools/gcil/commit/477bf8efe6d74623f730bbfdd9b807d0e87064ce))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.0.1...2.1.0) (2020-12-02)

### ✨ Features

- implement #126: add network mode support in Podman engine ([d7b2b1b](https://gitlab.com/RadianDevCore/tools/gcil/commit/d7b2b1b5fc5ff9d209668c73e601eac9a68203a3))
- implement #125: implement a settings storage class ([8b2e58d](https://gitlab.com/RadianDevCore/tools/gcil/commit/8b2e58d9c8ea63b49cf164320944a6b24eac13c7))
- implement #124: add daily PyPI updates notifications ([fb0a4d8](https://gitlab.com/RadianDevCore/tools/gcil/commit/fb0a4d8894eee0c14c14e718cf23f1d64ecebdcb))

### 📚 Documentation

- changelog: regenerate release tag changes history ([39e3702](https://gitlab.com/RadianDevCore/tools/gcil/commit/39e37028891531f3b6b729049607adad678b4047))

### ⚙️ Cleanups

- gitlab-ci: add '--force-reinstall' to pip reinstallations ([b1c6597](https://gitlab.com/RadianDevCore/tools/gcil/commit/b1c6597de4a276c517ad87631a4b421ba369bfa7))
- gitlab-ci: isolate requirements and use built packages ([94102a0](https://gitlab.com/RadianDevCore/tools/gcil/commit/94102a01ce62f7922a017da2aed0af10cabc62e7))
- gitlab-ci: isolate local jobs under a 'development' stage ([68eb249](https://gitlab.com/RadianDevCore/tools/gcil/commit/68eb2493900f9d87343ff2c649e431b4be340f32))
- gitlab-ci: quiet pip installation logs in 'deploy' jobs ([d6bf1f4](https://gitlab.com/RadianDevCore/tools/gcil/commit/d6bf1f4ce7c04da0ce35393e2fadae3147d97376))
- gitlab-ci: turn the 'Codestyle' job into a CI check job ([c07f3f5](https://gitlab.com/RadianDevCore/tools/gcil/commit/c07f3f5bd103417473d68c18d807abb2ef59bd6b))
- gitlab-ci: disable pip updates warnings in relevant jobs ([65deb91](https://gitlab.com/RadianDevCore/tools/gcil/commit/65deb9116e08049b2d1b17e032c1d80edd55e788))
- gitlab-ci: add local 'Lint' job as a pylint wrapper ([b908139](https://gitlab.com/RadianDevCore/tools/gcil/commit/b908139394c676f313bb280fa303b3285e9f11f4))
- prepare #123: import only required libraries in preview.py ([5d1407e](https://gitlab.com/RadianDevCore/tools/gcil/commit/5d1407eace06565960a1bb0a1daa966124fe0c6d))
- prepare #123: import only required libraries in setup.py ([fec3ef6](https://gitlab.com/RadianDevCore/tools/gcil/commit/fec3ef622db4e3e5f6a7267ba0911b311a36cc44))
- gitlab-ci: isolate pip install steps in 'before_script' ([686cd49](https://gitlab.com/RadianDevCore/tools/gcil/commit/686cd49c9db7c2c35d90f3166f9fa484467d2e4a))
- resolve #123: isolate into classes and lint the sources ([6f10188](https://gitlab.com/RadianDevCore/tools/gcil/commit/6f10188a59c528b72b1d3d82c399476450f7f4b6))


<a name="2.0.1"></a>
## [2.0.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/2.0.0...2.0.1) (2020-11-30)

### ✨ Features

- resolve #113: standardize --tags values as "list,of,values" ([a7b46a8](https://gitlab.com/RadianDevCore/tools/gcil/commit/a7b46a8902976e31d9d73119ba0f54a3657120ce))

### 🐛 Bug Fixes

- resolve #114: show default prioritized engines list in --help ([694362b](https://gitlab.com/RadianDevCore/tools/gcil/commit/694362bc5c82ff999894d3180a136b3dad993253))
- resolve #116: fix native scripts working directory access ([10119f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/10119f3923165d89f6ee0bb27af90dfffd21ff1c))

### 📚 Documentation

- changelog: regenerate release tag changes history ([33e5332](https://gitlab.com/RadianDevCore/tools/gcil/commit/33e533272b67fe6ab822056c92ab8fcc08668a9b))
- test: add tools and engines references for Linux and Windows ([53b29d4](https://gitlab.com/RadianDevCore/tools/gcil/commit/53b29d492d542c9be8e0e4f67f12bb439fc434d5))
- readme: add Windows 10 1909 as being a supported system ([7d52f82](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d52f822e6f6d8c7fc9609237eec1e121d4123cb))
- resolve #120: refactor the supported .gitlab-ci.yml nodes ([240f460](https://gitlab.com/RadianDevCore/tools/gcil/commit/240f460920c059ba177a5b8e829d62d4bf047064))
- resolve #117: add usual examples of parameters ([8d5776f](https://gitlab.com/RadianDevCore/tools/gcil/commit/8d5776f90427829b3596b0fd0f0b727301f8a8fc))
- changelog: regenerate release tag changes history ([a3b9fd3](https://gitlab.com/RadianDevCore/tools/gcil/commit/a3b9fd3cfed0fcc4c80adfa92b10a8822fab8216))

### ⚙️ Cleanups

- resolve #111: cleanup typos and improve --help details ([b169e48](https://gitlab.com/RadianDevCore/tools/gcil/commit/b169e488d684e72e5eba0ff864042e05573f5f54))
- resolve #112: prevent line breaks in the tables ([03567b3](https://gitlab.com/RadianDevCore/tools/gcil/commit/03567b3c0ebcafd16db6d09b8e5fc0bc07b76e13))
- resolve #119: avoid preparing volumes on native jobs ([c6b561d](https://gitlab.com/RadianDevCore/tools/gcil/commit/c6b561d3029ca21580adec5644e3d46c39e9b1d5))
- resolve #112: prevent line break of 'Hyper-V' in engines ([e494967](https://gitlab.com/RadianDevCore/tools/gcil/commit/e4949677b730fa601ec60031fc3bda2848eb418b))
- resolve #111: improve '-p' pipeline documentation details ([8bf8d0a](https://gitlab.com/RadianDevCore/tools/gcil/commit/8bf8d0a57d790bf6d2ff72bcbd9aa451fae6e8ae))
- gitlab-ci: add 'Preview' wrapper job for 'docs/preview.py' ([de3f030](https://gitlab.com/RadianDevCore/tools/gcil/commit/de3f0304dda466ecfe41bcd6bfbae88426d3458c))
- gitlab-ci: use 'Deploy Trial' name to avoid 'Test' issues ([fd2d912](https://gitlab.com/RadianDevCore/tools/gcil/commit/fd2d912bedff3d106fc0a5bb510facc2cccbcbfa))
- readme: minor missing line break in native context jobs ([9d487b8](https://gitlab.com/RadianDevCore/tools/gcil/commit/9d487b813e10af1af7d6482243053b223aa45d1b))
- readme: isolate Linux and Windows tables in chapters ([cecdd7c](https://gitlab.com/RadianDevCore/tools/gcil/commit/cecdd7c3ef7ecd15ed1fa9671e273a71b8d4365a))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.3.1...2.0.0) (2020-11-30)

### ✨ Features

- implement #82: add -H or --host to force host local usage ([92e6fae](https://gitlab.com/RadianDevCore/tools/gcil/commit/92e6fae4148667a474978fa002bba3f0bfe1031c))
- finish #79: add 'Statistics' links for PyPI ([98e6f5c](https://gitlab.com/RadianDevCore/tools/gcil/commit/98e6f5c0199b0964c6c1a4bc9a2b701829191bde))
- implement #80: add Podman root / sudoers engine support ([c11d405](https://gitlab.com/RadianDevCore/tools/gcil/commit/c11d405e395f6b9bc71972488f2d165bddce57c3))
- implement #84: accept -c with folder path to .gitlab-ci.yml ([a4bb5f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/a4bb5f352c71688493723aa3e9b9fc7554e3eb70))
- implement #85: add 'image: local:quiet' for host quiet jobs ([aa7fa22](https://gitlab.com/RadianDevCore/tools/gcil/commit/aa7fa222cf40cd3101314358f3a42622df8c8526))
- implement #87: add support for --version informations ([34e42e7](https://gitlab.com/RadianDevCore/tools/gcil/commit/34e42e780a1fab2fa3e368f19cb997c3929dbd3d))
- implement #88: add 'image: local:silent' as host silent jobs ([9c4edd2](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c4edd2a55803a95115b8428fb8c2ebf6b19b863))
- implement #89: improve pipeline total duration outputs ([555e8e4](https://gitlab.com/RadianDevCore/tools/gcil/commit/555e8e45fa27c908dba51ef3f72b044a3d4b2de3))
- extend #80: add -E engine selection and add CI_LOCAL_ENGINE ([e2e1d7d](https://gitlab.com/RadianDevCore/tools/gcil/commit/e2e1d7dacba26db162b555ed76599ce113ba75b7))
- fix #87: use setuptools API for the --version informations ([dbd8e4f](https://gitlab.com/RadianDevCore/tools/gcil/commit/dbd8e4f5f64ce8997b8b5fda8b9e0072b2888bf1))
- fix #85: resolve puller access to job options 'host' ([1b65826](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b658267c15da28bac3b1087c5ab2f5772ded0bf))
- finish #80: refactor with Podman subprocess CLI calls ([95f48a7](https://gitlab.com/RadianDevCore/tools/gcil/commit/95f48a77eccf179f4dacab9414007be863b98cae))
- implement #92: add '.local:engine' default configurations ([06fcd7c](https://gitlab.com/RadianDevCore/tools/gcil/commit/06fcd7c288e609d7853160ff713337bce67e817e))
- resolve #93: add 'docker,' / 'podman,' for engines priority ([5cec035](https://gitlab.com/RadianDevCore/tools/gcil/commit/5cec035ff07c9216ad64572daa65f42585e55136))
- resolve #99: add support and tests for Python 3.9.0 ([7449e1c](https://gitlab.com/RadianDevCore/tools/gcil/commit/7449e1c652f60c28c90996db1b08f1f5a7778723))
- resolve #100: use /builds paths and add '-r' for real mounts ([4c21ee3](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c21ee381f661394191cad9f822032893c1ab3ce))
- resolve #100: use /builds paths for the temporary script ([6ec0e9c](https://gitlab.com/RadianDevCore/tools/gcil/commit/6ec0e9cf0e68cea780589de50cec61b9bf2a1da9))
- resolve #100: add '.local: real_paths:' configuration ([68bd8ba](https://gitlab.com/RadianDevCore/tools/gcil/commit/68bd8baa58dc1a20e8f9144dc1358c04106420be))
- implement #103: see the used engine in the job header ([2f0d9ed](https://gitlab.com/RadianDevCore/tools/gcil/commit/2f0d9ed75ade17f580a545c2db4b769fe0adec2d))
- implement #101: add '-S' to manually mount engine sockets ([dbb7b25](https://gitlab.com/RadianDevCore/tools/gcil/commit/dbb7b257836fcd0fea81db9f928d300a5ba967ad))
- resolve #34: automate interactive winpty calls on Windows ([1c0e854](https://gitlab.com/RadianDevCore/tools/gcil/commit/1c0e854cedd8fb8ffa9aaed5b03d6f7a5562ff7e))
- resolve #108: define CI_LOCAL_ENGINE if engine option is set ([502a592](https://gitlab.com/RadianDevCore/tools/gcil/commit/502a592808ff292137618bc596bd985757c6d9ce))

### 🐛 Bug Fixes

- resolve #81: avoid invoking Docker APIs if running local jobs ([05f4673](https://gitlab.com/RadianDevCore/tools/gcil/commit/05f467327201638df464c048e683a9f4ef3a9f66))
- tests: resolve entrypoint i686 / x86_64 unreliable results ([a20dcfa](https://gitlab.com/RadianDevCore/tools/gcil/commit/a20dcfa563fc53b9366c5f0bfba48ec760f364a2))
- prepare #80: add missing 'linux-headers' for the Podman test ([d2ff539](https://gitlab.com/RadianDevCore/tools/gcil/commit/d2ff539ab7b42adcf9af92cfc00d059dadc5a8ac))
- implement #83: add support for 'variables:' usage in 'image:' ([99959ba](https://gitlab.com/RadianDevCore/tools/gcil/commit/99959ba2c976c8bf6c4249d8a5a2276af0189fb8))
- gitlab-ci: migrate to Docker-in-Docker (dind) 19.03.13 ([7e4195e](https://gitlab.com/RadianDevCore/tools/gcil/commit/7e4195ef75f6e60aa16dc2aef58506174a180697))
- gitlab-ci: add engines sources to the codestyle input files ([8ab87ec](https://gitlab.com/RadianDevCore/tools/gcil/commit/8ab87ecee7d81277117438b5d465309c12df370b))
- gitlab-ci: remove PATH to avoid issues with Docker-in-Docker ([74d6c3e](https://gitlab.com/RadianDevCore/tools/gcil/commit/74d6c3efa4589b0ccc0b29fcea69f32f6a75e351))
- resolve #90: fix regex searches of names upon --dump ([692433a](https://gitlab.com/RadianDevCore/tools/gcil/commit/692433a73f1df3dcb28fcb5595542bddcb7a0d66))
- resolve #91: fix parser support for empty variables ([bc979ea](https://gitlab.com/RadianDevCore/tools/gcil/commit/bc979ea9285ef6ea6b9539f6d303c4cf1db8aca7))
- test #80: use extends rather than anchos to keeps variables ([c48eb15](https://gitlab.com/RadianDevCore/tools/gcil/commit/c48eb15acd60e8a935f54a5a95bbf2de742e1cc5))
- finish #80: define CI_LOCAL_ENGINE and resolve Podman tests ([58483ad](https://gitlab.com/RadianDevCore/tools/gcil/commit/58483ade563721909f2eeef2c2e2543881647f7c))
- resolve #80: avoid Python 3.7+ specific 'capture_output' ([81a0b7e](https://gitlab.com/RadianDevCore/tools/gcil/commit/81a0b7efbf41a328db62b60816753626de87ded4))
- finish #80: avoid CI_LOCAL_ENGINE / CI_LOCAL_ENGINE_NAME loop ([1b2248f](https://gitlab.com/RadianDevCore/tools/gcil/commit/1b2248f2cfc9bfa2807c00909d1ce1898bd0b7a4))
- finish #80: add '--privileged' flag for Podman containers ([1fd78b6](https://gitlab.com/RadianDevCore/tools/gcil/commit/1fd78b66fe9d714649db57826b28ef21027c19f5))
- finish #80: ensure the entrypoint script is user accessible ([354810d](https://gitlab.com/RadianDevCore/tools/gcil/commit/354810d12c3989d6589f3039def47c5d625cd81a))
- resolve #98: avoid running incomplete jobs in pipelines ([45dff07](https://gitlab.com/RadianDevCore/tools/gcil/commit/45dff0792db35fb19d9b7743d2c482f04ed48925))
- resolve #96: support non-regex names like "C++" in inputs ([907bff9](https://gitlab.com/RadianDevCore/tools/gcil/commit/907bff9a77758f51073cf967124f216a11eb6117))
- resolve #95: avoid opening the NamedTemporaryFile file twice ([df05050](https://gitlab.com/RadianDevCore/tools/gcil/commit/df05050aec37aa46b02603360060dc06983d95a3))
- prepare #34: migrate from os.path to pathlib Path items ([e01cd88](https://gitlab.com/RadianDevCore/tools/gcil/commit/e01cd88073b4146e21e4da790b7b89e5cfdb9ed1))
- prepare #34: use Linux newline endings in entrypoint scripts ([9a78ee5](https://gitlab.com/RadianDevCore/tools/gcil/commit/9a78ee5afc1e59d409fe53f1c1b2f4226f7b0ea6))
- prepare #34: use PurePosixPath for internal container paths ([62d6902](https://gitlab.com/RadianDevCore/tools/gcil/commit/62d69024e711951fdbebaeb3e9524716ae4d897b))
- finish #89: minor comments typo fixes upon time evaluations ([41620ca](https://gitlab.com/RadianDevCore/tools/gcil/commit/41620caeb34461aec63f71f04e2e4c4f714ee6e0))
- prepare #34: remove the temporary script only after execution ([5e5d972](https://gitlab.com/RadianDevCore/tools/gcil/commit/5e5d9725f28d46929ff308833be5448032bc95cb))
- prepare #34: add IS_LINUX and IS_WINDOWS constants ([76e4725](https://gitlab.com/RadianDevCore/tools/gcil/commit/76e472589a600c7ed5551100dc8ff5b70dafe90b))
- prepare #34: exclude /var/run/docker.sock from Windows mounts ([8623b09](https://gitlab.com/RadianDevCore/tools/gcil/commit/8623b09c6132288e9362e7770880901d51718f4e))
- prepare #34: prepare Windows specific changes in resolvePath ([d4c6045](https://gitlab.com/RadianDevCore/tools/gcil/commit/d4c6045b0df66bcf6f4037d27b4bf48b4052bbfe))
- prepare #34: resolve workdir absolute path before using it ([f4f0604](https://gitlab.com/RadianDevCore/tools/gcil/commit/f4f0604bd482a03708a8f7233180147cc328df4a))
- prepare #103: use hidden internal members in Engine classes ([1ccd0e7](https://gitlab.com/RadianDevCore/tools/gcil/commit/1ccd0e7dafa4b22de2eac07e32c5f19e499df537))
- resolve #102: ensure CI_LOCAL_ENGINE_NAME is set for all jobs ([20f658d](https://gitlab.com/RadianDevCore/tools/gcil/commit/20f658d2d890bb901488e56e3d7f1d1d778ee0a7))
- prepare #34: resolve 'local: workdir' absolute path in parser ([d387669](https://gitlab.com/RadianDevCore/tools/gcil/commit/d38766943bdd695b538c39a5fe08ce03b18e9169))
- resolve #104: configure and instantiate the engine only once ([c6aa64e](https://gitlab.com/RadianDevCore/tools/gcil/commit/c6aa64e49f921add9ce18afe9de3a71e0b2ea504))
- test #102: test if CI_LOCAL_ENGINE_NAME is defined twice ([e947678](https://gitlab.com/RadianDevCore/tools/gcil/commit/e947678e92009317d60dd99457f46ffda862cb6b))
- resolve #34: use 'sh' explicitly for local native scripts ([ed560a2](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed560a23c156d8fb3171ac4be7d638767f964b3d))
- resolve #34: bind temp directory to avoid Hyper-V share spams ([dcb5059](https://gitlab.com/RadianDevCore/tools/gcil/commit/dcb5059334e6784eba01b8a8bee3c49874157426))
- resolve #34: avoid using host '/tmp' with container processes ([2eaec6e](https://gitlab.com/RadianDevCore/tools/gcil/commit/2eaec6e82c58af144879b7725d134951da7e0883))
- gitlab-ci: resolve "${PWD}" real path upon environment tests ([94bd5b2](https://gitlab.com/RadianDevCore/tools/gcil/commit/94bd5b28c479c4a5a07d2538ddd67391dd2a6b03))
- gitlab-ci: refactor, nested containers and Podman 3.6 to 3.9 ([420edd4](https://gitlab.com/RadianDevCore/tools/gcil/commit/420edd4eb796d1514b10093d801c43b6a35c99c8))
- gitlab-ci: use real paths and bind sockets for development ([5a94667](https://gitlab.com/RadianDevCore/tools/gcil/commit/5a9466734f9f99ef19b018f5c0067c296d94ae53))
- resolve #34: use isolated temporary directory to avoid issues ([581e886](https://gitlab.com/RadianDevCore/tools/gcil/commit/581e886951a6eb3cac80f4d0bb8883f5d5a520bc))
- resolve #34: use only /builds folder for entrypoint scripts ([017282d](https://gitlab.com/RadianDevCore/tools/gcil/commit/017282d5a58b7ad2ba0721fdfb0f084ef6eda12c))
- resolve #105: support mounting a path twice without overlaps ([4f4e0fe](https://gitlab.com/RadianDevCore/tools/gcil/commit/4f4e0fee1b20587d598c5155c1e37bfbde0838b1))
- resolve #34: support local script paths with spaces ([1bd638a](https://gitlab.com/RadianDevCore/tools/gcil/commit/1bd638a4bf16006e98d93cd37fdcff0865dd12c0))
- resolve #106: resolve relative paths against configuration ([9f3dbcd](https://gitlab.com/RadianDevCore/tools/gcil/commit/9f3dbcdd3d14d402045b911b334ca22bb3dec2ad))
- resolve #105: handle volumes duplicates and local overrides ([1027e6d](https://gitlab.com/RadianDevCore/tools/gcil/commit/1027e6dfc50908db78d4047886f83a493814e96f))
- resolve #106: resolve relative workdir paths against options ([8e8e1bb](https://gitlab.com/RadianDevCore/tools/gcil/commit/8e8e1bbdb599eb41986941e5e37dd08b08213811))
- resolve #109: disallow real paths usage on Windows ([cbd9a58](https://gitlab.com/RadianDevCore/tools/gcil/commit/cbd9a58527231b29b7537d6a911d44791e75df75))
- resolve #106: use required pure POSIX paths for workdir paths ([a380727](https://gitlab.com/RadianDevCore/tools/gcil/commit/a3807279524c8d80f8104a8c72cb60e07b0c35c5))
- resolve #107: support working directory in local native jobs ([38509bd](https://gitlab.com/RadianDevCore/tools/gcil/commit/38509bdd7c4a7e13d15b75a07f62e852252c32af))
- resolve #105: handle duplicated source paths on Windows too ([5f9c1f9](https://gitlab.com/RadianDevCore/tools/gcil/commit/5f9c1f99d5feecd7b171d8517de48b3a03af0a25))
- resolve #110: fix non-interactive menus and engine on Windows ([3381bda](https://gitlab.com/RadianDevCore/tools/gcil/commit/3381bda164d8c2c7a69f1c6edbb44324d21fd167))
- gitlab-ci: resolve "${PWD}" path usage with spaces in tests ([44282d2](https://gitlab.com/RadianDevCore/tools/gcil/commit/44282d2427e85ee5fe688720c96744f5411c176d))

### 🚜 Code Refactoring

- prepare #80: isolate Docker engine specific APIs ([5772112](https://gitlab.com/RadianDevCore/tools/gcil/commit/5772112d91eb69e5e26ac7ec1277c5acd492f65b))
- prepare #80: isolate the Docker engine as an abstract ([4a0c8c6](https://gitlab.com/RadianDevCore/tools/gcil/commit/4a0c8c6075ba22ff0f91db94fbb178c8397e032a))

### 📚 Documentation

- document #34: add supported systems and engines in README ([6edb4f7](https://gitlab.com/RadianDevCore/tools/gcil/commit/6edb4f7b5e95dfe55cdaa5512e7544dea684acac))
- readme: refresh 'gitlabci-local' usage and parameters lists ([db781fd](https://gitlab.com/RadianDevCore/tools/gcil/commit/db781fd4a678989850166c94253a3e3d35eed60b))
- readme: improve readability of supported engines and systems ([a39e129](https://gitlab.com/RadianDevCore/tools/gcil/commit/a39e1296dc1c44f8b66bbafc9b0a92daf185b49d))
- gitlab-ci: use 'docs: changelog:' for changelog commits ([abb7fc9](https://gitlab.com/RadianDevCore/tools/gcil/commit/abb7fc938cbede68456d6302151a5d4decf01f64))
- readme: center operating systems and engines names tables ([e2a5695](https://gitlab.com/RadianDevCore/tools/gcil/commit/e2a56951ee32d367e570bb4998a9946892dff22a))
- changelog: regenerate release tag changes history ([3c17ccf](https://gitlab.com/RadianDevCore/tools/gcil/commit/3c17ccfc9231fa6ca5fefc340785744dd25de458))

### 🧪 Test

- prepare #80: add Podman specific test job for reference ([7d18258](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d182581a45365f726a23a39722d3ad3ccc671f7))
- prepare #105: specific tests for local and CLI volumes ([42143f0](https://gitlab.com/RadianDevCore/tools/gcil/commit/42143f0d95232cd01d110070b6a6186b97556236))

### ⚙️ Cleanups

- prepare #82: ensure Python 3 is explicitly used in 'Build' ([6e8a28a](https://gitlab.com/RadianDevCore/tools/gcil/commit/6e8a28a084a13f926263286464936f6a2499c8a8))
- prepare #80: reduce Docker specific references and add OCI ([f5f0151](https://gitlab.com/RadianDevCore/tools/gcil/commit/f5f015109ff68d1b8e704a4fb75f5b3fa7fb0a44))
- dev: add missing setuptools-scm development requirement ([e97f1cc](https://gitlab.com/RadianDevCore/tools/gcil/commit/e97f1cc9bbf3eed93081cc640d675f44c8b31681))
- prepare #82: ensure Python 3 is explicitly used in 'Deploy' ([f8adb44](https://gitlab.com/RadianDevCore/tools/gcil/commit/f8adb44ff9edd147541cff3d4f6c7f4c8a1114ec))
- gitlab-ci: ensure /usr/local/path is in PATH for all tests ([070920e](https://gitlab.com/RadianDevCore/tools/gcil/commit/070920e06bcaf70671c442b79b7d1e45fa64c70a))
- development: install as 'sudoer' when using 'Development' ([751c1c4](https://gitlab.com/RadianDevCore/tools/gcil/commit/751c1c431556ce32999dd01acec0c5e0948f8994))
- resolve #86: hide irrelevant internal values from --dump ([10d415f](https://gitlab.com/RadianDevCore/tools/gcil/commit/10d415fa34f3bc820c00e9686a8659f53ffb7610))
- gitlab-ci: add 'Test' local job to run unit tests suites ([d0498d5](https://gitlab.com/RadianDevCore/tools/gcil/commit/d0498d5c4dd479aa8ada77f8defa17c440e135bd))
- gitlab-ci: add 'git --name-status' after 'Codestyle' fixes ([6da6f7e](https://gitlab.com/RadianDevCore/tools/gcil/commit/6da6f7e2420fa35f3663283dbb48035b84c7dba9))
- gitlab-ci: add command headers for the 'Test' local job ([41ea228](https://gitlab.com/RadianDevCore/tools/gcil/commit/41ea2280133aaa964ce02bc9972bc7a00316cd2c))
- gitlab-ci: install production requirements then development ([9c9faba](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c9fabaadf1f545666dce6d39536e68997041060))
- main: use a global variable for '.gitlab-ci.yml' file name ([9311b3a](https://gitlab.com/RadianDevCore/tools/gcil/commit/9311b3a0d875000057eeafe99a7f1cfbc5a62b1a))
- prepare #34: isolate /builds and /tmp paths in const class ([c50538e](https://gitlab.com/RadianDevCore/tools/gcil/commit/c50538ee0b71abfd70274764b657e4d9661dc525))
- gitlab-ci: resolve colored terminal outputs in 'Test' ([f712373](https://gitlab.com/RadianDevCore/tools/gcil/commit/f712373bf657ef625ea170a76f22550f1e78790a))
- gitlab-ci: avoid reinstalling upon local native tests ([cc91b6c](https://gitlab.com/RadianDevCore/tools/gcil/commit/cc91b6c6bfc2e3fecfef4008bd275e22826b4ff0))
- run: add 'run.sh' script for local development purposes ([ac92059](https://gitlab.com/RadianDevCore/tools/gcil/commit/ac92059ebfc56ce70caa924a7f91a487a463a1c7))
- gitlab-ci: use the Docker engine by default for development ([5bda88e](https://gitlab.com/RadianDevCore/tools/gcil/commit/5bda88e5d9fedabedf8fc11c5acda2cf7ba82f44))
- gitlab-ci: add 'pwd' and 'mount' to all tests jobs ([4c590b7](https://gitlab.com/RadianDevCore/tools/gcil/commit/4c590b715236294b90215e432e6c25124d84f79c))
- gitignore: exclude all .tmp.* entrypoint intermediate files ([46fa725](https://gitlab.com/RadianDevCore/tools/gcil/commit/46fa725e5fc3ca8c2aa381cb481f693dba988986))
- docs: drop 'gitlabci-local --help' command in the preview ([c2ae3a9](https://gitlab.com/RadianDevCore/tools/gcil/commit/c2ae3a90b84bec437e1f9bd416ee0ecbecd14f6c))
- docs: use Docker engine by default and minor cleanups ([b04743f](https://gitlab.com/RadianDevCore/tools/gcil/commit/b04743f7c4fc606ca16937fff468fa4476fbaa0f))
- docs: refresh the preview GIF for the latest 2.0.0 release ([3ecde51](https://gitlab.com/RadianDevCore/tools/gcil/commit/3ecde51a0735dce0513b5effbb5461aa56940e6c))
- gitlab-ci: add Test PyPI uploader local manual job ([fccffed](https://gitlab.com/RadianDevCore/tools/gcil/commit/fccffed46791c9ff57d7adf1a287d87887b5392c))

### Parser

- resolve #94: ignore and consider trigger jobs as disabled ([1056603](https://gitlab.com/RadianDevCore/tools/gcil/commit/105660368c7d63b2558a20d2df4c7e2f8a21fe0f))


<a name="1.3.1"></a>
## [1.3.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.3.0...1.3.1) (2020-10-23)

### ✨ Features

- implement #78: add total pipeline time in results ([2d88325](https://gitlab.com/RadianDevCore/tools/gcil/commit/2d88325a6480c9f0624a42c699e8fd2f8df7ea42))
- resolve #79: add 'Bug Reports' and 'Source' links for PyPI ([0b4faf3](https://gitlab.com/RadianDevCore/tools/gcil/commit/0b4faf33db9375cbd9011c376d528ebe5793050b))

### CHANGELOG

- regenerate release tag changes history ([7940bad](https://gitlab.com/RadianDevCore/tools/gcil/commit/7940badcd53803b50a5f63f09ca2ce5e1fb96397))


<a name="1.3.0"></a>
## [1.3.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.2.1...1.3.0) (2020-10-21)

### ✨ Features

- resolve #74: disable incomplete jobs instead of failing ([4013a19](https://gitlab.com/RadianDevCore/tools/gcil/commit/4013a19c9c918470ca1b4988181e19af32868318))

### 🐛 Bug Fixes

- resolve #77: resolve standalone multiline scripts parser ([f694949](https://gitlab.com/RadianDevCore/tools/gcil/commit/f6949497031b68113dafc2a07afb1ba7c16c3100))

### 🧪 Test

- validate #77: check standalone multiline scripts parser ([b030f6e](https://gitlab.com/RadianDevCore/tools/gcil/commit/b030f6eb13dff5c3432c049ac73e2c72f590cc04))

### ⚙️ Cleanups

- requirements: bind setuptools for delivery rather than dev ([a682b49](https://gitlab.com/RadianDevCore/tools/gcil/commit/a682b4984d976ad2e77ebe0c7ed65af18732b55f))
- setup: add support for comments in requirements.txt ([95dc6fa](https://gitlab.com/RadianDevCore/tools/gcil/commit/95dc6fa7d73a8dbba3e60d1c42c4965cd3a4804c))

### CHANGELOG

- regenerate release tag changes history ([d48e357](https://gitlab.com/RadianDevCore/tools/gcil/commit/d48e35778b0d8225ac81568d2605b8b5a2085e06))


<a name="1.2.1"></a>
## [1.2.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.2.0...1.2.1) (2020-08-04)

### ✨ Features

- implement #67: define CI_LOCAL variable to detect local jobs ([a485177](https://gitlab.com/RadianDevCore/tools/gcil/commit/a485177d91baac19e8789f7f394fccf594fa4ed6))
- implement #71: add a shorter "gcil" entrypoint wrapper ([a648241](https://gitlab.com/RadianDevCore/tools/gcil/commit/a64824197c1bbda93ba7c4fcaab9ac9d1ab9b6cd))
- document #71: add 'gcil' alias references in help and README ([072510c](https://gitlab.com/RadianDevCore/tools/gcil/commit/072510c59cdc37eeaec0d169dcf765d8d3ae44eb))
- resolve #72: add support for the --help parameter along -h ([4ae8838](https://gitlab.com/RadianDevCore/tools/gcil/commit/4ae88389896f8912f53493eceb8b013b9fcd8028))
- implement #73: add support for regex searches of names ([525e35d](https://gitlab.com/RadianDevCore/tools/gcil/commit/525e35d50ad9c908be92326637e4af7ed163d100))

### 🐛 Bug Fixes

- resolve #68: add empty footer lines upon error failures ([48b4a20](https://gitlab.com/RadianDevCore/tools/gcil/commit/48b4a20b781890ae21d152abd09aa867115312f1))
- resolve #69: propagate and cumulate extended jobs' variables ([f89af09](https://gitlab.com/RadianDevCore/tools/gcil/commit/f89af09ba67191a26ce4bcf9ce9df93b2e838aee))
- resolve #70: support disabling *script: nodes with extends: ([4de0e6e](https://gitlab.com/RadianDevCore/tools/gcil/commit/4de0e6e4bc547fe24c6eb6104985ffa9457d84be))

### 🧪 Test

- validate #71: check 'gcil' works on the 'simple' tests ([44d52e9](https://gitlab.com/RadianDevCore/tools/gcil/commit/44d52e9d77cda787c151b583d12ce604da2bb933))

### ⚙️ Cleanups

- gitlab-ci: remove unnecessary 'tags: local' for local jobs ([6a769c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/6a769c29b264872f755c40ec71c9c5f916288dfd))

### CHANGELOG

- regenerate release tag changes history ([38ea476](https://gitlab.com/RadianDevCore/tools/gcil/commit/38ea476abc568f703d22633817429546ffd3e228))


<a name="1.2.0"></a>
## [1.2.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.6...1.2.0) (2020-06-13)

### ✨ Features

- implement #66: add support for 'extends' jobs in parser ([7dd9acc](https://gitlab.com/RadianDevCore/tools/gcil/commit/7dd9accd7649300652c962bc839ad98f0abdf88d))

### 🐛 Bug Fixes

- prepare #66: ensure missing 'image' key is properly detected ([6a84f4b](https://gitlab.com/RadianDevCore/tools/gcil/commit/6a84f4bc120f01de4f829910673a079bb296bbea))
- prepare #66: ensure missing 'script' required node detection ([0c472ff](https://gitlab.com/RadianDevCore/tools/gcil/commit/0c472ff1b4cd2d54963a9629696931882aaec7f7))
- prepare #66: ensure global keys will not be parsed as jobs ([0a5f332](https://gitlab.com/RadianDevCore/tools/gcil/commit/0a5f332a55e01292dbf378b8f496c01b6cb61b1f))
- prepare #66: respect included data order in 'include' nodes ([ed2a209](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed2a2093cc72890c31b1856b3983ad8c7ee3bcaa))

### 🧪 Test

- validate #66: ensure 'extends' full support is validated ([3f4300c](https://gitlab.com/RadianDevCore/tools/gcil/commit/3f4300c3dfe285773551362e905481925c4c7381))

### CHANGELOG

- regenerate release tag changes history ([97f418f](https://gitlab.com/RadianDevCore/tools/gcil/commit/97f418f3168dca73c0b0e2dfd20e826fa6f6721b))


<a name="1.1.6"></a>
## [1.1.6](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.5...1.1.6) (2020-04-02)

### ✨ Features

- implement #63: add execution timings for every job ([21ed3ed](https://gitlab.com/RadianDevCore/tools/gcil/commit/21ed3ed7774c18ee081c7758634fb27497a3889c))
- implement #62: add support for 'allow_failure: true' options ([53d5cc4](https://gitlab.com/RadianDevCore/tools/gcil/commit/53d5cc41e5e9a943505f1595a5aca7bc3d8252e7))

### 🐛 Bug Fixes

- resolve #65: synchronize stdout and stderr runner outputs ([8451118](https://gitlab.com/RadianDevCore/tools/gcil/commit/84511188ed6540d73aec9f9177d710b88814064d))

### ⚙️ Cleanups

- validate #64: ensure first failure drops the script ([3f935d4](https://gitlab.com/RadianDevCore/tools/gcil/commit/3f935d441469795c55b06bacdc2c298c8e31e0d5))

### CHANGELOG

- regenerate release tag changes history ([428b6e6](https://gitlab.com/RadianDevCore/tools/gcil/commit/428b6e6ca50ac455fed45f7b3d68d24492072d9a))


<a name="1.1.5"></a>
## [1.1.5](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.4...1.1.5) (2020-03-15)

### 🐛 Bug Fixes

- resolve UTF-8 stdout outputs from container logs stream ([e2a1e74](https://gitlab.com/RadianDevCore/tools/gcil/commit/e2a1e742ba4b509e163daf6bb0c3ce5bd4b314c3))

### ⚙️ Cleanups

- deprecate 'Deploy Test' and enforce automatic tags release ([5987e1c](https://gitlab.com/RadianDevCore/tools/gcil/commit/5987e1c6da360507efaaf3ef4d0f18ebcd9e4fc1))

### CHANGELOG

- regenerate release tag changes history ([4b8d1c9](https://gitlab.com/RadianDevCore/tools/gcil/commit/4b8d1c925d32644535511e68f13316feccc09fb8))


<a name="1.1.4"></a>
## [1.1.4](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.3...1.1.4) (2020-03-15)

### 🐛 Bug Fixes

- fix #61: handle before_script and script together like CI ([91d7269](https://gitlab.com/RadianDevCore/tools/gcil/commit/91d7269c4eb2a90a5727fe0229d651d8d5d3d2da))

### CHANGELOG

- regenerate release tag changes history ([1e8b0f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/1e8b0f35fa8d916f9a032bc202c9d218886fe9f7))


<a name="1.1.3"></a>
## [1.1.3](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.2...1.1.3) (2020-03-09)

### ✨ Features

- implement #60: adapt debug command if bash exists ([5ecc628](https://gitlab.com/RadianDevCore/tools/gcil/commit/5ecc628de7b51780488923d9d6b7b2f5a3c7c011))
- implement #59: add support for bash in debug mode ([f864614](https://gitlab.com/RadianDevCore/tools/gcil/commit/f864614e1c4520e20e3f422406346726b4849497))

### 🐛 Bug Fixes

- resolve Python codestyle with YAPF in parser and runner ([45e896c](https://gitlab.com/RadianDevCore/tools/gcil/commit/45e896c6bd30f5eb855bedb6dd3a13b9e98f22dc))
- implement #61: handle before_script and after_script like CI ([e0c16a9](https://gitlab.com/RadianDevCore/tools/gcil/commit/e0c16a9bff91c432b7a9f4958a5bb5b17a0e457f))

### ⚙️ Cleanups

- add 'Dependencies' development requirements local job ([9e30e3f](https://gitlab.com/RadianDevCore/tools/gcil/commit/9e30e3f318996c0d1f33f2da7a6d261d1dd5590c))

### CHANGELOG

- regenerate release tag changes history ([0dacf9d](https://gitlab.com/RadianDevCore/tools/gcil/commit/0dacf9d38e06f572b1c58fb62f39236571f17c9f))


<a name="1.1.2"></a>
## [1.1.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.1...1.1.2) (2020-03-07)

### 🐛 Bug Fixes

- finish #57: ensure --debug works upon runner failures too ([bd4803b](https://gitlab.com/RadianDevCore/tools/gcil/commit/bd4803b07eb8094e0bc4718aca5ef1733e275438))
- tests: minor local test output syntax cleanup ([622e781](https://gitlab.com/RadianDevCore/tools/gcil/commit/622e781c5e12e78411eb967f88cbd3eb8f2559bd))

### CHANGELOG

- regenerate release tag changes history ([f280f96](https://gitlab.com/RadianDevCore/tools/gcil/commit/f280f9621b1e547b2916cca73a571cbbfa4c97c2))


<a name="1.1.1"></a>
## [1.1.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.1.0...1.1.1) (2020-03-03)

### ✨ Features

- implement #58: handle SIGTERM as an interruption ([7ed9e3f](https://gitlab.com/RadianDevCore/tools/gcil/commit/7ed9e3fff97da6b5f2c233aaf49c13aa8e011124))
- implement #57: add --debug support to keep runner execution ([73a2bca](https://gitlab.com/RadianDevCore/tools/gcil/commit/73a2bca7446703e41962a0987a2f8122f70e662b))

### CHANGELOG

- regenerate release tag changes history ([07cbe0b](https://gitlab.com/RadianDevCore/tools/gcil/commit/07cbe0baff55ad97695ad0c348f27777e3078ab2))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.5...1.1.0) (2020-02-23)

### ✨ Features

- implement #46: implement most parameters in .local nodes ([3a7fcb7](https://gitlab.com/RadianDevCore/tools/gcil/commit/3a7fcb7e025c12f2d85cbfa417c9b33bcb1df287))
- implement #48: add support for a network mode configuration ([554de0c](https://gitlab.com/RadianDevCore/tools/gcil/commit/554de0cf5120dea8044213d284e662f069bf2e19))
- resolve #52: expand volume paths containing variables ([c3e582f](https://gitlab.com/RadianDevCore/tools/gcil/commit/c3e582fc8564a90d98ad6440059b721c2ab8fbcf))
- implement #50: always enable before/after_script by default ([dd1cd7b](https://gitlab.com/RadianDevCore/tools/gcil/commit/dd1cd7b55158f772f4f5c91f335e21cb16dc627a))
- resolve #47: add support for env parsing in .local node ([eb5aeb2](https://gitlab.com/RadianDevCore/tools/gcil/commit/eb5aeb2868c05efd63924c353dfde2f741b23b72))
- implement #54: initial support for include:local nodes ([1929b8b](https://gitlab.com/RadianDevCore/tools/gcil/commit/1929b8b2635c4db7e424180f283c6476676289af))
- study #55: add 'Unit Tests (PyPI)' manual customized job ([cad9a90](https://gitlab.com/RadianDevCore/tools/gcil/commit/cad9a90adb63d4b943630e6ec92cdd37ad38e4e4))
- add support for 'when:' result details for clarity ([eb267a0](https://gitlab.com/RadianDevCore/tools/gcil/commit/eb267a0a75a340530bff3dcb96da6eeace741fae))
- add support for 'names' in .local node configurations ([484324a](https://gitlab.com/RadianDevCore/tools/gcil/commit/484324ab0da89fd7ac77d0c298853962dbe494cd))

### 🐛 Bug Fixes

- resolve #49: preserve environment variables when set in .env ([30e9833](https://gitlab.com/RadianDevCore/tools/gcil/commit/30e9833a869c0e861b95033081879742a13a81b5))
- resolve #51: handle global variables as default values only ([99105c3](https://gitlab.com/RadianDevCore/tools/gcil/commit/99105c348cb77fe649f2b16c713bdf65bbbac04d))
- resolve #53: parse complete context before parsing stages ([9360262](https://gitlab.com/RadianDevCore/tools/gcil/commit/93602623f5cb307242eda6d4169620f088eb9348))
- resolve #55: use stable docker:19.03.5-dind image service ([807ca30](https://gitlab.com/RadianDevCore/tools/gcil/commit/807ca30a2b9d0fa086dedadec255b1f6f0ff0706))

### 📚 Documentation

- regenerate preview GIF with latest changes for 'failures' ([1ff53b3](https://gitlab.com/RadianDevCore/tools/gcil/commit/1ff53b3ed6478f783414878d0ee66c361e151779))

### ⚙️ Cleanups

- resolve colored codestyle with YAPF ([56881f3](https://gitlab.com/RadianDevCore/tools/gcil/commit/56881f34c5a268d9b32e63258efcb6ee316de606))
- ensure Unit Tests jobs timeout after 10 minutes ([f300a4e](https://gitlab.com/RadianDevCore/tools/gcil/commit/f300a4ec7b755ce5e0005f8b75f5bd068df33012))
- remove unused configurations variable in parser.py ([ea36eba](https://gitlab.com/RadianDevCore/tools/gcil/commit/ea36ebaad4c154dc38f00779520c952135271ccc))
- refresh preview GIF for latest features and parameters ([f423376](https://gitlab.com/RadianDevCore/tools/gcil/commit/f423376d0e39e34bdbd36a78ca85e5a09b861716))
- finish #47: add '.local:env' mention in README.md ([46d2de3](https://gitlab.com/RadianDevCore/tools/gcil/commit/46d2de3b5897bfc3415fdb69656971708218fa3e))
- resolve #56: document all supported .gitlab-ci.yml features ([40fc98e](https://gitlab.com/RadianDevCore/tools/gcil/commit/40fc98e640683e79db3098929ef53f482306b9e7))
- finish #54: add missing tests/includes unit tests call ([8c520e0](https://gitlab.com/RadianDevCore/tools/gcil/commit/8c520e0fd7d69e07253e987c7c3a86b11d8165f8))
- fix the README and helper tool name to 'gitlabci-local' ([c7d68b3](https://gitlab.com/RadianDevCore/tools/gcil/commit/c7d68b388ba0bc6416e30dad6fcede51ad31c37f))
- refresh the README usage helper parameters list ([fd0aeb7](https://gitlab.com/RadianDevCore/tools/gcil/commit/fd0aeb7c0ec19653f12532d2c9d44d6cedf49265))
- finish #56: cleanup supported .gitlab-ci.yml features ([faa2905](https://gitlab.com/RadianDevCore/tools/gcil/commit/faa2905f4e5968387b2db8dbc0ca135355ab8a82))
- regenerate preview GIF documentation ([f96bf4b](https://gitlab.com/RadianDevCore/tools/gcil/commit/f96bf4b495a4b599ee0659629b0e1397c5291bb4))
- finish #48: add missing '.local:network' mention in README ([082b503](https://gitlab.com/RadianDevCore/tools/gcil/commit/082b5030dd2e41fc0385bd3da61120fcb960a63f))

### CHANGELOG

- regenerate release tag changes history ([25ecf31](https://gitlab.com/RadianDevCore/tools/gcil/commit/25ecf31d5085e294b0a1ea915ba42b3fe3d98fe2))
- regenerate release tag changes history ([cdfb52c](https://gitlab.com/RadianDevCore/tools/gcil/commit/cdfb52cdcdd64640cf7524e9c67abb1a706c4a6c))


<a name="1.0.5"></a>
## [1.0.5](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.4...1.0.5) (2020-01-27)

### ✨ Features

- implement #40: migrate to .local unified configurations node ([bed8bd4](https://gitlab.com/RadianDevCore/tools/gcil/commit/bed8bd49d00923d0b1a6ed8b064c17baa0499fae))
- implement #42: disable configurations with --defaults ([6bd7fb4](https://gitlab.com/RadianDevCore/tools/gcil/commit/6bd7fb403cbceeb2e5c187be35c193b0678b97f2))
- prepare #41: add support for :ro and :rw volume mounts flags ([47c9583](https://gitlab.com/RadianDevCore/tools/gcil/commit/47c9583868ecb2bc54e4ad4246c651cf6eecbc65))
- prepare #41: support overriding a bound volume with another ([9623386](https://gitlab.com/RadianDevCore/tools/gcil/commit/9623386526f252520b1d7a94506c39cb9f122463))
- implement #41: add support for local volumes definitions ([cf78e9f](https://gitlab.com/RadianDevCore/tools/gcil/commit/cf78e9f5ca424dad495ab653e67b01166782419c))
- implement #43: allow enabling all jobs with --all ([b7d05a8](https://gitlab.com/RadianDevCore/tools/gcil/commit/b7d05a8985cb377933e0286ea5881fa9dbbc0c09))

### 🐛 Bug Fixes

- prepare #34: migrate from Blessings to Colored library ([584c8f6](https://gitlab.com/RadianDevCore/tools/gcil/commit/584c8f637f33f3f627228aab6ba42cf7d48faad9))

### ⚙️ Cleanups

- gitlab-ci: isolate local preparation jobs to prepare stage ([b797a9e](https://gitlab.com/RadianDevCore/tools/gcil/commit/b797a9eba2a4789fcd27cbdaa89d52652063cd03))
- tests: add --pull feature validation upon entrypoints test ([07ba5b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/07ba5b0a882332e82b4810ba4e6c18c0777c6c88))
- docs: refactor preview.sh Executor class with constants ([2a3783d](https://gitlab.com/RadianDevCore/tools/gcil/commit/2a3783d1f9ba02d4f61f83327b6de985b95a0596))
- requirements: rename _dev.txt to requirements-dev.txt ([f126c3d](https://gitlab.com/RadianDevCore/tools/gcil/commit/f126c3d630e25450e703b7cd87e48ee2f6f65191))
- prepare #44: add Python 3.6, 3.7, 3.8 and local tests ([a5d9e19](https://gitlab.com/RadianDevCore/tools/gcil/commit/a5d9e199b1425ebc8c2207ae147bb7bd10304936))
- setup: add 'Documentation' reference to README.md ([2f66deb](https://gitlab.com/RadianDevCore/tools/gcil/commit/2f66deba8edd438709c0b14bd807c3926fd61148))
- resolve #44: restrict Python to versions 3.6, 3.7 and 3.8 ([801ef3d](https://gitlab.com/RadianDevCore/tools/gcil/commit/801ef3de43e4a3692459c8b8d1a7bef872b83b6d))
- prepare #34: add 'winpty' references for Windows in README ([edb6f78](https://gitlab.com/RadianDevCore/tools/gcil/commit/edb6f788d3f660f8b8db04c88bcde19430470628))
- changelog: add current commit hint with git describe ([31340b0](https://gitlab.com/RadianDevCore/tools/gcil/commit/31340b06cfdebcbac62232e9b30f80390749ba61))

### CHANGELOG

- regenerate release tag changes history ([b9522b5](https://gitlab.com/RadianDevCore/tools/gcil/commit/b9522b57b2c8177f2069ceed73f78ec5891c1847))


<a name="1.0.4"></a>
## [1.0.4](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.3...1.0.4) (2020-01-26)

### ✨ Features

- implement #32: add --pull mode for Docker images ([d7a60dd](https://gitlab.com/RadianDevCore/tools/gcil/commit/d7a60dde96cd0f1bb9f7192376f4034e6f33418c))
- implement #37: use low-level Docker pull with streamed logs ([6f13d7f](https://gitlab.com/RadianDevCore/tools/gcil/commit/6f13d7fa3adbec9af6290d44d7ac7595e96a052f))
- implement #38: pull Docker images if missing upon execution ([57dabdf](https://gitlab.com/RadianDevCore/tools/gcil/commit/57dabdf4191ed6c8339da13625bc0b1a9d34cd52))
- implement #3: support job retry values upon executions ([0444993](https://gitlab.com/RadianDevCore/tools/gcil/commit/0444993ca2b3849df0337ff32b0d712aa887e941))

### 🐛 Bug Fixes

- resolve #13: fix rare container wait random failures ([bc09017](https://gitlab.com/RadianDevCore/tools/gcil/commit/bc09017bcdc412d5162d461aab9028cb0ada454b))
- resolve #33 support integer variables definitiionz type ([35307fa](https://gitlab.com/RadianDevCore/tools/gcil/commit/35307fa5a110f9755fc20bf41e51405365a423b8))
- resolve #36: preserve original image and CI YAML entrypoints ([db9e657](https://gitlab.com/RadianDevCore/tools/gcil/commit/db9e657b7dcb7e95d413a8c258a6b09985f21ae2))
- resolve #31: hardcode the README GIF preview with tags ([b0f89c2](https://gitlab.com/RadianDevCore/tools/gcil/commit/b0f89c2a51899e87ff7eded9fa4be8f2f596c066))
- resolve #36: support overriding image entrypoint with none ([8359f51](https://gitlab.com/RadianDevCore/tools/gcil/commit/8359f514cca5658da884a0385c38fb24a9307a46))
- resolve #39: resolve Docker Python random exceptions ([643ec92](https://gitlab.com/RadianDevCore/tools/gcil/commit/643ec92e9355251cab533cee924d9c6a09a7c41d))
- resolve #4: fix list view separator in PyInquirer ([228cf9e](https://gitlab.com/RadianDevCore/tools/gcil/commit/228cf9ec3c1474bf78b026c6b8d7b5ec300f416f))

### ⚙️ Cleanups

- development: only rebuild in the Development local stage ([dcdb6c9](https://gitlab.com/RadianDevCore/tools/gcil/commit/dcdb6c93772a22593954f7ab97f77c1d6fe21814))
- requirements: unify and add missing developement items ([5f646fc](https://gitlab.com/RadianDevCore/tools/gcil/commit/5f646fc2df0af31eed646df9bd05e1cbfb0cf63e))
- requirements: add YAPF as a development requirement ([e96150d](https://gitlab.com/RadianDevCore/tools/gcil/commit/e96150d5ed37a93f471708d9f06bbfb4451378e8))
- codestyle: add an automated YAPF local job wrapper ([cad770c](https://gitlab.com/RadianDevCore/tools/gcil/commit/cad770cd7d416f3c9554d598b2846da31ca3b152))
- codestyle: pass all Python sources through YAPF ([067cb48](https://gitlab.com/RadianDevCore/tools/gcil/commit/067cb48868cdc117a46a2035962d62f6a56ff93c))
- codestyle: pass all Python files through unify with "'" ([9c0690f](https://gitlab.com/RadianDevCore/tools/gcil/commit/9c0690fab10713746bda08f4f2e58954174e79af))

### CHANGELOG

- regenerate release tag changes history ([137df4e](https://gitlab.com/RadianDevCore/tools/gcil/commit/137df4ea9303b9f2079aeb409301c9362660ccf6))

### README

- add pexpect references for docs/ automated preview script ([11f639d](https://gitlab.com/RadianDevCore/tools/gcil/commit/11f639d57667fb988f32f1004094cbbba4696d3d))
- resolve Changelog job reference for 'image: local' ([f07a810](https://gitlab.com/RadianDevCore/tools/gcil/commit/f07a810209ce045296b06684d703263547b58cf8))


<a name="1.0.3"></a>
## [1.0.3](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.2...1.0.3) (2020-01-23)

### ✨ Features

- implement #18: extend user configurations support for types ([11cbb2b](https://gitlab.com/RadianDevCore/tools/gcil/commit/11cbb2b705fcc38046863f2bc3d410ac5979cb1d))
- implement #16: configure with environment variables if set ([0c4af24](https://gitlab.com/RadianDevCore/tools/gcil/commit/0c4af2449040416ebb99c6e1b60cf4238459eda8))
- implement #19: add support for YAML and JSON configurations ([ed66b1e](https://gitlab.com/RadianDevCore/tools/gcil/commit/ed66b1ee231454083d0d75325687e3ef6c83da71))
- implement #23: add support for native local jobs execution ([d6819e2](https://gitlab.com/RadianDevCore/tools/gcil/commit/d6819e2c6c469278efe1ec2d4cd0e0626b0b5627))
- resolve #25: use listed values for -t tags parameters ([5bab10a](https://gitlab.com/RadianDevCore/tools/gcil/commit/5bab10a1a7601dcf603d9b635ca1fb0e98bdbeed))
- implement #22: add support for passing environment variables ([67f58c3](https://gitlab.com/RadianDevCore/tools/gcil/commit/67f58c3d8bf33cb6193c9b926e493ac90772d1ed))
- implement #28: add support for specific environment files ([fb8371f](https://gitlab.com/RadianDevCore/tools/gcil/commit/fb8371fbb46595381b8a7c000f274ded77e24d2b))
- implement #29: add support for specific volume mounts ([d1f734d](https://gitlab.com/RadianDevCore/tools/gcil/commit/d1f734d6d670303b1d5388b15abc902e68dab88f))
- implement #30: add support for working directory parameter ([260dcf6](https://gitlab.com/RadianDevCore/tools/gcil/commit/260dcf6660bec71088341a9d0c50c69be6fded26))

### 🐛 Bug Fixes

- resolve #17: support user interruptions ([77ecadf](https://gitlab.com/RadianDevCore/tools/gcil/commit/77ecadf535845c6c00d9a3da96e86ed6a5bc7e65))
- resolve #21: stop Docker container upon user interruption ([54711a8](https://gitlab.com/RadianDevCore/tools/gcil/commit/54711a8c5671dc3914188f623002cc5ac5b848a4))
- fix #25: prevent tags parameters from appending default tags ([4cadc41](https://gitlab.com/RadianDevCore/tools/gcil/commit/4cadc41265459e8171e4c22bdb36950c77f32a48))
- resolve #26: use .env variables only as default values ([fedf91a](https://gitlab.com/RadianDevCore/tools/gcil/commit/fedf91ac160d14553ab3b9341fecf19e222cbc3c))

### ⚙️ Cleanups

- implement #27: add local build and test wrapper ([34a04b2](https://gitlab.com/RadianDevCore/tools/gcil/commit/34a04b20fedf0185d56e5dd93821d05f7f1d1b89))
- resolve #15: document the .configurations features ([dcb34a2](https://gitlab.com/RadianDevCore/tools/gcil/commit/dcb34a2d3c1a1920b774551ff50f51e759bdef84))

### CHANGELOG

- implement #20: automate tag and log regeneration ([b50cd30](https://gitlab.com/RadianDevCore/tools/gcil/commit/b50cd30abaa65a246e866a040440d365c96d33c6))
- regenerate release tag changes history ([565aac2](https://gitlab.com/RadianDevCore/tools/gcil/commit/565aac2cdfba908da2a3b940fa5c7f8e353e5337))

### README

- resolve #24: document special usage cases ([7d7baa4](https://gitlab.com/RadianDevCore/tools/gcil/commit/7d7baa4e82a92a792e3a0219909bd035217e29b2))


<a name="1.0.2"></a>
## [1.0.2](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.1...1.0.2) (2020-01-21)

### ✨ Features

- resolve #6: allow menu selections while using --pipeline ([919e639](https://gitlab.com/RadianDevCore/tools/gcil/commit/919e63998daae2e9a4c3d2bbea6917f515415f9e))
- implement #7: load .env local environment variables ([04052ef](https://gitlab.com/RadianDevCore/tools/gcil/commit/04052ef09c734a0f7213fb4fb63a854e84de2854))
- implement #10: support local job tag as being manual jobs ([f78891a](https://gitlab.com/RadianDevCore/tools/gcil/commit/f78891a920f73c30b51929a57d203d1903cb3308))
- implement #11: add Changelog link on PyPI releases ([3ee37ac](https://gitlab.com/RadianDevCore/tools/gcil/commit/3ee37aca23a6a22a473134cc9719590fe8cc2d01))

### 🐛 Bug Fixes

- resolve #8: ensure Docker and other dependencies are recent ([0f05f36](https://gitlab.com/RadianDevCore/tools/gcil/commit/0f05f36b5367a9379330285485e550a7a4d48ac2))
- implement #1: add --manual-tags default values documentation ([e345ede](https://gitlab.com/RadianDevCore/tools/gcil/commit/e345ede1f65ee7bacc7f9a6cbf5b2defd4f7ce63))

### 📚 Documentation

- regenerate preview documentations and fix quotes ([5d7384a](https://gitlab.com/RadianDevCore/tools/gcil/commit/5d7384ae08ff2c72b20cd74bd0f6788ea7c15ebf))

### ⚙️ Cleanups

- implement #9: unify dependencies under requirements.txt ([08b0c06](https://gitlab.com/RadianDevCore/tools/gcil/commit/08b0c06d7a091a9538ddeef533007ef9343febae))
- resolve #12: apply VSCode, MarkdownLint and YAPF settings ([43a4e3e](https://gitlab.com/RadianDevCore/tools/gcil/commit/43a4e3e6a5825b520eef2c877b6744fa16066484))

### CHANGELOG

- implement #11: create initial CHANGELOG with git-chglog ([db97c94](https://gitlab.com/RadianDevCore/tools/gcil/commit/db97c94b2ea8192158cf440769589da97e608c28))

### README

- resolve #5: add dependencies list and purposes ([31e763b](https://gitlab.com/RadianDevCore/tools/gcil/commit/31e763b7d681ba2135ce71e2d1f671a2aac22f25))


<a name="1.0.1"></a>
## [1.0.1](https://gitlab.com/RadianDevCore/tools/gcil/compare/1.0.0...1.0.1) (2020-01-20)

### ✨ Features

- implement #2: add .configurations dynamic user choices ([87300df](https://gitlab.com/RadianDevCore/tools/gcil/commit/87300df0a5f8a04ec82fb211773614a83839178d))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/gcil/commits/1.0.0) (2020-01-19)

### Gitlabci-local

- initial public release with examples and tests ([547eb71](https://gitlab.com/RadianDevCore/tools/gcil/commit/547eb71ee6ed9df10f0c898f99e50cdfcae5a106))


