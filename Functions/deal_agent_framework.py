import os
import sys
import logging
import json
from typing import List, Optional
from twilio.rest import Client  # 用于发送通知（虽然在这段代码中未用到）
from dotenv import load_dotenv  # 加载 .env 文件中的环境变量，比如 API 密钥
import chromadb  # 向量数据库，用于嵌入存储和相似度查询
from agents.planning_agent import PlanningAgent  # 智能体类，用于生成产品推荐等决策
from agents.deals import Opportunity  # 表示一个商品机会的数据结构
from sklearn.manifold import TSNE  # 用于降维（例如可视化 embedding）
import numpy as np  # 数值处理库

# 日志输出颜色控制（终端美化）
BG_BLUE = '\033[44m'
WHITE = '\033[37m'
RESET = '\033[0m'

# 类别与对应颜色（用于产品分类可视化）
CATEGORIES = ['Appliances', 'Automotive', 'Cell_Phones_and_Accessories', 'Electronics','Musical_Instruments', 'Office_Products', 'Tools_and_Home_Improvement', 'Toys_and_Games']
COLORS = ['red', 'blue', 'brown', 'orange', 'yellow', 'green' , 'purple', 'cyan']

# 初始化日志系统：设置输出格式和等级
def init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)  # 输出到终端
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [Agents] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

# 主框架类，负责加载记忆、连接向量数据库、管理智能体和执行任务
class DealAgentFramework:

    DB = "products_vectorstore"  # 向量数据库路径
    MEMORY_FILENAME = "memory.json"  # 本地记忆文件，用于记录已处理的机会

    def __init__(self):
        init_logging()  # 设置日志输出格式
        load_dotenv()  # 加载环境变量
        client = chromadb.PersistentClient(path=self.DB)  # 初始化向量数据库
        self.memory = self.read_memory()  # 读取之前记录的机会列表
        self.collection = client.get_or_create_collection('products')  # 获取或创建 'products' 向量集合
        self.planner = None  # 智能体初始化为空，按需加载

    # 按需初始化智能体，只初始化一次
    def init_agents_as_needed(self):
        if not self.planner:
            self.log("Initializing Agent Framework")
            self.planner = PlanningAgent(self.collection)  # 启动智能规划代理，并传入向量集合
            self.log("Agent Framework is ready")
        
    # 从本地文件读取 memory.json 中的历史机会
    def read_memory(self) -> List[Opportunity]:
        if os.path.exists(self.MEMORY_FILENAME):
            with open(self.MEMORY_FILENAME, "r") as file:
                data = json.load(file)
            opportunities = [Opportunity(**item) for item in data]  # 反序列化为 Opportunity 对象
            return opportunities
        return []

    # 将当前内存中的机会写入本地 memory.json 文件（持久化）
    def write_memory(self) -> None:
        data = [opportunity.dict() for opportunity in self.memory]  # 转换为 JSON 可存储格式
        with open(self.MEMORY_FILENAME, "w") as file:
            json.dump(data, file, indent=2)

    # 日志输出函数，带颜色标识“Agent Framework”模块
    def log(self, message: str):
        text = BG_BLUE + WHITE + "[Agent Framework] " + message + RESET
        logging.info(text)

    # 主运行函数：负责调用智能体进行计划决策，并更新记忆
    def run(self) -> List[Opportunity]:
        self.init_agents_as_needed()  # 确保智能体已加载
        logging.info("Kicking off Planning Agent")
        result = self.planner.plan(memory=self.memory)  # 调用 plan 函数，传入当前机会作为上下文
        logging.info(f"Planning Agent has completed and returned: {result}")
        if result:
            self.memory.append(result)  # 记录新机会
            self.write_memory()  # 保存到本地
        return self.memory

    # 可视化函数：获取降维后的嵌入数据用于 3D 可视化（如 t-SNE）
    @classmethod
    def get_plot_data(cls, max_datapoints=10000):
        client = chromadb.PersistentClient(path=cls.DB)
        collection = client.get_or_create_collection('products')  # 再次访问向量集合
        result = collection.get(include=['embeddings', 'documents', 'metadatas'], limit=max_datapoints)  # 取出数据
        vectors = np.array(result['embeddings'])  # 向量矩阵
        documents = result['documents']  # 原始文本
        categories = [metadata['category'] for metadata in result['metadatas']]  # 提取分类标签
        colors = [COLORS[CATEGORIES.index(c)] for c in categories]  # 分类映射为颜色
        tsne = TSNE(n_components=3, random_state=42, n_jobs=-1)  # 设置 t-SNE 降维器
        reduced_vectors = tsne.fit_transform(vectors)  # 执行降维
        return documents, reduced_vectors, colors  # 返回可用于 3D 可视化的数据

# 如果当前脚本直接运行（非被导入），执行 run()
if __name__=="__main__":
    DealAgentFramework().run()
