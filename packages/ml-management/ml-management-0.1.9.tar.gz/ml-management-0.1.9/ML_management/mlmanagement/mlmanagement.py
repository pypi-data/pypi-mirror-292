"""
Mlflow server inside ML_management.

ML_manager sends request to our server on /mlflow endpoint
Server calls original mlflow function accordingly
"""
import atexit
import importlib
import inspect
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cloudpickle
import numpy
import pandas
from scipy.sparse import csc_matrix, csr_matrix

import mlflow
from ML_management.mlmanagement import variables
from ML_management.mlmanagement.abstract_mlflow_client import AbstractMlflowClient
from ML_management.mlmanagement.base_exceptions import PylintError
from ML_management.mlmanagement.mlmanager import request_for_function
from ML_management.mlmanagement.model_type import ModelType
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.mlmanagement.server_mlmanager_exceptions import ModelTypeIsNotFoundError
from ML_management.mlmanagement.utils import _load_model_type, is_model_name_valid, validate_predict_config
from ML_management.mlmanagement.variables import (
    EXPERIMENT_NAME_FOR_DATASET_LOADER,
    EXPERIMENT_NAME_FOR_EXECUTOR,
    FILENAME_FOR_INFERENCE_CONFIG,
    active_run_stack,
)
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from mlflow import ActiveRun
from mlflow.entities import Experiment, Run, RunStatus
from mlflow.entities.model_registry import ModelVersion
from mlflow.models import Model
from mlflow.pyfunc import DATA
from mlflow.store.entities import PagedList
from mlflow.tracking.fluent import _RUN_ID_ENV_VAR
from mlflow.utils import env


def monkey_patching_exit(self, exc_type, exc_val, exc_tb):
    """Redefine __exit__ function of class ActiveRun."""
    status = RunStatus.FINISHED if exc_type is None else RunStatus.FAILED
    end_run(RunStatus.to_string(status))
    return exc_type is None


# Rewrite __exit__ method to enable using Python ``with`` syntax of ActiveRun class.
ActiveRun.__exit__ = monkey_patching_exit


def start_run_if_not_exist():
    """If run doesn't exist call start_run() function."""
    if len(active_run_stack) == 0:
        start_run()


def set_experiment(
    experiment_name: Optional[str] = None,
    experiment_id: Optional[str] = None,
    visibility: VisibilityOptions = VisibilityOptions.PRIVATE,
) -> Experiment:
    """
    Set the given experiment as the active experiment.

    The experiment must either be specified by name via
    experiment_name or by ID via experiment_id. The experiment name and ID cannot both be specified.
    Set global variable active_experiment_name to that experiment_name.
    """
    experiment = request_for_function(inspect.currentframe())
    variables.active_experiment_name = experiment_name
    return experiment


