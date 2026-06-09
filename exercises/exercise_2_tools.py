"""Bài tập 2: Thêm tools và knowledge base.

Hoàn thành bài tập bằng cách:
1. Thêm một knowledge base entry về luật lao động Việt Nam.
2. Tạo tool kiểm tra thời hiệu khởi kiện.
3. Cho LLM dùng cả hai tool để trả lời.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from common.llm import get_llm


LEGAL_KNOWLEDGE = [
    {
        "id": "ucc_breach",
        "keywords": ["breach", "contract", "remedies", "damages", "ucc"],
        "text": (
            "Under the Uniform Commercial Code (UCC) Article 2, remedies for breach of contract "
            "include expectation damages, consequential damages, specific performance, and cover "
            "damages. Statute of limitations is typically 4 years (UCC § 2-725)."
        ),
    },
    {
        "id": "labor_law",
        "keywords": ["lao động", "sa thải", "hợp đồng lao động", "chấm dứt", "labor", "termination"],
        "text": (
            "Theo Bộ luật Lao động Việt Nam 2019, người sử dụng lao động chỉ được đơn phương "
            "chấm dứt hợp đồng lao động khi có căn cứ hợp pháp và tuân thủ thời hạn báo trước. "
            "Nếu chấm dứt trái luật, người lao động có thể yêu cầu được nhận lại làm việc, "
            "được trả lương và bảo hiểm cho thời gian không được làm việc, đồng thời được "
            "bồi thường theo quy định."
        ),
    },
]


@tool
def search_legal_knowledge(query: str) -> str:
    """Tìm kiếm trong knowledge base pháp lý."""
    query_lower = query.lower()
    for entry in LEGAL_KNOWLEDGE:
        if any(kw in query_lower for kw in entry["keywords"]):
            return f"[{entry['id']}] {entry['text']}"
    return "Không tìm thấy thông tin liên quan."


@tool
def check_statute_of_limitations(case_type: str) -> str:
    """Kiểm tra thời hiệu khởi kiện theo loại vụ án.

    Args:
        case_type: Loại vụ án, ví dụ contract, tort, property, labor.
    """
    limits = {
        "contract": "4 năm đối với nhiều tranh chấp hợp đồng mua bán hàng hóa theo UCC § 2-725.",
        "tort": "Thường khoảng 2-3 năm tùy từng bang hoặc hệ thống pháp luật áp dụng.",
        "property": "Thường khoảng 5 năm, tùy loại tranh chấp và pháp luật áp dụng.",
        "labor": "Tranh chấp lao động cá nhân ở Việt Nam thường có thời hiệu 1 năm từ ngày phát hiện quyền lợi bị xâm phạm.",
    }
    case_type_lower = case_type.lower()
    for key, value in limits.items():
        if key in case_type_lower:
            return value
    return "Không xác định. Hãy nhập contract, tort, property hoặc labor."


async def main():
    load_dotenv()
    llm = get_llm()

    tools = [search_legal_knowledge, check_statute_of_limitations]
    llm_with_tools = llm.bind_tools(tools)

    question = "Thời hiệu khởi kiện vụ vi phạm hợp đồng là bao lâu?"

    messages = [
        SystemMessage(content="Bạn là chuyên gia pháp lý. Sử dụng tools để tra cứu thông tin."),
        HumanMessage(content=question),
    ]

    print(f"Câu hỏi: {question}\n")

    response = await llm_with_tools.ainvoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            print(f"Gọi tool: {tool_call['name']}")
            tool_result = None

            if tool_call["name"] == "search_legal_knowledge":
                tool_result = search_legal_knowledge.invoke(tool_call["args"])
            elif tool_call["name"] == "check_statute_of_limitations":
                tool_result = check_statute_of_limitations.invoke(tool_call["args"])

            if tool_result:
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

        final_response = await llm_with_tools.ainvoke(messages)
        print(f"\nKết quả:\n{final_response.content}")
    else:
        print(f"\nKết quả:\n{response.content}")


if __name__ == "__main__":
    asyncio.run(main())
