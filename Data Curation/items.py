from typing import Optional
from transformers import AutoTokenizer
import re

BASE_MODEL = "meta-llama/Meta-Llama-3.1-8B"

MIN_TOKENS = 150 # Any less than this, and we don't have enough useful content
MAX_TOKENS = 160 # Truncate after this many tokens. Then after adding in prompt text, we will get to around 180 tokens

MIN_CHARS = 300
CEILING_CHARS = MAX_TOKENS * 7

class Item:
    """
    An Item is a cleaned, curated datapoint of a Product with a Price
    """
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    PREFIX = "Price is $"
    QUESTION = "How much does this cost to the nearest dollar?"
    REMOVALS = ['"Batteries Included?": "No"', '"Batteries Included?": "Yes"', '"Batteries Required?": "No"', '"Batteries Required?": "Yes"', "By Manufacturer", "Item", "Date First", "Package", ":", "Number of", "Best Sellers", "Number", "Product "]

    title: str
    price: float
    category: str
    token_count: int = 0
    details: Optional[str]
    prompt: Optional[str] = None
    include = False

    def __init__(self, data, price):
        self.title = data['title']
        self.price = price
        self.parse(data)

    def scrub_details(self):
        """
        Clean up the details string by removing common text that doesn't add value
        """
        details = self.details
        for remove in self.REMOVALS:
            details = details.replace(remove, "")
        return details

    def scrub(self, stuff):
        """
        Clean up the provided text by removing unnecessary characters and whitespace
        Also remove words that are 7+ chars and contain numbers, as these are likely irrelevant product numbers
        """
        stuff = re.sub(r'[:\[\]"{}【】\s]+', ' ', stuff).strip()
        stuff = stuff.replace(" ,", ",").replace(",,,",",").replace(",,",",")
        words = stuff.split(' ')
        select = [word for word in words if len(word)<7 or not any(char.isdigit() for char in word)]
        return " ".join(select)
    
    def parse(self, data):
        """
        Parse this datapoint and if it fits within the allowed Token range,
        then set include to True
        """
    
        # 将数据中的描述（一个字符串列表）合并为一个大字符串，每行之间用换行符连接
        contents = '\n'.join(data['description'])
    
        # 如果 description 非空，则在末尾添加一个换行符，便于后续拼接
        if contents:
            contents += '\n'
    
        # 将 features 字段（同样是一个字符串列表）合并成一段文本
        features = '\n'.join(data['features'])
    
        # 如果 features 非空，拼接到 contents 上，并添加换行符
        if features:
            contents += features + '\n'
    
        # 保存原始 details 字段到对象属性中，可能是未清洗的原始文本
        self.details = data['details']
    
        # 如果 details 非空，调用 scrub_details 对其进行清洗，并拼接到 contents 中
        if self.details:
            contents += self.scrub_details() + '\n'
    
        # 如果最终合并的内容超过最小字符数要求（MIN_CHARS）
        if len(contents) > MIN_CHARS:
            # 截断内容，防止过长，保留前 CEILING_CHARS 个字符
            contents = contents[:CEILING_CHARS]
    
            # 将标题和正文内容分别清洗，然后拼接为最终的 text
            text = f"{self.scrub(self.title)}\n{self.scrub(contents)}"
    
            # 使用 tokenizer 编码成 tokens，不加特殊标记
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
    
            # 如果 token 数量超过 MIN_TOKENS，说明信息量足够
            if len(tokens) > MIN_TOKENS:
                # 截断 token 列表到允许的最大长度 MAX_TOKENS
                tokens = tokens[:MAX_TOKENS]
    
                # 解码 tokens 回字符串文本
                text = self.tokenizer.decode(tokens)
    
                # 调用 make_prompt 方法生成最终可用于模型输入的提示语
                self.make_prompt(text)
    
                # 设置 include 标记为 True，表示该样本有效，可以用于后续处理
                self.include = True


    def make_prompt(self, text):
        """
        Set the prompt instance variable to be a prompt appropriate for training
        """
        self.prompt = f"{self.QUESTION}\n\n{text}\n\n"
        self.prompt += f"{self.PREFIX}{str(round(self.price))}.00"
        self.token_count = len(self.tokenizer.encode(self.prompt, add_special_tokens=False))

    def test_prompt(self):
        """
        Return a prompt suitable for testing, with the actual price removed
        """
        return self.prompt.split(self.PREFIX)[0] + self.PREFIX

    def __repr__(self):
        """
        Return a String version of this Item
        """
        return f"<{self.title} = ${self.price}>"

        

    
    