def start_run(
    run_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    run_name: Optional[str] = None,
    nested: bool = False,
    tags: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> ActiveRun:
    """
    Start a new MLflow run, setting it as the active run under which metrics and parameters will be logged.

    The return value can be used as a context manager within a with block; otherwise, you must call end_run() to
    terminate the current run.
    If you pass a run_id or the MLFLOW_RUN_ID environment variable is set, start_run attempts to resume a run with
    the specified run ID and other parameters are ignored. run_id takes precedence over MLFLOW_RUN_ID.
    If resuming an existing run, the run status is set to RunStatus.RUNNING.
    Add that created run to active_run_stack.
    """
    if len(active_run_stack) > 0 and not nested:
        raise Exception(
            (
                "Run with UUID {} is already active. To start a new run, first end the "
                "current run with mlmanagement.end_run(). To start a nested "
                "run, call start_run with nested=True"
            ).format(active_run_stack[0].info.run_id)
        )
    _active_run = request_for_function(inspect.currentframe())
    active_run_stack.append(_active_run)
    return _active_run


def _add_job_registration_metainfo(
    registration_timestamp,
    init_model_version_run_ids,
    dataset_loader_version_run_ids,
    executor_version_run_id,
    name,
    job_executor_name,
    job_executor_version,
    role_dataset_loader_map,
    role_model_map,
    new_model_names,
    prepare_new_models_inference,
    descriptions,
    experiment_name,
    periodic_type,
    cron_expression,
    executor_params_json,
    models_params_json,
    dataset_loaders_params_json,
    collectors_params_json,
    role_collectors_map,
    gpu,
    additional_system_packages,
):
    """Add job metainfo on job registration. For internal use only."""
    return request_for_function(inspect.currentframe())


def _add_job_start_metainfo(
    job_name,
    start_timestamp,
):
    """Add job metainfo on execution start. For internal use only."""
    return request_for_function(inspect.currentframe())


def _add_job_end_metainfo(
    job_name,
    end_timestamp,
):
    """Add job metainfo on execution end. For internal use only."""
    return request_for_function(inspect.currentframe())


def _add_job_fail_metainfo(
    job_name,
    end_timestamp,
):
    """Add job metainfo on execution fail. For internal use only."""
    return request_for_function(inspect.currentframe())


def log_model(
    artifact_path,
    description: Optional[str],
    model_version_tags: Optional[Dict[str, str]] = None,
    code_path=None,
    conda_env=None,
    python_model=None,
    artifacts: Optional[dict] = None,
    registered_model_name: str = "default_name",
    signature: mlflow.models.signature.ModelSignature = None,
    input_example: Union[
        pandas.core.frame.DataFrame, numpy.ndarray, dict, list, csr_matrix, csc_matrix, str, bytes
    ] = None,
    await_registration_for: int = 300,
    pip_requirements=None,
    extra_pip_requirements=None,
    metadata=None,
    source_model_name=None,
    source_model_version=None,
    source_executor_name=None,
    source_executor_version=None,
    source_executor_role=None,
    upload_model_mode=None,
    visibility=None,
    extra_modules_names: Optional[list] = None,
    used_modules_names: Optional[list] = None,
    root_module_name: str = "__main__",
    linter_check: bool = True,
    start_build: bool = True,
    create_venv_pack: bool = False,
):
    """
    Log a Pyfunc model with custom inference logic and optional data dependencies as an MLflow artifact.

    Current run is using.
    Parameter registered_model_name must be not empty string,
        consist of alphanumeric characters, '_'
        and must start and end with an alphanumeric character.
        Validation regexp: "(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"
    You cannot specify the parameters: loader_module, data_path and the parameters: python_model, artifacts together.
    """
    from ML_management.executor.upload_model_mode import UploadModelMode  # circular import

    if extra_modules_names and used_modules_names:
        raise RuntimeError("Parameters 'extra_modules_names' and 'used_modules_names' cannot be used at the same time.")
    if upload_model_mode == UploadModelMode.none:
        raise RuntimeError("You can't log a model using the 'upload_model_mode' parameter set to none.")
    if not is_model_name_valid(registered_model_name):
        raise RuntimeError(
            "Parameter 'registered_model_name' must be not empty string, "
            "consist of alphanumeric characters, '_' "
            "and must start and end with an alphanumeric character."
            "Validation regexp: '(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+'"
        )
    del UploadModelMode  # need to delete this because it is not JSON serializable
    if create_venv_pack:
        if not isinstance(artifacts, dict):
            raise RuntimeError("You must provide config for model serving in artifacts, if create_venv_pack=True")
        validate_predict_config(path=artifacts.get(FILENAME_FOR_INFERENCE_CONFIG))
    start_run_if_not_exist()
    if used_modules_names is not None:
        submodules = set(used_modules_names)
        ModuleFinder.import_modules_by_name(submodules)
    else:
        submodules = ModuleFinder().find_root_submodules(root_name=root_module_name)
        if linter_check:
            for module_name in submodules:
                if hasattr(sys.modules[module_name], "__file__"):
                    # pylint check what would fall on any error except when abstract method is not implemented (E0110)
                    # and when pylint has been unable to import a module (E0401)
                    linter_output = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pylint",
                            "{}".format(sys.modules[module_name].__file__),
                            "--clear-cache-post-run=True",
                            "--disable=all",
                            "--enable=E",
                            "--disable=E0401, E1101",
                            "--fail-on=E",
                            "--reports=n",
                            "--score=n",
                            "-j 0",
                        ],
                        check=False,
                        stdout=subprocess.PIPE,
                        text=True,
                    )
                    if linter_output.stdout:  # if linter has output when something wrong with code
                        raise PylintError(linter_output.stdout)
                    del linter_output
        if extra_modules_names:
            extra_set = set(extra_modules_names)
            ModuleFinder.import_modules_by_name(extra_set)
            submodules = submodules.union(extra_set)
    try:
        for module_name in submodules:
            cloudpickle.register_pickle_by_value(sys.modules[module_name])
        result = request_for_function(inspect.currentframe(), ["pyfunc"])
        return result
    finally:
        for module_name in submodules:
            cloudpickle.unregister_pickle_by_value(sys.modules[module_name])


