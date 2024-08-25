#!/bin/bash

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

set -euo pipefail

# Define color codes
RED='\033[0;31m'
NC='\033[0m' # No Color

error_handler() {
  echo "Error occurred in script at line: ${1}" >&2
  exit 1
}

# Set up the error trap
trap 'error_handler ${LINENO}' ERR

if [ $# -lt 2 ]; then
    echo "Usage: $0 <environment_name> <script_args...>"
    exit 1
fi


env_name="$1"
shift

eval "$(conda shell.bash hook)"
conda deactivate && conda activate "$env_name"

python_interp=$(conda run -n "$env_name" which python)
$python_interp -m llama_toolchain.distribution.server "$@"
