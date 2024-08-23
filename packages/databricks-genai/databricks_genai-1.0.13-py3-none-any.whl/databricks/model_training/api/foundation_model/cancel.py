"""Cancel a model training run"""

from typing import Any, Dict, List, Optional, Union

from databricks.model_training.api.engine import get_return_response, run_plural_mapi_request
from databricks.model_training.api.exceptions import DatabricksModelTrainingRequestError
from databricks.model_training.types.training_run import TrainingRun

QUERY_FUNCTION = 'stopFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
OPTIONAL_DATA_NAME = 'stopFinetunesData'
QUERY = f"""
mutation StopFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!, ${OPTIONAL_DATA_NAME}: StopFinetunesInput) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}, {OPTIONAL_DATA_NAME}: ${OPTIONAL_DATA_NAME}) {{
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


def cancel(
    runs: Optional[Union[str, TrainingRun, List[str], List[TrainingRun]]] = None,
    experiment_id: Optional[str] = None,
) -> int:
    """
    Cancel a training run, list of training runs, or all runs under a single MLflow experiment id without 
    deleting them. If the run does not exist or if the run has already terminated, an error will be raised.

    Args:
        runs (Optional[Union[str, TrainingRun, List[str], List[TrainingRun]]]): The
            training run(s) to cancel. Can be a single run or a list of runs.
        experiment_id (Optional[str]): The MLflow experiment ID to cancel by.  
            This will cancel all training runs under the given experiment.

    Raises:
        DatabricksModelTrainingRequestError: Raised if stopping any of the requested runs failed

    Returns:
        int: The number of training runs cancelled
    """

    if not (runs or experiment_id):
        raise DatabricksModelTrainingRequestError('Must provide training run(s) or MLflow experiment ID to cancel')

    if runs and experiment_id:
        raise DatabricksModelTrainingRequestError(
            'Cannot provide both training run(s) and MLflow experiment ID to cancel. Please specify one or the other.')

    filters = {}

    if experiment_id:
        filters['mlflowExperimentId'] = {'equals': experiment_id}
        cancel_msg = 'MLflow experiment ID'
    else:
        runs_list: List[Union[str, TrainingRun]] = [runs] if isinstance(runs,
                                                                        (str, TrainingRun)) else runs  # pyright: ignore

        # Extract run names
        training_run_names = [r if isinstance(r, str) else r.name for r in runs_list]

        filters = {}
        if training_run_names:
            filters['name'] = {'in': training_run_names}

        cancel_msg = 'training run(s)'

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
            f'Failed to cancel {cancel_msg} {runs if runs else experiment_id}. Please make sure the run \
                                                  has not completed or failed and try again.') from e
