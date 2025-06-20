import os
import time
import json
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

BASE_URL =  os.getenv("HUAWEICLOUD_BASEURL", "default_value")

# 初始化 LLM
llm = ChatOpenAI(
    model="deepseek-r1:8b",
    openai_api_base=f"{BASE_URL}/v1",
    openai_api_key="ollama",
    temperature=0.7,
)

# 模拟工具实现
def search_web(query: str) -> str:
    """搜索互联网上的实时信息，例如流行趋势和用户评价。"""
    print(f"[Tool Call] 搜索网页：{query}")
    time.sleep(0.5)
    if "小红书美妆趋势" in query:
        return "近期流行：多巴胺穿搭、早C晚A护肤、伪素颜妆容。热门关键词有#氛围感、#抗老、#屏障修复。"
    elif "保湿面膜" in query:
        return "话题：沙漠干皮救星、熬夜急救、水光肌养成。用户痛点：卡粉、泛红、紧绷。"
    elif "深海蓝藻保湿面膜" in query:
        return "用户评价：补水效果佳，吸收快，适合敏感肌。价格略高但值得。"
    return "无特别搜索结果。"

def query_product_database(product_name: str) -> str:
    """查询产品信息，包括成分、功效、适用人群等。"""
    print(f"[Tool Call] 查询产品数据库：{product_name}")
    time.sleep(0.5)
    if "深海蓝藻保湿面膜" in product_name:
        return "含深海蓝藻提取物，富含多糖和氨基酸。深层补水、舒缓泛红，适合干敏肌，质地清爽。"
    return "未查询到该产品。"

def generate_emoji(context: str) -> str:
    """为内容匹配一组小红书风格的表情符号。"""
    print(f"[Tool Call] 生成表情符号：{context}")
    if any(k in context for k in ["保湿", "水润", "补水"]):
        return "💦 💧 🌊 ✨"
    if any(k in context for k in ["爱了", "惊喜", "回购"]):
        return "😍 💖 💯 🛍️"
    return "✨ 🔥 💖"

# 构造工具列表
tools = [
    Tool.from_function(search_web, name="search_web", description="搜索实时热门趋势"),
    Tool.from_function(query_product_database, name="query_product_database", description="查询产品数据库信息"),
    Tool.from_function(generate_emoji, name="generate_emoji", description="生成表情符号"),
]

# Prompt 定义
prompt = ChatPromptTemplate.from_template("""
你是一个资深的小红书爆款文案专家，擅长结合最新潮流和产品卖点，创作引人入胜、高互动的笔记文案。
你的任务是根据用户提供的产品，生成包含标题、正文、标签和表情的完整小红书爆款文案。
请始终采用 Thought → Action → Observation → Answer 模式进行推理。
如果需要获取趋势、成分或表情，请调用工具。
生成的文案风格需活泼、真诚、富有感染力。
当完成任务后，请以JSON格式直接输出最终文案，示例格式如下：
```json
{{
  "title": "小红书标题",
  "body": "正文内容",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["💦", "🔥", "💖"]
}}
```

问题描述：
{input}

{agent_scratchpad}
""")

# 创建 Agent 和执行器
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

import json
import re

def extract_json_from_text(text: str) -> dict:
    try:
        # 提取首个 JSON 块
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("未找到合法 JSON 内容")
    except Exception as e:
        return {"error": f"解析JSON失败: {e}"}

def generate_rednote(product_name: str, style: str = "活泼甜美") -> dict:
    
    query = f"请结合当前最新小红书流行趋势，为产品「{product_name}」生成一篇风格为「{style}」的小红书爆款文案，包含标题、正文、至少5个标签和表情，结果以JSON格式返回。"
    
    result = agent_executor.invoke({"input": query})

    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
    return extract_json_from_text(output_text)

    return result.get("output", result)

if __name__ == "__main__":
    print("小红书爆款文案生成器（DeepSeek-R1-8B）")
    print("输入格式：产品名称 文案风格（如：深海蓝藻面膜 活泼甜美）,退出请输入exit 或 quit")

    while True:
        try:
            user_input = input("\n请输入> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break

            if " " not in user_input:
                print("请同时输入产品名称和风格！")
                continue

            product, style = user_input.rsplit(" ", 1)
            print(f"\n🛠️ 正在为「{product}」生成「{style}」风格的文案...")

            start_time = time.time()
            result = generate_rednote(product, style)

            print(f"\n✅ 生成成功（耗时{time.time() - start_time:.1f}s）")
            print("\n--- JSON格式 ---")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"发生错误: {str(e)}")
