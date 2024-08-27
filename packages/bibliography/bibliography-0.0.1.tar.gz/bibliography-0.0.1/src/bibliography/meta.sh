#!/usr/bin/env sh


export VERSION=0.0.1

export NAME=bibliography

export DESCRIPTION=""
export DESCRIPTION="${DESCRIPTION}Stub files to use as the basis of a Python"
export DESCRIPTION="${DESCRIPTION} project that can be packaged and uploaded to PyPI"

export LONG_DESC=""
export LONG_DESC="${LONG_DESC}"'The ``python-project-stub`` codebase provides stub files that\n'
export LONG_DESC="${LONG_DESC}"'can be used to create a Python project that is able to\n'
export LONG_DESC="${LONG_DESC}"'be packaged and uploaded to the Python Package Index\n'
export LONG_DESC="${LONG_DESC}"'and hence can be conveniently installed with\n'
export LONG_DESC="${LONG_DESC}"'\n'
export LONG_DESC="${LONG_DESC}"'.. code-block:: sh\n'
export LONG_DESC="${LONG_DESC}"'   \n'
export LONG_DESC="${LONG_DESC}"'   pip install my-project-name\n'
export LONG_DESC="${LONG_DESC}"'   \n'
export LONG_DESC="${LONG_DESC}"'The ``Makefile`` provided in the codebase has targets for\n'
export LONG_DESC="${LONG_DESC}"'building, uploading,\n'
export LONG_DESC="${LONG_DESC}"'downloading, installing, and executing the package.'


export GITHUB_USER='striebel'

export AUTHOR='Jacob Striebel'
export AUTHOR_EMAIL='jacob.striebel@example.com'

export FIRST_COPYRIGHT_YEAR=2023

export BUILD_REQUIRES=''
export BUILD_REQUIRES=${BUILD_REQUIRES}'"setuptools>=61.0.0"'

export REQUIRES=''
#export REQUIRES=${REQUIRES}'"allennlp==1.3.0"'
#export REQUIRES=${REQUIRES}',"transformers==4.0.0"'
#export REQUIRES=${REQUIRES}',"torch==1.7.1"'
#export REQUIRES=${REQUIRES}',"jsonnet==0.20.0"'



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#  Most files other than Python source files must be explicitly specified   #
#  if it is desired that they be included in the built package              #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
export INCLUDE_FILES="meta.sh"
export INCLUDE_FILES="${INCLUDE_FILES}:data/quote.txt"



# logging level str options:
#
#     CRITICAL, ERROR, WARNING, INFO, DEBUG
#
export DEFAULT_LOGGING_LEVEL_STR='DEBUG'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#  The following statements print the the metadata variables defined above  #
#  in a format that can be exec'd by a Python program                       #
#                                                                           #
#  Likely you don't want to modify statements in the section below          #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

printf 'global VERSION                  \n'
printf 'global NAME                     \n'
printf 'global DESCRIPTION              \n'
printf 'global LONG_DESC                \n'
printf 'global GITHUB_USER              \n'
printf 'global AUTHOR                   \n'
printf 'global AUTHOR_EMAIL             \n'
printf 'global FIRST_COPYRIGHT_YEAR     \n'
printf 'global BUILD_REQUIRES           \n'
printf 'global REQUIRES                 \n'
printf 'global INCLUDE_FILES            \n'
printf 'global DEFAULT_LOGGING_LEVEL_STR\n'

printf 'VERSION                   = "%s"\n' "$VERSION"
printf 'NAME                      = "%s"\n' "$NAME"
printf 'DESCRIPTION               = "%s"\n' "$DESCRIPTION"
printf 'LONG_DESC                 = "%s"\n' "$LONG_DESC"
printf 'GITHUB_USER               = "%s"\n' "$GITHUB_USER"
printf 'AUTHOR                    = "%s"\n' "$AUTHOR"
printf 'AUTHOR_EMAIL              = "%s"\n' "$AUTHOR_EMAIL"
printf 'FIRST_COPYRIGHT_YEAR      = "%s"\n' "$FIRST_COPYRIGHT_YEAR"
printf "BUILD_REQUIRES            = '%s'\n" "$BUILD_REQUIRES"
printf "REQUIRES                  = '%s'\n" "$REQUIRES"
printf 'INCLUDE_FILES             = "%s"\n' "$INCLUDE_FILES"
printf 'DEFAULT_LOGGING_LEVEL_STR = "%s"\n' "$DEFAULT_LOGGING_LEVEL_STR"