def log_object_src(
    artifact_path,
    model_path: str,
    description: str,
    model_version_tags: Optional[Dict[str, str]] = None,
    code_path=None,
    conda_env=None,
    python_model=None,
    registered_model_name: str = "default_name",
    signature: mlflow.models.signature.ModelSignature = None,
    input_example: Union[
        pandas.core.frame.DataFrame, numpy.ndarray, dict, list, csr_matrix, csc_matrix, str, bytes
    ] = None,
    await_registration_for: int = 300,
    pip_requirements=None,
    extra_pip_requirements=None,
    metadata=None,
    source_model_name=None,
    source_model_version=None,
    source_executor_name=None,
    source_executor_version=None,
    source_executor_role=None,
    upload_model_mode=None,
    visibility=None,
    start_build: bool = True,
    create_venv_pack: bool = False,
    additional_local_packages: Optional[List[str]] = None,
):
    """
    Log a Pyfunc model with custom inference logic and optional data dependencies as an MLflow artifact.

    Current run is using.
    Parameter registered_model_name must be not empty string,
            consist of alphanumeric characters, '_'
            and must start and end with an alphanumeric character.
            Validation regexp: "(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"
    You cannot specify the parameters: loader_module, data_path and the parameters: python_model, artifacts together.
    """
    from ML_management.executor.upload_model_mode import UploadModelMode  # circular import

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Path: {model_path} does not exist.")

    if not os.path.exists(os.path.join(model_path, "conda.yaml")):
        raise FileNotFoundError("There is no conda.yaml file.")

    if upload_model_mode == UploadModelMode.none:
        raise RuntimeError("You can't log a model using the 'upload_model_mode' parameter set to none.")
    if not is_model_name_valid(registered_model_name):
        raise RuntimeError(
            "Parameter 'registered_model_name' must be not empty string, "
            "consist of alphanumeric characters, '_'"
            "and must start and end with an alphanumeric character."
            "Validation regexp: '(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+'"
        )
    del UploadModelMode  # need to delete this because it is not JSON serializable
    if create_venv_pack:
        validate_predict_config(path=os.path.join(f"{model_path}", "artifacts", f"{FILENAME_FOR_INFERENCE_CONFIG}"))
    start_run_if_not_exist()
    python_path = sys.path
    try:
        model_path = os.path.abspath(model_path)
        parts = Path(model_path).parts
        sys.path.append(str(Path(*parts[:-2])))
        python_model = importlib.import_module(".".join(parts[-2:])).get_object()  # noqa: F841
        result = request_for_function(inspect.currentframe(), ["pyfunc"])
    except Exception as err:
        raise err
    finally:
        sys.path = python_path
    if additional_local_packages:
        for package in additional_local_packages:
            log_artifact(package, DATA)
    return result


def log_executor_src(
    model_path: str,
    registered_name: str,
    description: str,
    artifact_path: str = "",
    start_build: bool = False,
    visibility: VisibilityOptions = VisibilityOptions.PRIVATE,
    additional_local_packages: Optional[List[str]] = None,
):
    """
    Upload executor using folder with source code of the executor.

    model_path folder must contain "__init__.py" file with get_object function
    which have to return instance of the executor.
    Also model_path must contain "conda.yaml" file with dependencies of the executor
    model_path can optionally contain "artifacts" folder with files/folders,
    which would be automatically uploaded with executor
    and path to them can be accessed with self.artifacts within executor class.

    Parameters
    ----------
        model_path: str
            Path to folder with executor.
        registered_name: str
            Name of the executor.
        description: str
            Description of the executor
        artifact_path: str
            Path to the folder with additional artifacts of the executor.
        start_build: bool
            Is to start build image of the executor right after it was logged. Defaults to False.
        visibility: VisibilityOptions
            Visibility of this executor to other users. Possible values VisibilityOptions.PRIVATE, PUBLIC.
            Defaults to PRIVATE.
        additional_local_packages: Optional[List[str]]
            Path to folder with local dependencies which are not within model_path folder. Defaults to None.

    """
    old_experiment_name = variables.active_experiment_name

    try:
        set_experiment(EXPERIMENT_NAME_FOR_EXECUTOR, visibility=VisibilityOptions.PUBLIC)

        with start_run(nested=True):
            log_object_src(
                artifact_path=artifact_path,
                description=description,
                registered_model_name=registered_name,
                start_build=start_build,
                model_path=model_path,
                visibility=visibility,
                additional_local_packages=additional_local_packages,
            )

    except Exception as err:
        raise err
    finally:
        variables.active_experiment_name = old_experiment_name


