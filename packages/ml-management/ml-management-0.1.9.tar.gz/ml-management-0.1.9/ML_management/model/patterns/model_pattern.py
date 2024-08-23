"""Define Abstract class for Model with necessary methods and methods to implement."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ML_management.mlmanagement import mlmanagement, variables
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.model.patterns.rich_python_model import RichPythonModel


class Model(RichPythonModel, ABC):
    """Abstract class for model that Job will use."""

    def __init__(self):
        """Initialize Model class."""
        # That parameters will be set automatically while loading the model.
        self.artifacts: str
        """
        :param self.artifacts: local path to artifacts.
        """
        # That parameters will be set automatically in job before the 'execute' func would be executed.
        self.dataset = None
        """
        :param self.dataset: DatasetLoader object
        """

    @abstractmethod
    def predict_function(self, **kwargs):
        """Every model should make predictions."""
        raise NotImplementedError

    def to_device(self, device: str) -> None:
        """
        Define model migration to specific device.

        Devices are marked with following notation:
        cpu - CPU
        cuda:<number: int> - GPU instance
        """
        pass

    def upload_model(
        self,
        registered_model_name: str,
        description: str,
        artifacts: Optional[dict] = None,
        experiment_name: Optional[str] = None,
        pip_requirements=None,
        extra_pip_requirements=None,
        conda_env=None,
        model_version_tags: Optional[Dict[str, str]] = None,
        extra_modules_names: Optional[List[str]] = None,
        used_modules_names: Optional[List[str]] = None,
        linter_check: bool = True,
        start_build: bool = True,
        create_venv_pack: bool = False,
    ):
        """
        Upload wrapper to MLmanagement server.

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

                          If ``None``, no artifacts are added to the model.
        :param description: A string containing description for model version that is being uploaded. If a new
                                      model is being created, this description will also be added to the model
        :param model_version_tags: A dictionary containing ``<name, value>`` tag pairs to add to resulting model
                                      version as tags
        :param registered_model_name: This argument may change or be removed in a
                                      future release without warning. If given, create a model
                                      version under ``registered_model_name``, also creating a
                                      registered model if one with the given name does not exist.
                                      Must be not empty string and consist of alphanumeric characters, '_'
                                      and must start and end with an alphanumeric character.
                                      Validation regexp: ``"(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"``
        :param experiment_name: Name of experiment to which load the model
        :param pip_requirements: {{ pip_requirements }}
        :param extra_pip_requirements: {{ extra_pip_requirements }}
        `pip_requirements` and 'extra_pip_requirements' must be either a string path to a pip requirements file on the
            local filesystem or an iterable of pip requirement strings.
        :param conda_env: {{ conda_env }}
        'conda_env' must be a dict specifying the conda environment for this model.
        :param extra_modules_names: names of modules that should be pickled by value
            in addition to auto-detected modules.
        :param used_modules_names: modules that should be pickled by value, disables the auto-detection of modules.
        :param linter_check: if True, check code of the model by linter
        :param start_build: if True, start building an image for the model to use within the job later.
            If false, an image will be built when the job is started.
        :param create_venv_pack: if True, start building tar archive with model environment to use it for model serving.
        """
        old_experiment_name = variables.active_experiment_name
        if experiment_name:
            mlmanagement.set_experiment(experiment_name)
        try:
            with mlmanagement.start_run(nested=True):
                mlmanagement.log_model(
                    artifact_path="",
                    python_model=self,
                    artifacts=artifacts,
                    description=description,
                    model_version_tags=model_version_tags,
                    registered_model_name=self.model_name if hasattr(self, "model_name") else registered_model_name,
                    source_model_name=self.source_model_name
                    if hasattr(self, "source_model_name")
                    else None,  # set that after model download from mlflow
                    source_model_version=self.source_model_version
                    if hasattr(self, "source_model_version")
                    else None,  # set that after model download from mlflow
                    source_executor_name=self.source_executor_name if hasattr(self, "source_executor_name") else None,
                    source_executor_version=(
                        self.source_executor_version if hasattr(self, "source_executor_version") else None
                    ),
                    source_executor_role=self.source_executor_role if hasattr(self, "source_executor_role") else None,
                    pip_requirements=pip_requirements,
                    extra_pip_requirements=extra_pip_requirements,
                    conda_env=conda_env,
                    extra_modules_names=extra_modules_names,
                    used_modules_names=used_modules_names,
                    root_module_name=ModuleFinder.get_my_caller_module_name(),
                    linter_check=linter_check,
                    start_build=start_build,
                    create_venv_pack=create_venv_pack,
                )

        except Exception as err:
            raise err
        finally:
            variables.active_experiment_name = old_experiment_name
