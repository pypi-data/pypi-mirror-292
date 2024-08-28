# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

# pyre-strict

import os

from atek.data_loaders.atek_wds_dataloader import (
    process_wds_sample,
    select_and_remap_dict_keys,
)


class AtekRawDataloader:
    def __init__(self, model_key_remapping, model_adaptor_fn) -> None:
        self.model_key_remapping = model_key_remapping
        self.model_adaptor_fn = model_adaptor_fn

    def convert_to_model_specific_sample(self, atek_data_sample):
        atek_sample_dict = atek_data_sample.to_flatten_dict()

        # key remapping
        remapped_data_dict = select_and_remap_dict_keys(
            sample_dict=atek_sample_dict, key_mapping=self.model_key_remapping
        )

        # transform
        model_specific_sample = self.model_adaptor_fn([remapped_data_dict])

        return model_specific_sample
