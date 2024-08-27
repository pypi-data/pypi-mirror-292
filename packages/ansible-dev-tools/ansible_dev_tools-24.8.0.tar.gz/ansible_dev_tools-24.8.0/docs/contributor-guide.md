---
hide:
  - navigation
  - toc
---

# Contributor Guide

To contribute to `ansible-dev-tools` python package or to the list of tools part of it, please use pull requests on a branch of your own fork.

After [creating your fork on GitHub], you can do:

```shell-session
$ git clone --recursive git@github.com:your-name/developer-tool-name
$ cd developer-tool-name
$ git checkout -b your-branch-name
# DO SOME CODING HERE
$ git add your new files
$ git commit -v
$ git push origin your-branch-name
```

You will then be able to create a pull request from your commit.

Prerequisites:

1. All fixes to core functionality (i.e. anything except docs or examples) should
   be accompanied by tests that fail prior to your change and succeed afterwards.

2. Before sending a PR, make sure that `tox -e lint` passes.

Feel free to raise issues in the repo if you feel unable to contribute a code
fix.

## Container testing

`pytest` has been extended to facilitate testing a container.

```shell
Custom options:
  --container-engine=CONTAINER_ENGINE
                        Container engine to use. (default=ADT_CONTAINER_ENGINE, podman, docker, '')
  --container-name=CONTAINER_NAME
                        Container name to use for the running container. (default=ADT_CONTAINER_NAME)
  --image-name=IMAGE_NAME
                        Container name to use. (default=ADT_IMAGE_NAME)
  --only-container      Only run container tests
  --include-container   Include container tests
```

Container tests can be run with either of the following commands:

```shell
# Run the tests against the default container engine
pytest --only-container
pytest --only-container --container-engine=<ce> --image-name <image>
tox -e test-image
tox -e test-image -- --container-engine=<ce> --image-name <image>
```

See the `tests/integration/test_container.py` for examples.

## Talk to us

Use Github [discussions] forum or for a live chat experience try
`#ansible-devtools` IRC channel on libera.chat or Matrix room
[#devtools:ansible.com](https://matrix.to/#/#devtools:ansible.com).

For the full list of Ansible IRC and Mailing list, please see the [Ansible
Communication] page. Release announcements will be made to the [Ansible
Announce] list.

Possible security bugs should be reported via email to
<mailto:security@ansible.com>.

## Code of Conduct

Please see the official [Ansible Community Code of Conduct].

[discussions]: https://github.com/ansible/ansible-dev-tools/discussions
[ansible communication]: https://docs.ansible.com/ansible/latest/community/communication.html
[ansible announce]: https://groups.google.com/forum/#!forum/ansible-announce
[Ansible Community Code of Conduct]: https://docs.ansible.com/ansible/latest/community/code_of_conduct.html
[creating your fork on github]: https://docs.github.com/en/get-started/quickstart/contributing-to-projects
