from datetime import datetime
from tqdm import tqdm
from datasets import load_dataset
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from items import Item

CHUNK_SIZE = 1000
MIN_PRICE = 0.5
MAX_PRICE = 999.49

class ItemLoader:


    def __init__(self, name):
        self.name = name
        self.dataset = None

    def from_datapoint(self, datapoint):
        """
        Try to create an Item from this datapoint
        Return the Item if successful, or None if it shouldn't be included
        """
        try:
            price_str = datapoint['price']
            if price_str:
                price = float(price_str)
                if MIN_PRICE <= price <= MAX_PRICE:
                    item = Item(datapoint, price)
                    return item if item.include else None
        except ValueError:
            return None

    def from_chunk(self, chunk):
        """
        Create a list of Items from this chunk of elements from the Dataset
        """
        batch = []
        for datapoint in chunk:
            result = self.from_datapoint(datapoint)
            if result:
                batch.append(result)
        return batch

    def chunk_generator(self):
        """
        Iterate over the Dataset, yielding chunks of datapoints at a time
        """
        size = len(self.dataset)
        for i in range(0, size, CHUNK_SIZE):
            yield self.dataset.select(range(i, min(i + CHUNK_SIZE, size)))

    def load_in_parallel(self, workers):
        """
        使用 concurrent.futures 模块并行处理数据块。
        这可以显著加速数据处理过程，但在运行时会占用大量 CPU 资源。
        参数 workers 表示并行使用的最大进程数。
        """
    
        # 初始化一个空列表，用于收集所有的处理结果
        results = []
    
        # 计算数据集可分成的块数量，每个块的大小为 CHUNK_SIZE
        chunk_count = (len(self.dataset) // CHUNK_SIZE) + 1
    
        # 创建一个进程池（多进程），最多运行 workers 个进程
        with ProcessPoolExecutor(max_workers=workers) as pool:
            
            # 并行调用 self.from_chunk 方法处理每个数据块
            # 使用 tqdm 显示进度条，方便跟踪处理进度
            for batch in tqdm(pool.map(self.from_chunk, self.chunk_generator()), total=chunk_count):
                
                # 将每个处理结果（一个 batch）扩展加入 results 列表
                results.extend(batch)
    
        # 对所有结果设置它们的 category 字段为当前对象的 name（用于标记数据类别）
        for result in results:
            result.category = self.name
    
        # 返回所有并行处理后的结果列表
        return results

            
    def load(self, workers=8):
        """
        Load in this dataset; the workers parameter specifies how many processes
        should work on loading and scrubbing the data
        """
        start = datetime.now()
        print(f"Loading dataset {self.name}", flush=True)
        self.dataset = load_dataset("McAuley-Lab/Amazon-Reviews-2023", f"raw_meta_{self.name}", split="full", trust_remote_code=True)
        results = self.load_in_parallel(workers)
        finish = datetime.now()
        print(f"Completed {self.name} with {len(results):,} datapoints in {(finish-start).total_seconds()/60:.1f} mins", flush=True)
        return results
        

    
    