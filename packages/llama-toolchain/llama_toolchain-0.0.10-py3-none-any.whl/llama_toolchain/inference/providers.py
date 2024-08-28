# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from typing import List

from llama_toolchain.distribution.datatypes import Api, InlineProviderSpec, ProviderSpec


def available_inference_providers() -> List[ProviderSpec]:
    return [
        InlineProviderSpec(
            api=Api.inference,
            provider_id="meta-reference",
            pip_packages=[
                "accelerate",
                "blobfile",
                "codeshield",
                "fairscale",
                "fbgemm-gpu==0.8.0",
                "torch",
                "transformers",
                "zmq",
            ],
            module="llama_toolchain.inference.meta_reference",
            config_class="llama_toolchain.inference.meta_reference.MetaReferenceImplConfig",
        ),
        InlineProviderSpec(
            api=Api.inference,
            provider_id="meta-ollama",
            pip_packages=[
                "ollama",
            ],
            module="llama_toolchain.inference.ollama",
            config_class="llama_toolchain.inference.ollama.OllamaImplConfig",
        ),
        InlineProviderSpec(
            api=Api.inference,
            provider_id="fireworks",
            pip_packages=[
                "fireworks-ai",
            ],
            module="llama_toolchain.inference.fireworks",
            config_class="llama_toolchain.inference.fireworks.FireworksImplConfig",
        ),
    ]