def log_dataset_loader_src(
    model_path: str,
    registered_name: str,
    description: str,
    artifact_path: str = "",
    additional_local_packages: Optional[List[str]] = None,
):
    """
    Upload dataset loader using folder with source code of the dataset loader.

    model_path folder must contain "__init__.py" file with get_object function
    which have to return instance of the dataset loader.
    Also model_path must contain "conda.yaml" file with dependencies of the dataset loader
    model_path can optionally contain "artifacts" folder with files/folders,
    which would be automatically uploaded with dataset loader
    and path to them can be accessed with self.artifacts within dataset loader class.

    Parameters
    ----------
        model_path: str
            Path to folder with dataset loader.
        registered_name: str
            Name of the dataset loader.
        description: str
            Description of the dataset loader
        artifact_path: str
            Path to the folder with additional artifacts of the dataset loader.
        additional_local_packages: Optional[List[str]]
            Path to folder with local dependencies which are not within model_path folder. Defaults to None.

    """
    old_experiment_name = variables.active_experiment_name
    try:
        set_experiment(EXPERIMENT_NAME_FOR_DATASET_LOADER, visibility=VisibilityOptions.PUBLIC)
        with start_run(nested=True):
            log_object_src(
                artifact_path=artifact_path,
                description=description,
                registered_model_name=registered_name,
                model_path=model_path,
                additional_local_packages=additional_local_packages,
            )
    except Exception as err:
        raise err
    finally:
        variables.active_experiment_name = old_experiment_name


def log_model_src(
    model_path: str,
    registered_name: str,
    description: str,
    artifact_path: str = "",
    start_build: bool = True,
    model_version_tags: Optional[Dict[str, str]] = None,
    create_venv_pack: bool = False,
    additional_local_packages: Optional[List[str]] = None,
):
    """Parameter registered_name should match regexp "(([A-Za-z0-9][A-Za-z0-9_]*)?[A-Za-z0-9])+"."""
    with start_run(nested=True):
        log_object_src(
            artifact_path=artifact_path,
            description=description,
            registered_model_name=registered_name,
            model_path=model_path,
            visibility=VisibilityOptions.PRIVATE,
            start_build=start_build,
            model_version_tags=model_version_tags,
            create_venv_pack=create_venv_pack,
            additional_local_packages=additional_local_packages,
        )


def log_metric(key: str, value: float, step: Optional[int] = None) -> None:
    """
    Log a metric under the current run. If no run is active, this method will create a new active run.

    Parameters
    key - Metric name (string).
    This string may only contain alphanumerics, underscores (_), dashes (-), periods (.), spaces ( ), and slashes (/).
    All backend stores will support keys up to length 250, but some may support larger keys.

    value - Metric value (float). Note that some special values such as +/-
    Infinity may be replaced by other values depending on the store.
    For example, the SQLAlchemy store replaces +/- Infinity with max / min float values.
    All backend stores will support values up to length 5000, but some may support larger values.

    step - Metric step (int). Defaults to zero if unspecified.

    Returns
    Returns None.
    """
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe())


def log_artifact(local_path: str, artifact_path: Optional[str] = None) -> None:
    """
    Log a local file or directory as an artifact of the currently active run.

    If no run is active, this method will create a new active run.
    """
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe())


def log_param(key: str, value: Any) -> Any:
    """
    Log a parameter (e.g. model hyperparameter) under the current run.

    If no run is active, this method will create a new active run.
    """
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe())


def log_params(params: Dict[str, Any]) -> None:
    """
    Log a batch of params for the current run.

    If no run is active, this method will create a new active run.
    """
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe())


def set_tag(key: str, value: Any) -> None:
    """Set a tag under the current run. If no run is active, this method will create a new active run."""
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe())


