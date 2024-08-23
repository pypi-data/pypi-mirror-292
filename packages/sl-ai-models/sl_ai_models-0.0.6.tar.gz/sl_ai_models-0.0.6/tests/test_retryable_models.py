from sl_ai_models.basic_model_interfaces.ai_model import AiModel
from sl_ai_models.basic_model_interfaces.retryable_model import RetryableModel
import asyncio
import pytest
from unittest.mock import Mock
from tests.models_to_test import ModelsToTest
from tests.ai_mock_manager import AiModelMockManager
import inspect
import logging
logger = logging.getLogger(__name__)

RETRYABLE_ERROR_MESSAGE = "Model must be Retryable"


@pytest.mark.parametrize(
    "subclass",
    ModelsToTest.RETRYABLE_LIST
)
def test_ai_model_successfully_retries(mocker: Mock, subclass: type[AiModel]) -> None:
    if not issubclass(subclass, RetryableModel):
        raise ValueError(RETRYABLE_ERROR_MESSAGE)

    AiModelMockManager.mock_ai_model_direct_call_with_2_errors_then_success(mocker, subclass)
    number_of_retries = 3

    model = subclass()
    model.allowed_tries = number_of_retries
    model_input = model._get_cheap_input_for_invoke()
    response = asyncio.run(model.invoke(model_input))
    assert response is not None


@pytest.mark.parametrize(
    "subclass",
    ModelsToTest.RETRYABLE_LIST
)
def test_errors_when_runs_out_of_tries(mocker: Mock, subclass: type[AiModel]) -> None:
    if not issubclass(subclass, RetryableModel):
        raise ValueError(RETRYABLE_ERROR_MESSAGE)

    AiModelMockManager.mock_ai_model_direct_call_with_2_errors_then_success(mocker, subclass)
    model = subclass()
    model.allowed_tries = 2 # It should run out of retries with the first 2 errors
    model_input = model._get_cheap_input_for_invoke()
    with pytest.raises(Exception):
        asyncio.run(model.invoke(model_input))


@pytest.mark.parametrize(
    "subclass",
    ModelsToTest.RETRYABLE_LIST
)
def test_raises_error_on_tries_setter_if_invalid(subclass: type[AiModel]) -> None:
    if not issubclass(subclass, RetryableModel):
        raise ValueError(RETRYABLE_ERROR_MESSAGE)

    model = subclass()

    with pytest.raises(ValueError):
        model.allowed_tries = -1

    with pytest.raises(ValueError):
        model.allowed_tries = 0

    try:
        model.allowed_tries = 1
    except Exception:
        pytest.fail("Should not raise error on positive allowed_tries")


@pytest.mark.parametrize(
    "subclass",
    ModelsToTest.RETRYABLE_LIST
)
def test_raises_error_on_tries_init_if_invalid(subclass: type[AiModel]) -> None:
    if not issubclass(subclass, RetryableModel):
        raise ValueError(RETRYABLE_ERROR_MESSAGE)

    init_params = inspect.signature(subclass.__init__).parameters
    allowed_tries_key = "allowed_tries"
    if allowed_tries_key in init_params:
        init_args_with_0_allowed_tries = {allowed_tries_key: 0}
        init_args_with_negative_allowed_tries = {allowed_tries_key: -1}
        init_args_with_positive_allowed_tries = {allowed_tries_key: 1}

        with pytest.raises(ValueError):
            subclass(**init_args_with_0_allowed_tries)

        with pytest.raises(ValueError):
            subclass(**init_args_with_negative_allowed_tries)

        try:
            subclass(**init_args_with_positive_allowed_tries)
        except Exception:
            pytest.fail("Should not raise error on positive allowed_tries")
    else:
        raise ValueError(f"{subclass.__name__} must have an allowed_tries parameter in its __init__")
