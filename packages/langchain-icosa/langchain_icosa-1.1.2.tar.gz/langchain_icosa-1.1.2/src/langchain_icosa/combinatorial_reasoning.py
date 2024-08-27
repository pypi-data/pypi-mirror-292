import inspect
from typing import Any, Dict, Iterator, List, Optional

import openai
import requests
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import Generation, GenerationChunk
from langchain_core.outputs.llm_result import LLMResult
from langchain_core.utils import convert_to_secret_str, get_from_dict_or_env
from pydantic.v1 import Field, SecretStr, root_validator
from requests.auth import HTTPBasicAuth

API_LICENSE = {
    "user": "langchainPackage",
    "pwd": "Uy2xfygkssbZdUlpp0CO1UXSuqRFv3mVSw5utrE94NU",
}

API_ENDPOINT = "https://cr-api.icosacomputing.com"


class CombinatorialReasoningLLM(LLM):
    """
    `Icosa Computing Combinatorial Reasoning LangChain API`

    To use, you must have a valid OpenAI API key that you either pass into the LLM
    or set in an environment variable called `OPENAI_API_KEY`.

    Although the actual compute is free of charge,
    the calls to OpenAI's `gpt-4o-mini` will be charged to your own account.

    Example:
        .. code-block:: python

            cr_llm = CombinatorialReasoningLLM(
                linearSensitivity=1.0,
                threshParam=0.0,
                riskParam=0.0,
                weight=1
            )

            print(cr_llm.invoke("Who solved the Riemann Hypothesis?", responseType='answerWithReasoning')
    """

    linear_sensitivity: float = 3.5341454578705958
    """Sets the relative scaling between the linear and the quadratic terms."""
    thresh_param: float = 2.4601753808001217
    """Shifts the center of the distribution of the quadratic variables."""
    risk_param: float = 0.38900003710737635
    """Shifts the linear terms according to their respective 'risk' factors."""
    weight: int = 2
    """Controls the integer encoding of each reason. Essentially a method to assign more importance to certain reasons."""
    openai_api_key: Optional[SecretStr] = Field(None, alias="openai_api_key")
    """API key for OpenAI service. Can also be passed in through an environment variable called `OPENAI_API_KEY`."""
    model: str = "gpt-4o-mini"
    """OpenAI model to use for text generation."""

    @root_validator()
    def validate(cls, values: dict[str, Any]) -> dict[str, Any]:

        # validate OpenAI key was passed in
        api_key = get_from_dict_or_env(values, "openai_api_key", "OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API key")

        # validate OpenAI key and model is valid
        with openai.OpenAI(
            api_key=(
                api_key.get_secret_value()
                if isinstance(api_key, SecretStr)
                else api_key
            )
        ) as client:
            try:
                client.models.list()
            except openai.AuthenticationError:
                raise ValueError("Provided OpenAI API key is invalid")

            try:
                client.models.retrieve(values["model"])
            except openai.NotFoundError:
                raise ValueError("Provided OpenAI model does not exist")

        values["openai_api_key"] = convert_to_secret_str(api_key)

        # validate API endpoint
        response = requests.get(
            f"{API_ENDPOINT}/account",
            auth=HTTPBasicAuth(API_LICENSE["user"], API_LICENSE["pwd"]),
        )

        response.raise_for_status()

        return values

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""
        generations = []
        distinct_reasons_list = []
        selected_reasons_list = []
        sampled_reasons_flat_list = []
        sampled_reasons_matrix_list = []

        new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")

        for prompt in prompts:

            llm_result = (
                self._get_llm_result(
                    prompt, stop=stop, run_manager=run_manager, **kwargs
                )
                if new_arg_supported
                else self._get_llm_result(prompt, stop=stop, **kwargs)
            )

            text = llm_result["text"]
            distinct_reasons = llm_result["distinctReasons"]
            selected_reasons = llm_result["selectedReasons"]
            sampled_reasons_flat = llm_result["sampledReasonsFlat"]
            sampled_reasons_matrix = llm_result["sampledReasonsMatrix"]

            generations.append([Generation(text=text)])
            distinct_reasons_list.append(distinct_reasons)
            selected_reasons_list.append(selected_reasons)
            sampled_reasons_matrix_list.append(sampled_reasons_matrix)
            sampled_reasons_flat_list.append(sampled_reasons_flat)
        return LLMResult(
            generations=generations,
            llm_output={
                "distinct_reasons": distinct_reasons_list,
                "selected_reasons": selected_reasons_list,
                "sampled_reasons_flat": sampled_reasons_flat_list,
                "sampled_reasons_matrix": sampled_reasons_matrix_list,
            },
        )

    def _get_llm_result(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Calls the API and returns the LLM result

        Args:
            prompt: the prompt to pass to the LLM.
            stop: an optional stop word to use. Currently, only one stop word is supported.
            run_manager: A callback manager for the LLM run.
            **kwargs: Arbitrary keyword arguments
        Returns:
            A dictionary containing the answer, distinct reasons generated, and final selected reasons
        """
        responseType = kwargs.get("responseType", "answer")
        if responseType not in {"answer", "answerWithReasoning"}:
            raise ValueError(
                f"Response Type {responseType} not supported. Must be 'answer' or 'answerWithReasoning'"
            )

        params = {
            "prompt": prompt,
            "apiKey": self.openai_api_key.get_secret_value(),
            "model": self.model,
        }

        if stop is not None:
            if len(stop) > 1:
                raise ValueError("LLM only supports a maximum of one stop token.")
            params["stop"] = stop

        if "seed" in kwargs:
            params["seed"] = kwargs["seed"]

        hyperparams = {
            "linearSensitivity": kwargs.get(
                "linearSensitivity", self.linear_sensitivity
            ),
            "threshParam": kwargs.get("threshParam", self.thresh_param),
            "riskParam": kwargs.get("riskParam", self.risk_param),
            "weight": kwargs.get("weight", self.weight),
        }

        params.update(hyperparams)

        response = requests.post(
            f"{API_ENDPOINT}/cr/solve_post",
            json=params,
            auth=HTTPBasicAuth(API_LICENSE["user"], API_LICENSE["pwd"]),
        )

        if response.status_code == 400:
            print(response.json()["detail"])

        response.raise_for_status()

        result = {
            "text": response.json()[responseType],
            "distinctReasons": response.json()["initialReasons"],
            "selectedReasons": response.json()["finalReasons"],
            "sampledReasonsMatrix": response.json()["sampledReasonsMatrix"],
            "sampledReasonsFlat": response.json()["sampledReasonsFlat"],
        }

        return result

    # The abstract method must be implemented,
    # even though we do not need it.
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        pass

    @property
    def _llm_type(self) -> str:
        return "CombinatorialReasoningLLM"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": "CombinatorialReasoningLLM",
            "linear_sensitivity": self.linear_sensitivity,
            "thresh_param": self.thresh_param,
            "risk_param": self.risk_param,
            "weight": self.weight,
            "model": self.model,
        }

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """
        Enables final answer to be streamed as tokens are generated.

        This method does not support streaming different response types or selected reasons.

        Args:
            prompt (str): The prompt to pass to the LLM.
            stop (Optional[List[str]]): The stop word to use. Defaults to None. Currently, only one stop token is supported.
            run_manager (Optional[CallbackManagerForLLMRun]): The callback manager for the LLM run. Defaults to None.
            **kwargs: Arbitary keyword arguments.

        Yields:
            An iterator of generation chunks.
            In test mode, this returns the original prompt as an iterator of generation chunks
        """

        params = {
            "prompt": prompt,
            "apiKey": self.openai_api_key.get_secret_value(),
            "model": self.model,
        }

        if stop is not None:
            if len(stop) > 1:
                raise ValueError("LLM only supports a maximum of one stop token.")
            params["stop"] = stop

        if "seed" in kwargs:
            params["seed"] = kwargs["seed"]

        hyperparams = {
            "linearSensitivity": kwargs.get(
                "linearSensitivity", self.linear_sensitivity
            ),
            "threshParam": kwargs.get("threshParam", self.thresh_param),
            "riskParam": kwargs.get("riskParam", self.risk_param),
            "weight": kwargs.get("weight", self.weight),
        }

        params.update(hyperparams)

        with requests.post(
            f"{API_ENDPOINT}/cr/stream_post",
            json=params,
            auth=HTTPBasicAuth(API_LICENSE["user"], API_LICENSE["pwd"]),
            stream=True,
        ) as response:
            if response.status_code == 400:
                print(response.json()["detail"])
            response.raise_for_status()
            for token in response.iter_content(decode_unicode=True):
                if token:
                    chunk = GenerationChunk(text=token)
                    if run_manager:
                        run_manager.on_llm_new_token(token=token, chunk=chunk)
                    yield chunk


class CombinatorialReasoningCallbackHandler(BaseCallbackHandler):
    """
    Callback for Combinatorial Reasoning LLM
    """

    def __init__(self) -> None:
        super().__init__()
        self.data = None
        self.stats = None

    def on_llm_end(self, response: LLMResult, **kwargs) -> Any:
        self.data = response.llm_output

        if self.data:
            self.stats = []
            for distinct_reasons, selected_reasons in zip(
                self.data["distinct_reasons"], self.data["selected_reasons"]
            ):
                self.stats.append(
                    {
                        "num_distinct_reasons": len(distinct_reasons),
                        "num_selected_reasons": len(selected_reasons),
                        "proportion_selected": (
                            len(selected_reasons) / len(distinct_reasons)
                            if len(distinct_reasons) > 0
                            else None
                        ),
                    }
                )
