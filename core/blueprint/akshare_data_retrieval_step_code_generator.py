from typing import Generator, Dict, Any

from core.blueprint.llm_provider import LLMProvider
from ._step_abstract import StepCodeGenerator, BaseStepModel
from .akshare_data_retrieval_step_model import AkShareDataRetrievalStepModel
from .llm_provider import LLMProvider
from ..planner.akshare_prompts import AksharePrompts
from ..rag.akshare_functions import AkshareFunctions
from ..planner.message import send_message
from ..akshare_doc import AKShareDataSingleton

class AkshareDataRetrievalStepCodeGenerator(StepCodeGenerator):
    def __init__(self, step_data: AkShareDataRetrievalStepModel):
        self.step_data = step_data
        self._step_code = ""
        self.llm_provider = LLMProvider()
        self.llm_client = self.llm_provider.new_llm_client()
        self.llms_cheap = self.llm_provider.new_cheap_client()
        self.retriever = AkshareFunctions()
        self.prompts = AksharePrompts()
        self.akshare_docs = AKShareDataSingleton()

    def gen_step_code(self) -> Generator[Dict[str, Any], None, None]:
        selected_functions = self.step_data.selected_functions
        function_docs = self.akshare_docs.get_specific_doc(selected_functions)
        
        if "required_data" in self.step_data.model_dump():
            data_summaries = {
                data_var: self.step_data.model_dump().get(f"{data_var}_summary", "数据摘要不可用")
                for data_var in self.step_data.required_data
            }
            code_prompt = self.prompts.generate_enhanced_code_for_data_retrieval_prompt(
                self.step_data.model_dump(), function_docs, data_summaries
            )
        else:
            code_prompt = self.prompts.generate_code_for_functions_prompt(
                self.step_data.model_dump(), function_docs
            )

        for chunk in self.llm_client.text_chat(code_prompt, is_stream=True):
            yield send_message(chunk, "code")
            self._step_code += chunk

        self._step_code = self._extract_code(self._step_code)
        yield send_message(self._step_code, "full_code")

    def fix_code(self, error: str) -> Generator[str, None, None]:
        if not self._step_code:
            yield send_message("没有可修复的代码。", "error")
            return

        fix_prompt = self.prompts.fix_code_prompt(self._step_code, error)
        
        fixed_code = ""
        for chunk in self.llm_client.text_chat(fix_prompt, is_stream=True):
            yield send_message(chunk, "code")
            fixed_code += chunk
        
        self._step_code = self._extract_code(fixed_code)
        yield send_message(f"代码已修复。")
        yield send_message(self._step_code, "code")

    def _extract_code(self, content: str) -> str:
        import re
        code_match = re.search(r'```python(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        else:
            return content.strip()

    def pre_enhancement(self) -> Generator[str, None, None]:
        pass

    def post_enhancement(self) -> Generator[str, None, None]:
        pass

    @property
    def step_code(self) -> str:
        return self._step_code