"""Dataset loader template for custom dataset loader."""
from abc import ABC, abstractmethod
from typing import List, Optional

from ML_management.mlmanagement import mlmanagement, variables
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.mlmanagement.variables import EXPERIMENT_NAME_FOR_DATASET_LOADER
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.model.patterns.rich_python_model import RichPythonModel


class DatasetLoaderPattern(RichPythonModel, ABC):
    """Define dataset loader."""

    def __init__(self):
        """
        Init dataset loader class.

        :param dataset_loader_name: The name of the dataset loader.
            Must be not empty string and consist of alphanumeric characters, '_'
            and must start and end with an alphanumeric character.
            Validation regexp: "(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"
        """
        # That parameters will be set automatically while loading the model.
        """
        :param self.artifacts: local path to artifacts.
        """
        self.artifacts: str

        # That parameters will be set automatically in job before the 'get_dataset' func would be executed.
        """
        :param: self.data_path: A path to data to be loaded.
        """
        self.data_path = None

    @abstractmethod
    def get_dataset(self, **dataset_params):
        """
        Return dataset.

        To get data_path use self.data_path parameter, which also will be set in the job.
        'dataset_params' are dataset_loader parameters. One has to define it as ordinary kwargs
        with type annotation.
        """
        raise NotImplementedError

    def upload_dataset_loader(
        self,
        dataset_loader_name: str,
        description: str,
        pip_requirements=None,
        extra_pip_requirements=None,
        conda_env=None,
        artifacts: Optional[dict] = None,
        extra_modules_names: Optional[List[str]] = None,
        used_modules_names: Optional[List[str]] = None,
        linter_check=True,
    ):
        """
        Upload wrapper to MLmanagement server.

        :param pip_requirements: {{ pip_requirements }}
        :param extra_pip_requirements: {{ extra_pip_requirements }}
        `pip_requirements` and 'extra_pip_requirements' must be either a string path to a pip requirements file on the
            local filesystem or an iterable of pip requirement strings.
        :param conda_env: {{ conda_env }}
        'conda_env' must be a dict specifying the conda environment for this model.
        :param artifacts: A dictionary containing ``<name, artifact_uri>`` entries. Remote artifact URIs
                          are resolved to absolute filesystem paths, producing a dictionary of
                          ``<name, absolute_path>`` entries. ``python_model`` can reference these
                          resolved entries as the ``artifacts`` property of the ``context`` parameter
                          in :func:`PythonModel.load_context() <mlflow.pyfunc.PythonModel.load_context>`
                          and :func:`PythonModel.predict() <mlflow.pyfunc.PythonModel.predict>`.
                          For example, consider the following ``artifacts`` dictionary::

                            {
                                "my_file": "s3://my-bucket/path/to/my/file"
                            }

                          In this case, the ``"my_file"`` artifact is downloaded from S3. The
                          ``python_model`` can then refer to ``"my_file"`` as an absolute filesystem
                          path via ``context.artifacts["my_file"]``.

                          If ``None``, no artifacts are added to the dataset loader.

        :param extra_modules_names: names of modules that should be pickled by value
            in addition to auto-detected modules.

        :param used_modules_names: modules that should be pickled by value, disables the auto-detection of modules.
        """
        old_experiment_name = variables.active_experiment_name
        mlmanagement.set_experiment(EXPERIMENT_NAME_FOR_DATASET_LOADER, visibility=VisibilityOptions.PUBLIC)
        try:
            with mlmanagement.start_run(nested=True):
                mlmanagement.log_model(
                    artifact_path="",
                    artifacts=artifacts,
                    description=description,
                    python_model=self,
                    registered_model_name=dataset_loader_name,
                    pip_requirements=pip_requirements,
                    extra_pip_requirements=extra_pip_requirements,
                    conda_env=conda_env,
                    extra_modules_names=extra_modules_names,
                    used_modules_names=used_modules_names,
                    root_module_name=ModuleFinder.get_my_caller_module_name(),
                    linter_check=linter_check,
                )
        except Exception as err:
            raise err
        finally:
            variables.active_experiment_name = old_experiment_name