def autolog(
    log_every_n_epoch=1,
    log_every_n_step=None,
    log_models=True,
    log_datasets=True,
    disable=False,
    exclusive=False,
    disable_for_unsupported_versions=False,
    silent=False,
    registered_model_name=None,
) -> None:
    """
    Enable (or disable) and configure autologging for all supported integrations.

    The parameters are passed to any autologging integrations that support them.
    """
    start_run_if_not_exist()
    return request_for_function(inspect.currentframe(), ["pytorch"])


default_model = Model()


def save_model(
    path,
    loader_module=None,
    data_path=None,
    code_path=None,
    conda_env=None,
    mlflow_model=default_model,
    python_model=None,
    artifacts=None,
):
    """
    Save a Pyfunc model with custom inference logic and optional data dependencies to a path on the local filesystem.

    You cannot specify the parameters: loader_module, data_path and the parameters: python_model, artifacts together.
    """
    return request_for_function(inspect.currentframe(), ["pyfunc"])


def active_run() -> Optional[ActiveRun]:
    """Get the currently active Run, or None if no such run exists."""
    return active_run_stack[-1] if len(active_run_stack) > 0 else None


finished_run_status = RunStatus.to_string(RunStatus.FINISHED)


def end_run(status: str = finished_run_status) -> None:
    """End an active MLflow run (if there is one)."""
    if len(active_run_stack) > 0:
        # Clear out the global existing run environment variable as well.
        env.unset_variable(_RUN_ID_ENV_VAR)
        run = active_run_stack[-1]
        MlflowClient().set_terminated(run.info.run_id, status)
        active_run_stack.pop()


def set_server_url(url: str) -> None:
    """
    Set server URL.

    If you set the URL using this function,
    it takes precedence over the URL from the environment variable 'server_url'.
    """
    variables.server_url = url


def set_s3_url(url: str) -> None:
    """
    Set s3 URL.

    If you set the URL using this function,
    it takes precedence over the URL from the environment variable 'S3_URL'.
    """
    variables.s3_url = url


def set_mlm_credentials(login: str, password: str) -> None:
    """
    Set login and password for mlmanagement.

    If you set the credentials using this function,
    it takes precedence over the credentials from the environment variables.
    """
    variables.mlm_login = login
    variables.mlm_password = password


def get_server_url() -> str:
    """Get the current server URL."""
    return variables._get_server_url()


def get_s3_gateway_url() -> str:
    """Get the current minio URL."""
    return variables._get_s3_gateway_url()


def get_server_websocket_url() -> str:
    """Get the current websocket server URL."""
    url = get_server_url()
    splitted_url = url.split("/")
    splitted_url[0] = "wss:" if "https" in url else "ws:"
    return "/".join(splitted_url)


def set_model_version_requirements(name: str, version: int, model_type: ModelType) -> None:
    """Installing requirements of the model locally."""
    if model_type == ModelType.MODEL:
        requirements = MlflowClient().get_model_version_requirements(name=name, version=version)
    elif model_type == ModelType.EXECUTOR:
        requirements = MlflowClient().get_executor_version_requirements(name=name, version=version)
    elif model_type == ModelType.DATASET_LOADER:
        requirements = MlflowClient().get_dataset_loader_version_requirements(name=name, version=version)
    else:
        raise ModelTypeIsNotFoundError()
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--default-timeout=100", *requirements]
        )
    except Exception:
        print(traceback.format_exc())
        print(f"Requirements for {name} weren't installed correctly.")


def load_model(
    name: str, version: int, install_requirements: bool = False, unwrap: bool = True, dst_path: Optional[str] = None
):
    """Download all model's files for loading model locally."""
    if install_requirements:
        set_model_version_requirements(name=name, version=version, model_type=ModelType.MODEL)
    run_id = MlflowClient().get_model_version(name, version).run_id
    return _load_model_type(run_id, unwrap, dst_path)


def load_dataset(
    name: str, version: int, install_requirements: bool = False, unwrap: bool = True, dst_path: Optional[str] = None
):
    """Download all model's files for loading model locally."""
    if install_requirements:
        set_model_version_requirements(name=name, version=version, model_type=ModelType.DATASET_LOADER)
    run_id = MlflowClient().get_dataset_loader_version(name, version).run_id
    return _load_model_type(run_id, unwrap, dst_path)


