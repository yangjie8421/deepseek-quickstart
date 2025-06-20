import os
import json
import random
import time
from openai import OpenAI

BASE_URL =  os.getenv("HUAWEICLOUD_BASEURL", "default_value")

# 初始化Ollama客户端
client = OpenAI(
    base_url=f"{BASE_URL}/v1",
    api_key="ollama",  # Ollama不需要真实API Key
)

# 优化后的系统提示词
SYSTEM_PROMPT = """
你是一个资深的小红书爆款文案专家，擅长结合最新潮流和产品卖点，创作引人入胜、高互动、高转化的笔记文案。
你的任务是根据用户提供的产品和需求，生成包含标题、正文、相关标签和表情符号的完整小红书笔记。
请始终采用'Thought-Action-Observation'模式进行推理和行动。文案风格需活泼、真诚、富有感染力。当完成任务后，请以JSON格式直接输出最终文案，示例格式如下：
```json
{{
  "title": "小红书标题",
  "body": "小红书正文",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖"]
}}
```
在生成文案前，请务必先思考并收集足够的信息。'
"""

def generate_rednote(product_name: str, style: str = "活泼甜美", max_retries:int = 5) -> dict:
    
    """生成小红书文案"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请为产品「{product_name}」创作一篇{style}风格的小红书爆款文案，要求包含：\n1. 吸引人的标题\n2. 详细使用体验\n3. 5个相关标签\n4. 适当的表情符号"}
    ]
    
    retries = 0
    while retries < max_retries:  # 最大迭代次数
        retries = retries + 1
        print(f"第{retries}次迭代")

        response = client.chat.completions.create(
            model="deepseek-r1:8b",
            messages=messages,
            temperature=0.3,
            response_format={
                        'type': 'json_object'
                        }
        )
        
        return json.loads(response.choices[0].message.content)        
        
        # 不是最终结果，继续对话
        messages.append({"role": "assistant", "content": content})
    
    return {"error": "生成失败，请重试"}

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
            
            # 生成文案
            start_time = time.time()
            result = generate_rednote(product, style)
            
            if "error" in result:
                print(f"❌ 生成失败: {result['error']}")
                continue
                
            # 打印结果
            print(f"\n✅ 生成成功（耗时{time.time()-start_time:.1f}s）")
            print("\n--- JSON格式 ---")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"发生错误: {str(e)}")