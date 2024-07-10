import json
import re
from typing import Dict, Any, List, Generator, Optional, Union
from core.interpreter.sse_code_runner import SSECodeRunner
from ..interpreter.data_summarizer import DataSummarizer
from .akshare_prompts import AksharePrompts
from ..llms.llm_factory import LLMFactory
from .akshare_retrieval_provider import AkshareRetrievalProvider


class StepsPlanManager:
    def __init__(self,max_retry: int= 8 , allow_yfinance: bool = False):
        self.llm_factory = LLMFactory()
        self.current_plan: Dict[str, Any] = {}
        self.step_vars: Dict[str, Any] = {}
        self.step_codes: Dict[int, str] = {}
        self.current_step_number: int = 0
        self.execution_results: List[Dict[str, Any]] = []
        self.llm_client = LLMFactory().get_instance()
        self.data_summarizer = DataSummarizer()
        self.retriever = AkshareRetrievalProvider()
        self.prompts = AksharePrompts()
        self.max_retry = max_retry
        self.allow_yfinance = allow_yfinance 
        self.is_plan_confirmed = False
        self.code_runner = SSECodeRunner()

    @property
    def total_steps(self) -> int:
        if self.current_plan=={}:
            return 0
        return len(self.current_plan.get("steps", []))

    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        if "query_summary" not in plan or "steps" not in plan:
            return False
        for step in plan["steps"]:
            if any(key not in step for key in ["step_number", "description", "type"]):
                return False
            if step["type"] not in ["data_retrieval", "data_analysis"]:
                return False
            if step["type"] == "data_retrieval" and "save_data_to" not in step:
                return False
            if step["type"] == "data_analysis" and "required_data" not in step:
                return False
        return True

    def create_plan(self, query: str) -> Generator[Dict[str, Any], None, None]:
        categories = self.retriever.get_categories()
        prompt = self.prompts.create_plan_prompt(query, categories)
        
        max_attempts = self.max_retry
        for attempt in range(max_attempts):
            plan_text = ""
            for chunk in self.llm_client.text_chat(prompt, is_stream=True):
                plan_text += chunk
                yield {"type": "plan", "content": chunk}
            
            try:
                plan = json.loads(plan_text)
                if self.validate_plan(plan):
                    self.current_plan = plan
                    yield {"type": "plan", "content": plan}
                    return
                else:
                    yield {"type": "error", "content": f"生成的计划格式不正确，正在重试（尝试 {attempt + 1}/{max_attempts}）"}
            except json.JSONDecodeError:
                yield {"type": "error", "content": f"生成的计划不是有效的 JSON，正在重试（尝试 {attempt + 1}/{max_attempts}）"}
        
        yield {"type": "error", "content": "无法生成有效的计划，请重新尝试。"}

    def modify_plan(self, query: str) -> Generator[Dict[str, Any], None, None]:
        prompt = self._create_modify_plan_prompt(query)
        plan_text = ""
        for chunk in self.llm_client.text_chat(prompt, is_stream=True):
            plan_text += chunk
            yield {"type": "plan", "content": chunk}
        
        try:
            self.current_plan = self._extract_json_from_text(plan_text)
            yield {"type": "plan", "content": self.current_plan}
            yield {"type": "message", "content": "计划修改完毕。请检查修改后的计划并输入'确认计划'来开始执行，或继续修改计划。"}
        except json.JSONDecodeError:
            yield {"type": "error", "content": "无法修改计划。请重试。"}

    def get_step_code(self, step: int) -> Optional[str]:
        return self.step_codes.get(step)

    def set_step_code(self, step: int, code: str) -> None:
        self.step_codes[step] = code

    def get_step_vars(self, var_name: str) -> Any:
        return self.step_vars.get(var_name)

    def set_step_vars(self, var_name: str, value: Any) -> None:
        self.step_vars[var_name] = value
        summary = self.data_summarizer.get_data_summary(value)
        self.step_vars[f"{var_name}_summary"] = summary

    def add_execution_result(self, step: int, result_type: str, result: Any) -> None:
        if not isinstance(result, str):
            raise TypeError(f"执行结果必须是字符串类型，但得到了 {type(result).__name__} 类型")
        self.execution_results.append({
            "step": step,
            "type": result_type,
            "result": result
        })

    def get_current_step(self) -> Dict[str, Any]:
        current_step = len(self.execution_results)
        if current_step < self.total_steps:
            return self.current_plan['steps'][current_step]
        return {}

    def is_plan_complete(self) -> bool:
        return len(self.execution_results) >= self.total_steps

    def get_plan_summary(self) -> str:
        return self.current_plan.get('query_summary', '未提供计划摘要')

    def _create_plan_prompt(self, query: str) -> str:
        categories = self.retriever.get_categories()
        return self.prompts.create_plan_prompt(query, categories)

    def _create_modify_plan_prompt(self, query: str) -> str:
        return self.prompts.modify_plan_prompt(query, self.current_plan)

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        raise json.JSONDecodeError("No valid JSON found in the text", text, 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_plan": self.current_plan,
            "step_vars": self.step_vars,
            "step_codes": self.step_codes,
            "total_steps": self.total_steps,
            "execution_results": self.execution_results
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], llm_client) -> 'StepsPlanManager':
        plan = cls(llm_client)
        plan.current_plan = data.get("current_plan", {})
        plan.step_vars = data.get("step_vars", {})
        plan.step_codes = data.get("step_codes", {})
        plan.total_steps = data.get("total_steps", 0)
        plan.execution_results = data.get("execution_results", [])
        return plan
    
    def modify_step_code(self, step: int, query: str) -> Generator[Dict[str, Any], None, None]:
        current_code = self.get_step_code(step)
        if not current_code:
            yield {"type": "error", "content": f"步骤 {step} 的代码不存在。"}
            return

        prompt = self.prompts.modify_step_code_prompt(current_code, query)
        modified_code = ""
        for chunk in self.llm_client.text_chat(prompt, is_stream=True):
            modified_code += chunk
            yield {"type": "code_modification_progress", "content": chunk}

        self.set_step_code(step, modified_code.strip())
        yield {"type": "message", "content": f"步骤 {step} 的代码已更新。"}
        yield {"type": "code", "content": f"更新后的代码：\n{modified_code.strip()}"}

    def generate_step_code(self, step: Dict[str, Any]) -> Generator[Union[Dict[str, Any], str], None, None]:
        if step['type'] == 'data_retrieval':
            yield from self._generate_data_retrieval_code(step)
        elif step['type'] == 'data_analysis':
            yield from self._generate_data_analysis_code(step)
        else:
            yield {"type": "error", "content": f"错误：未知的步骤类型 {step['type']}"}

    def _generate_data_retrieval_code(self, step: Dict[str, Any]) -> Generator[Union[Dict[str, Any], str], None, None]:
        category = step['data_category']
        
        # 从选定类别中选择函数
        selected_functions = yield from self._select_functions_from_category(step, category)
        
        # 生成代码
        function_docs = self.retriever.get_specific_doc(selected_functions)
        code_prompt = self.prompts.generate_code_for_functions_prompt(step, function_docs)

        extracted_code = ""
        for chunk in self.llm_client.text_chat(code_prompt, is_stream=True):
            yield {"type": "code_generation_progress", "content": chunk}
            extracted_code += chunk

        code = self._extract_code(extracted_code)
        yield code

    def _generate_data_analysis_code(self, step: Dict[str, Any]) -> Generator[Union[Dict[str, Any], str], None, None]:
        data_summaries = {
            data_var: self.get_step_vars(f"{data_var}_summary") or "数据摘要不可用"
            for data_var in step['required_data']
        }
        
        code_prompt = self.prompts.generate_data_analysis_code_prompt(step, data_summaries, self.allow_yfinance)

        full_code = ""
        for chunk in self.llm_client.text_chat(code_prompt, is_stream=True):
            yield {"type": "code_generation_progress", "content": chunk}
            full_code += chunk
        
        code = self._extract_code(full_code)
        yield code

    def fix_code(self, step: int, code: str, error: str) -> Generator[Dict[str, Any], None, None]:
        if not code:
            yield {"type": "error", "content": f"步骤 {step} 的代码不存在或为空。"}
            return

        fix_prompt = self.prompts.fix_code_prompt(code, error)
        fixed_code = ""
        for chunk in self.llm_client.text_chat(fix_prompt, is_stream=True):
            yield {"type": "code_fix_progress", "content": chunk}
            fixed_code += chunk
        
        fixed_code = self._extract_code(fixed_code)
        if fixed_code:
            yield {"type": "message", "content": f"步骤 {step} 的代码已修复。"}
            yield {"type": "code", "content": fixed_code}
        else:
            yield {"type": "error", "content": "未能生成有效的修复代码。"}

    def _select_functions_from_category(self, step: Dict[str, Any], category: str) -> Generator[List[str], None, None]:
        functions = self.retriever.get_functions([category])
        function_prompt = self.prompts.select_functions_from_category_prompt(step, functions[category])
        
        full_response = ""
        for chunk in self.llm_client.text_chat(function_prompt, is_stream=True):
            full_response += chunk
            yield {"type": "function_selection_progress", "content": chunk}

        selected_functions = [func.strip() for func in full_response.split(',')]
        yield {"type": "function_selection", "content": f"已选择函数：{', '.join(selected_functions)}"}
        return selected_functions

    def _extract_code(self, content: str) -> str:
        code_match = re.search(r'```python(.*?)```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        else:
            return content.strip()
        
    def step(self) -> Generator[Dict[str, Any], None, None]:
        if self.current_step_number >= self.total_steps:
            yield {"type": "message", "content": "所有步骤已完成。"}
            return

        current_step = self.get_current_step()
        yield {"type": "message", "content": f"执行步骤 {self.current_step_number + 1}: {current_step['description']}"}

        # 生成代码
        code_generator = self.generate_step_code(current_step)
        full_code = "".join(chunk for chunk in code_generator if isinstance(chunk, str))

        if not full_code:
            yield {"type": "error", "content": "未能生成有效的代码。"}
            return

        yield {"type": "code_generation", "content": full_code}

        # 执行代码
        for attempt in range(self.max_retry):
            try:
                if current_step['type'] == 'data_retrieval':
                    yield from self.execute_data_retrieval(full_code, current_step)
                elif current_step['type'] == 'data_analysis':
                    yield from self.execute_data_analysis(full_code, current_step)
                else:
                    raise Exception(f"未知的步骤类型: {current_step['type']}")

                self.set_step_code(self.current_step_number, full_code)
                yield {"type": "message", "content": f"步骤 {self.current_step_number + 1} 执行成功。"}
                break
            except Exception as e:
                if attempt < self.max_retry - 1:
                    yield {"type": "code_fix", "content": f"第 {attempt + 1} 次尝试失败。错误：{str(e)}。正在尝试修复代码。"}
                    fix_generator = self.fix_code(self.current_step_number, full_code, str(e))
                    new_code = ""
                    for chunk in fix_generator:
                        if chunk['type'] == 'code':
                            new_code = chunk['content']
                        yield chunk
                    if new_code:
                        full_code = new_code
                    else:
                        yield {"type": "error", "content": "未能生成修复后的代码。"}
                        break
                else:
                    yield {"type": "error", "content": f"在 {self.max_retry} 次尝试后仍无法执行代码。最后的错误：{str(e)}"}
                    break

        self.current_step_number += 1
        yield {"type": "debug", "content": f"当前步骤更新为: {self.current_step_number}"}

    def next_step(self):
        self.current_step_number += 1

    def execute_data_retrieval(self, code: str, step: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        yield {"type": "message", "content": "开始执行数据检索..."}

        global_vars = self.step_vars.copy()
        global_vars['llm_client'] = self.llm_factory.get_instance()
        global_vars['llm_factory'] = self.llm_factory

        try:
            updated_vars = None
            for event in self.code_runner.run_sse(code, global_vars):
                if event['type'] == 'output':
                    yield {"type": "code_execution", "content": event['content']}
                elif event['type'] == 'error':
                    yield {"type": "error", "content": f"执行代码时发生错误: {event['content']}"}
                    raise Exception(event['content'])
                elif event['type'] == 'variables':
                    updated_vars = event['content']
            
            if updated_vars is not None:
                if step['save_data_to'] in updated_vars:
                    data = updated_vars[step['save_data_to']]
                    self.set_step_vars(step['save_data_to'], data)
                    
                    # 生成数据摘要
                    summary = self.data_summarizer.get_data_summary(data)
                    self.set_step_vars(f"{step['save_data_to']}_summary", summary)
                    
                    yield {"type": "message", "content": f"数据已保存到 {step['save_data_to']}"}
                    yield {"type": "summary", "content": f"数据摘要: {summary}"}
                else:
                    error_msg = f"执行代码未产生预期的 '{step['save_data_to']}' 变量。可用变量: {list(updated_vars.keys())}"
                    yield {"type": "error", "content": error_msg}
                    raise Exception(error_msg)

            self.add_execution_result(step['step_number'], "data_retrieval", f"数据已保存到 {step['save_data_to']}")
            yield {"type": "message", "content": "数据检索成功完成。"}

        except Exception as e:
            yield {"type": "error", "content": f"数据检索失败: {str(e)}"}
            raise

    def execute_data_analysis(self, code: str, step: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        yield {"type": "message", "content": "开始执行数据分析..."}

        global_vars = self.step_vars.copy()
        global_vars['llm_client'] = self.llm_factory.get_instance()
        global_vars['llm_factory'] = self.llm_factory

        try:
            events = list(self.code_runner.run_sse(code, global_vars))
            
            for event in events:
                if event['type'] == 'output':
                    yield {"type": "code_execution", "content": event['content']}
                elif event['type'] == 'error':
                    yield {"type": "error", "content": f"执行代码时发生错误: {event['content']}"}
                    raise Exception(event['content'])

            updated_vars = next((event['content'] for event in events if event['type'] == 'variables'), None)
            
            if updated_vars is not None:
                if 'analysis_result' in updated_vars:
                    result = updated_vars['analysis_result']
                    
                    # 严格检查结果类型
                    if not isinstance(result, str):
                        error_msg = f"分析结果必须是字符串类型，但得到了 {type(result).__name__} 类型"
                        yield {"type": "error", "content": error_msg}
                        raise TypeError(error_msg)

                    self.set_step_vars(f"analysis_result_{step['step_number']}", result)
                    
                    yield {"type": "message", "content": "分析结果已生成"}
                    yield {"type": "analysis_result", "content": result}

                    self.add_execution_result(step['step_number'], "data_analysis", result)
                    yield {"type": "debug", "content": f"已添加执行结果: 步骤 {step['step_number']}, 类型 data_analysis"}
                else:
                    error_msg = f"执行代码未产生预期的 'analysis_result' 变量。可用变量: {list(updated_vars.keys())}"
                    yield {"type": "error", "content": error_msg}
                    raise Exception(error_msg)

            yield {"type": "message", "content": "数据分析成功完成。"}

        except Exception as e:
            yield {"type": "error", "content": f"数据分析失败: {str(e)}"}
            raise

    def reset(self):
        self.current_plan = {}
        self.step_vars = {}
        self.step_codes = {}
        self.current_step_number = 0
        self.execution_results = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_plan": self.current_plan,
            "step_vars": self.step_vars,
            "step_codes": self.step_codes,
            "current_step_number": self.current_step_number,
            "execution_results": self.execution_results
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepsPlanManager':
        manager = cls()
        manager.current_plan = data.get("current_plan", {})
        manager.step_vars = data.get("step_vars", {})
        manager.step_codes = data.get("step_codes", {})
        manager.current_step_number = data.get("current_step_number", 0)
        manager.execution_results = data.get("execution_results", [])
        return manager