"""Script for upload defaults executors."""
import os

from ML_management.mlmanagement import mlmanagement
from ML_management.mlmanagement.visibility_options import VisibilityOptions


def upload_eval_executor():
    mlmanagement.log_executor_src(
        description="Evaluate executor",
        registered_name="eval",
        model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "eval"),
        visibility=VisibilityOptions.PUBLIC,
    )


def upload_train_executor():
    mlmanagement.log_executor_src(
        description="Train executor",
        registered_name="train",
        model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "train"),
        visibility=VisibilityOptions.PUBLIC,
    )


def upload_finetune_executor():
    mlmanagement.log_executor_src(
        description="Finetune executor",
        registered_name="finetune",
        model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "finetune"),
        visibility=VisibilityOptions.PUBLIC,
    )
