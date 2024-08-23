# awscli-profile

[![PyPI - Version](https://img.shields.io/pypi/v/awscli-profile)](https://pypi.org/project/awscli-profile/)


a simple profile switcher for awscli

# Installation

```shell
$ pip install awscli_profile
```

# Usage

```shell
$ aws-profile
 0)account1 - AKA....
*1)account2 - AKB....

Choose profile: 0
Switched to: account1
```

```
$ aws-profile account2
Switched to: account2
```

## as a awscli alias

```shell
$ echo 'profile = !aws-profile' >> ~/.aws/cli/alias
```