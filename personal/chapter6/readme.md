## 捆绑 Ollama 的 Open WebUI（一体式安装）模式下，必须要添加“-e OLLAMA_HOST=0.0.0.0“ 否则容器外部无法访问相关的API接口
docker run -d \
  -p 3000:8080 \
  -p 11434:11434 \
  --gpus=all \
  -v ollama:/root/.ollama \
  -v open-webui:/app/backend/data \
  -e OLLAMA_HOST=0.0.0.0 \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:ollama
