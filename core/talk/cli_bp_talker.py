from typing import Generator, Union, Dict, Any
from ..llms.llm_factory import LLMFactory
from ..llms._llm_api_client import LLMApiClient
from ..planner.akshare_bp_planner import AkshareBPPlanner
from ._talker import Talker

class CliBpTalker(Talker):
    def __init__(self):
        factory = LLMFactory()
        self.llm_client: LLMApiClient = factory.get_instance()
        self.akshare_planner = AkshareBPPlanner()
        self.use_akshare = False
        self.session_id = ""

    def chat(self, message: str) -> Generator[Union[str, Dict[str, Any]], None, None]:
        if not self.use_akshare:
            # 只在第一次判断是否是金融数据查询
            self.use_akshare = self._is_financial_data_query(message)

        if self.use_akshare:
            # 如果已经确定使用AkshareBPPlanner，就继续使用它
            yield from self.akshare_planner.plan_chat(message)
        else:
            # 否则，继续使用LLM API响应
            yield from self.llm_client.text_chat(message, is_stream=True)

    def clear(self) -> None:
        self.llm_client.clear_chat()
        self.use_akshare = False  # 重置状态
        # 如果AkshareBPPlanner有清理方法，也应该在这里调用
        # self.akshare_planner.clear()

    def get_llm_client(self) -> LLMApiClient:
        return self.llm_client

    def set_llm_client(self, llm_client: LLMApiClient) -> None:
        self.llm_client = llm_client

    def _is_financial_data_query(self, query: str) -> bool:
        """
        使用LLM来判断查询是否与金融数据相关。
        """
        prompt = f"""请判断以下查询是否与金融数据（非金融知识）相关。财经新闻，经济新闻，市场舆情，情绪数据也属于金融数据。提及接口，API，akshare，tushare等金融接口，也属于金融数据相关
        只回答"是"或"否"。

        查询: {query}

        是否与金融数据相关？"""

        response = self.llm_client.one_chat(prompt)
        return "是" in response.lower()
    
    def set_session_id(self, session_id: str) -> None:
        self.session_id = session_id