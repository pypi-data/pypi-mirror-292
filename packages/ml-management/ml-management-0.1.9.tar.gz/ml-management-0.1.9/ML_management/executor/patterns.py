"""Module with patterns for models parameters in executors."""
from typing import List, Tuple

from pydantic import BaseModel

from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import DatasetLoaderMethodName
from ML_management.executor.upload_model_mode import UploadModelMode
from ML_management.model.model_type_to_methods_map import ModelMethodName

DEFAULT_ROLE = "single"


class OneModelPattern(BaseModel):
    """Pattern for only one model."""

    upload_model_mode: UploadModelMode
    desired_model_methods: List[ModelMethodName]

    def serialize(self) -> Tuple[dict, dict]:
        return {DEFAULT_ROLE: self.upload_model_mode}, {DEFAULT_ROLE: self.desired_model_methods}


class OneModelPatternWithRole(OneModelPattern):
    """Pattern for only one model with specific role."""

    role: str

    def serialize(self) -> Tuple[dict, dict]:
        return {self.role: self.upload_model_mode}, {self.role: self.desired_model_methods}


class OneDatasetLoaderPattern(BaseModel):
    """Pattern for only one dataset loader."""

    desired_dataset_loader_methods: List[DatasetLoaderMethodName] = [DatasetLoaderMethodName.get_dataset]

    def serialize(self) -> dict:
        return {DEFAULT_ROLE: self.desired_dataset_loader_methods}


class OneDatasetLoaderPatternWithRole(OneDatasetLoaderPattern):
    """Pattern for only one dataset loader with specific role."""

    role: str

    def serialize(self) -> dict:
        return {self.role: self.desired_dataset_loader_methods}


class ArbitraryDatasetLoaderPattern(BaseModel):
    """Pattern for arbitrary number of dataset loaders."""

    desired_dataset_loaders: List[OneDatasetLoaderPatternWithRole]

    def serialize(self) -> dict:
        result = {}
        roles_set = set()
        multiple_roles = set()
        for desired_dataset_loader in self.desired_dataset_loaders:
            if desired_dataset_loader.role in roles_set:
                multiple_roles.add(desired_dataset_loader.role)
            roles_set.add(desired_dataset_loader.role)
            result.update(desired_dataset_loader.serialize())
        if len(multiple_roles) != 0:
            raise RuntimeError(
                "Your data loaders must have different roles. "
                f"Roles {', '.join(multiple_roles)} occur 2 or more times."
            )
        return result


class ArbitraryModelsPattern(BaseModel):
    """Pattern for arbitrary number of models."""

    desired_models: List[OneModelPatternWithRole]

    def serialize(self) -> Tuple[dict, dict]:
        upload_model_modes, desired_model_methods = {}, {}
        roles_set = set()
        multiple_roles = set()
        for desired_model in self.desired_models:
            if desired_model.role in roles_set:
                multiple_roles.add(desired_model.role)
            roles_set.add(desired_model.role)
            current_upload_model_modes, current_desired_model_methods = desired_model.serialize()
            upload_model_modes.update(current_upload_model_modes)
            desired_model_methods.update(current_desired_model_methods)
        if len(multiple_roles) != 0:
            raise RuntimeError(
                f"Your models must have different roles. Roles {', '.join(multiple_roles)} occur 2 ore more times."
            )
        return upload_model_modes, desired_model_methods
