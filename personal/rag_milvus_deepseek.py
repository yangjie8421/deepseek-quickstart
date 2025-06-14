import os
from openai import OpenAI
from glob import glob
from pymilvus import model as milvus_model
from pymilvus import MilvusClient
from tqdm import tqdm

#因本地windows环境无法安装Milvus数据库，采用了远程服务器安装
milvus_client = MilvusClient("http://192.168.1.175:19530")

# 创建相关collection
collection_name = "my_rag_collection"
if milvus_client.has_collection(collection_name):
    milvus_client.drop_collection(collection_name)

from pymilvus import model as milvus_model
embedding_model = milvus_model.DefaultEmbeddingFunction()

test_embedding = embedding_model.encode_queries(["This is a test"])[0]
embedding_dim = len(test_embedding)

milvus_client.create_collection(
    collection_name=collection_name,
    dimension=embedding_dim,
    metric_type="IP",  # 内积距离
    consistency_level="Strong",  # 
)

# 读取相关文件，相关文档放在了项目上一级目录
text_lines = []
for file_path in glob("../../milvusdocs/faq/*.md", recursive=True):
    with open(file_path, "r") as file:
        file_text = file.read()

    text_lines += file_text.split("# ")

# 读取民法典
with open("./民法典节选.txt","r",encoding="utf-8") as file:
    file_text = file.read()

text_lines += file_text.split("\n")

# 把数据存到向量数据库
data = []
doc_embeddings = embedding_model.encode_documents(text_lines)

for i, line in enumerate(tqdm(text_lines, desc="Creating embeddings")):
    data.append({"id": i, "vector": doc_embeddings[i], "text": line})

milvus_client.insert(collection_name=collection_name, data=data)


print("question1:How is data stored in milvus?")
question = "How is data stored in milvus?"

search_res = milvus_client.search(
    collection_name=collection_name,
    data=embedding_model.encode_queries(
        [question]
    ),  # 将问题转换为嵌入向量
    limit=5,  # 返回前5个结果
    search_params={"metric_type": "IP", "params": {}},  # 内积距离
    output_fields=["text"],  # 返回 text 字段
)

import json

retrieved_lines_with_distances = [
    (res["entity"]["text"], res["distance"]) for res in search_res[0]
]
print(json.dumps(retrieved_lines_with_distances, indent=4))


print("question2:基本规定")
question = "基本规定"
search_res = milvus_client.search(
    collection_name=collection_name,
    data=embedding_model.encode_queries(
        [question]
    ),  # 将问题转换为嵌入向量
    limit=5,  # 返回前5个结果
    search_params={"metric_type": "IP", "params": {}},  # 内积距离
    output_fields=["text"],  # 返回 text 字段
)
retrieved_lines_with_distances = [
    (res["entity"]["text"], res["distance"]) for res in search_res[0]
]
print(json.dumps(retrieved_lines_with_distances, indent=4,ensure_ascii=False))