def load_executor(
    name: str, version: int, install_requirements: bool = False, unwrap: bool = True, dst_path: Optional[str] = None
):
    """Download all model's files for loading model locally."""
    if install_requirements:
        set_model_version_requirements(name=name, version=version, model_type=ModelType.EXECUTOR)
    run_id = MlflowClient().get_executor_version(name, version).run_id
    return _load_model_type(run_id, unwrap, dst_path)


atexit.register(end_run)


class MlflowClient(AbstractMlflowClient):
    """Initialize an MLflow Client."""

    def __init__(self):
        self.extra_attrs = ["tracking"]
        self.for_class = {"class_name": self.__class__.__name__, "class_kwargs": {}}

    def set_model_version_tag(
        self,
        name: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        stage: Optional[str] = None,
    ) -> None:
        """Set model version tag."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def set_dataset_loader_version_tag(
        self,
        name: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        stage: Optional[str] = None,
    ) -> None:
        """Set dataset loader version tag."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def set_executor_version_tag(
        self,
        name: str,
        version: Optional[str] = None,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        stage: Optional[str] = None,
    ) -> None:
        """Set executor version tag."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def update_model_version(self, name: str, version: str, description: Optional[str] = None) -> ModelVersion:
        """Set description for model's ModelVersion entity."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def update_executor_version(self, name: str, version: str, description: Optional[str] = None) -> ModelVersion:
        """Set description for executor's ModelVersion entity."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def update_dataset_loader_version(self, name: str, version: str, description: Optional[str] = None) -> ModelVersion:
        """Set description for dataset loader's ModelVersion entity."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_run(self, run_id: str) -> Run:
        """Get run by id."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_experiment_by_name(self, name: str) -> Optional[Experiment]:
        """Get experiment by experiment name from the backend store."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get experiment by experiment id from the backend store."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    # TODO after updating to a new version, the result is paginated
    # and needs to be converted to pagination scheme of our project.
    def search_model_versions(
        self,
        model_type: ModelType,
        filter_string: Optional[str] = None,
        max_results: int = 10000,
        order_by: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> PagedList[ModelVersion]:
        """Search for model versions in backend that satisfy the filter criteria."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def set_terminated(self, run_id: str, status: Optional[str] = None, end_time: Optional[int] = None) -> None:
        """Set a run’s status to terminated."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_model_version(self, name: str, version: int) -> ModelVersion:
        """Get model version by model name and version number."""
        return request_for_function(
            inspect.currentframe(),
            for_class=self.for_class,
        )

    def get_dataset_loader_version(self, name: str, version: int) -> ModelVersion:
        """Get dataset loader version by dataset loader name and version number."""
        return request_for_function(
            inspect.currentframe(),
            for_class=self.for_class,
        )

    def get_executor_version(self, name: str, version: int) -> ModelVersion:
        """Get executor version by executor name and version number."""
        return request_for_function(
            inspect.currentframe(),
            for_class=self.for_class,
        )

    def download_artifacts(self, run_id: str, path: str, dst_path: Optional[str] = None) -> str:
        """Download an artifact file or directory from a run to a local directory, and return a local path for it."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def download_job_artifacts(self, job_id: str, path: Optional[str] = "", dst_path: Optional[str] = None) -> str:
        """Download an artifact file or directory from a job to a local directory, and return a local path for it."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_model_version_requirements(self, name: str, version: int) -> list:
        """Download an artifact file and return list of requirements of the model."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_model_version_conda_env(self, name: str, version: int) -> dict:
        """Download an artifact file and return json file of conda environment."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_dataset_loader_version_requirements(self, name: str, version: int) -> list:
        """Download an artifact file and return list of requirements of the model."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_dataset_loader_version_conda_env(self, name: str, version: int) -> dict:
        """Download an artifact file and return json file of conda environment."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_executor_version_requirements(self, name: str, version: int) -> list:
        """Download an artifact file and return list of requirements of the model."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def get_executor_version_conda_env(self, name: str, version: int) -> dict:
        """Download an artifact file and return json file of conda environment."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )

    def search_runs(
        self,
        experiment_ids: Optional[List[str]] = None,
        filter_string: str = "",
        run_view_type: int = 1,
        max_results: int = 100000,
        order_by: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> PagedList[Run]:
        """Search experiments that fit the search criteria."""
        return request_for_function(
            inspect.currentframe(),
            extra_attrs=self.extra_attrs,
            for_class=self.for_class,
        )
