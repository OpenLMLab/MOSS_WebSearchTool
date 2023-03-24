import time
import fasttext

from google_search import engine

import logging
from typing import Any, List
import json
#import torch
import time
try:
    import thread
except ImportError:
    import _thread as thread
from multiprocessing import Process, Lock

from mosec import Server, Worker
import spacy

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(process)d - %(levelname)s - %(filename)s:%(lineno)s - %(message)s"
)
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

INFERENCE_BATCH_SIZE = 1

class Preprocess(Worker):
    """Preprocess BERT on current setup."""

    def __init__(self):
        super().__init__()
        
    def deserialize(self, data: bytes) -> str:
        # Override `deserialize` for the *first* stage;
        # `data` is the raw bytes from the request body
        return data.decode("utf-8")

    def forward(self, data):
        return json.loads(data)
    
class Inference(Worker):
    """Pytorch Inference class"""

    def __init__(self):
        super().__init__()
        self.measure = None
        print("loading embeddings ...")
        self.ft_en = fasttext.load_model('cc.en.300.bin')
        self.ft_zh = fasttext.load_model('cc.zh.300.bin')
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_zh = spacy.load("zh_core_web_sm")
        from score_utils import score_measure
        self.measure_en = None#score_measure("en")
        self.measure_zh = None#score_measure("zh")
        print("embeddings loaded ...")
        
        self.topk = 5

    def forward(self, data):
        json_data = data#request.json
        
        query = str(json_data["query"])
        start_time = time.time()
        response = engine(query, 
                          ft_en=self.ft_en, 
                          ft_zh=self.ft_zh, 
                          nlp_en=self.nlp_en, 
                          nlp_zh=self.nlp_zh,
                          measure_en=self.measure_en,
                          measure_zh=self.measure_zh,
                          topk=self.topk
                          )
        print("engine cost: ", time.time() - start_time)
        return json.dumps(response)

    def serialize(self, data: str) -> bytes:
        # Override `serialize` for the *last* stage;
        # `data` is the string from the `forward` output
        # print(data)
        return data.encode("utf-8")


if __name__ == "__main__":
    NUM_DEVICE = 12
    server = Server()
    server.append_worker(Preprocess, num=NUM_DEVICE)
    server.append_worker(Inference, 
                         num=NUM_DEVICE, 
                         #env=[_get_cuda_device(x) for x in range(NUM_DEVICE)], #env=[{"CUDA_VISIBLE_DEVICES":"7"}],
                         max_batch_size=INFERENCE_BATCH_SIZE, 
                        )#_
    #server.append_worker(Inference, num=NUM_DEVICE, env=[{"CUDA_VISIBLE_DEVICES":"7"}], max_batch_size=INFERENCE_BATCH_SIZE)#_
    server.run()
