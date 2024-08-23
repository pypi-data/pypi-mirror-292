"""Delete a model training run"""

import warnings
from typing import Any, Dict, List, Optional, Union

from databricks.model_training.api.engine import get_return_response, run_plural_mapi_request
from databricks.model_training.api.exceptions import DatabricksModelTrainingRequestError
from databricks.model_training.types import TrainingRun

QUERY_FUNCTION = 'deleteFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
QUERY = f"""
mutation DeleteFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    id
    name
    status
    createdById
    createdByEmail
    createdAt
    updatedAt
    startedAt
    completedAt
    reason
    isDeleted
  }}
}}"""


def delete(
    runs: Optional[Union[str, TrainingRun, List[str], List[TrainingRun]]] = None,
    experiment_id: Optional[str] = None,
) -> int:
    """
    [DEPRECATED] Cancel and delete a training run, list of training runs, or all runs under a single 
    MLflow experiment id. If the run does not exist, an error will be raised.

    Args:
        runs (``Optional[List[str] | List[``:class:`~databricks.model_training.types.training_run.TrainingRun` ``]]``):
            A list of runs or training_run names to stop. Using 
            :class:`~databricks.model_training.types.training_run.TrainingRun` objects is most efficient. 
            See the note below.
        experiment_id (``Optional[str]``): The MLflow ID of the experiment to stop.
        reason (``Optional[str]``): A reason for stopping the finetune run
        timeout (``Optional[float]``): Time, in seconds, in which the call should complete.
            If the call takes too long, a :exc:`~concurrent.futures.TimeoutError`
            will be raised. If ``future`` is ``True``, this value will be ignored.
        future (``bool``): Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to :func:`delete` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the list of :class:`~databricks.model_training.types.training_run.TrainingRun` output,
            use ``return_value.result()`` with an optional ``timeout`` argument.

    Raises:
        DatabricksGenAIError: Raised if stopping any of the requested runs failed

    Returns: Int representing the number of runs that were successfully deleted
    """
    warnings.simplefilter("once", DeprecationWarning)
    warnings.warn(
        "The 'foundation_model.delete' function will be deprecated in a future release. "
        "Please use 'foundation_model.cancel' to cancel runs instead.", DeprecationWarning)

    if not (runs or experiment_id):
        raise DatabricksModelTrainingRequestError('Must provide training run(s) or MLflow experiment ID to delete')

    if runs and experiment_id:
        raise DatabricksModelTrainingRequestError(
            'Cannot provide both training run(s) and MLflow experiment ID to delete')

    filters = {}

    if experiment_id:
        filters['mlflowExperimentId'] = {'equals': experiment_id}
        delete_msg = 'MLflow experiment ID'
    else:
        runs_list: List[Union[str, TrainingRun]] = [runs] if isinstance(runs,
                                                                        (str, TrainingRun)) else runs  # pyright: ignore

        # Extract run names
        training_run_names = [r if isinstance(r, str) else r.name for r in runs_list]

        filters = {}
        if training_run_names:
            filters['name'] = {'in': training_run_names}

        delete_msg = 'training run(s)'

    variables: Dict[str, Dict[str, Any]] = {VARIABLE_DATA_NAME: {'filters': filters}}

    try:
        response = run_plural_mapi_request(
            query=QUERY,
            query_function=QUERY_FUNCTION,
            return_model_type=TrainingRun,
            variables=variables,
        )

        return len(get_return_response(response))

    except Exception as e:
        raise DatabricksModelTrainingRequestError(
            f'Failed to delete {delete_msg} {runs if runs else experiment_id}. Please make sure the run \
                                                  has not completed or failed and try again.') from e
