Does your AWS infrastructure really do what you think it does? Prove it by writing tests!

This repository holds [lettuce](http://lettuce.it) steps for testing [CloudFormation](http://aws.amazon.com/cloudformation) templates. 

# TL;DR and I wanna use this

Get these steps in your repo as a subtree at features/cfn-steps and begin writing features. Check the [wiki](https://github.com/controlgroup/cloudformation-lettuce-steps/wiki) for help on writing features. 

Run tests on your cloudformation code by running lettuce.


# Installing

## Getting your system ready to test

Some steps utilize Python modules to do their tests. The modules that are required are listed in the [requirements.txt](requirements.txt). 

You can install these with your package manager, but many of us use virtualenv to handle this. A good way to get virtualenv up and running is to use [virtualenv-burrito](https://github.com/brainsik/virtualenv-burrito). 

You will also need to set up a boto config file with your AWS credentials to validate templates against the CloudFormation API. Here are [instructions for configuring boto](http://docs.pythonboto.org/en/latest/boto_config_tut.html).

## Adding these steps to an existing repository

When you start testing cloudformation, you want to organize your repository like this:

```
.
├── ec2-server.template <-- The CloudFormation templates you are writing.
└── features
    ├── ec2-server.feature <-- A feature file that you have written to test your CloudFormation
    ├── cfn-steps <-- This repository, as a subtree
```

A good way to get these integrated into an existing repository is to use [subtree merging](http://git-scm.com/book/ch6-7.html). Here's a step by step from the root of your local git repository:

```
# Make the features directory
mkdir features

# Add and fetch this repository
git remote add cloudformation-lettuce-steps-remote git@github.com:controlgroup/cloudformation-lettuce-steps.git
git fetch cloudformation-lettuce-steps-remote

# Store it in your own local branch
git checkout -b cloudformation-lettuce-steps-branch cloudformation-lettuce-steps-remote/master

# Merge the tree into your master branch
git checkout master
git read-tree --prefix=features/cfn-steps -u cloudformation-lettuce-steps-branch
```

You'll have some changes on your master branch that you will need to commit. You're ready to write tests at this point!

If new steps are released you can easily pull them in:

```
# Get the latest changes
git checkout cloudformation-lettuce-steps-branch
git pull

# Merge them into master
git checkout master
git merge --squash -s subtree --no-commit cloudformation-lettuce-steps-branch
```

