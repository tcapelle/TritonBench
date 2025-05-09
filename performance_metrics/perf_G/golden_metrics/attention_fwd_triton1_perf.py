import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TritonBench_v1.attention_fwd_triton1 import AttentionFunction
from performance_utils import Performance_Metrics, do_bench_config

import torch
import triton
import triton.language as tl

class performance_metrics(Performance_Metrics):
    def __init__(self, dtype=None, is_backward=False, **kwargs):
        super().__init__('attention_fwd_triton1', dtype=dtype, is_backward=is_backward, **kwargs)
        
    def get_input_tensors(self):
        self.input_tensors = []
        for i in range(5, 15):  # Example sizes, adjust as needed
            batch_size = 2 ** i
            n_heads = 8
            seq_len = 128
            d_head = 64
            q = torch.rand(batch_size, n_heads, seq_len, d_head, dtype=torch.float32)
            k = torch.rand(batch_size, n_heads, seq_len, d_head, dtype=torch.float32)
            v = torch.rand(batch_size, n_heads, seq_len, d_head, dtype=torch.float32)
            self.input_tensors.append((q, k, v))

    def to_cuda(self, input_tensor):
        q, k, v = input_tensor
        return q.cuda(), k.cuda(), v.cuda()

    def call_op(self, input_tensor):
        q, k, v = input_tensor
        return AttentionFunction.apply(q, k, v)

    def get_gbps(self, input_tensor, runtime):
        q, k, v = input_tensor
        total_bytes = 3 * q.numel() * q.element_size()  # q, k, v are the same size
        GBPS = total_bytes / (runtime / 1000) / 1e9
        return GBPS
    
    def get_tflops(self, input_tensor, runtime):
        q, k, v = input_tensor
        batch_size, n_heads, seq_len, d_head = q.shape
        FLOPS = 2 * batch_size * n_heads * seq_len * d_head * seq_len  # Simplified FLOP count
        TFLOPS = FLOPS / (runtime / 1000) / 1e12
        return TFLOPS

if __name__ == '__main__':
    op_perf = performance_metrics()
    op_perf.get_input_tensors()
    op_perf.get_do_bench_config(warmup=100, rep=1000)
    op_perf.run_benchmark()
