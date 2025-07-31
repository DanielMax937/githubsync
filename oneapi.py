import os
# 如果你的 One API 不需要 API Key，可以忽略这一行或将其设置为空字符串
# 这里的 key 取决于你的 One API 配置，可能是 Google Key，也可能是 One API 自己的 key
# 建议将 key 存储在环境变量中
from dotenv import load_dotenv
load_dotenv() # 如果使用 .env 文件存储 key

from openai import OpenAI

# 配置 OpenAI 客户端
# 这里的 base_url 指向你的 One API 的地址和端口，通常是 /v1 结尾
# 例如：http://localhost:3000/v1
# 你需要将 'YOUR_ONE_API_BASE_URL' 替换为你实际的 One API 地址
# 你也可能需要设置 API Key，这取决于你的 One API 配置
client = OpenAI(
    api_key=os.environ.get('ONE_API_KEY'),
    base_url=os.environ.get('BASE_URL') # 或者直接写你的 Key，但不推荐
)

# 更简洁的方式是使用环境变量
# 设置环境变量:
# export OPENAI_API_BASE="YOUR_ONE_API_BASE_URL"
# export OPENAI_API_KEY="YOUR_ONE_API_KEY" # 如果需要

# client = OpenAI() # 如果设置了 OPENAI_API_BASE 和 OPENAI_API_KEY 环境变量，直接这样初始化即可

try:
    # 调用聊天完成 API
    # 这里的 model 名称 (e.g., "gemini-pro") 必须是你在 One API 中配置的、
    # 映射到 Google 模型的名称
    response = client.chat.completions.create(
        model="gemini-2.5-flash-preview-04-17",  # 替换为你 One API 中配置的 Google 模型名称
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好，请问你是什么模型？"}
        ]
    )
    # 打印助手的回复
    if response.choices and response.choices[0].message:
        print("Assistant:", response.choices[0].message.content)
    else:
        print("No response from the model.")

except Exception as e:
    print(f"An error occurred: {e}")
    # 根据错误信息检查 One API 服务是否正常、API Key 是否正确、模型名称是否正确等