import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TritonBench_v1.attn_fwd_causal import forward
from performance_utils import Performance_Metrics, do_bench_config

import torch
import triton
import triton.language as tl

class performance_metrics(Performance_Metrics):
    def __init__(self, dtype=None, is_backward=False, **kwargs):
        super().__init__('attn_fwd_causal', dtype=dtype, is_backward=is_backward, **kwargs)
        
    def get_input_tensors(self):
        self.input_tensors = []
        for i in range(2, 12):  # Adjust the range as needed
            size = 2 ** i
            q = torch.rand((32, 8, size, 128), dtype=torch.float16)
            k = torch.rand((32, 8, size, 128), dtype=torch.float16)
            v = torch.rand((32, 8, size, 128), dtype=torch.float16)
            q_scale = torch.tensor(1.0, dtype=torch.float32)
            k_scale = torch.tensor(1.0, dtype=torch.float32)
            self.input_tensors.append((q, k, v, q_scale, k_scale))

    def to_cuda(self, input_tensor):
        q, k, v, q_scale, k_scale = input_tensor
        return (q.cuda(), k.cuda(), v.cuda(), q_scale.cuda(), k_scale.cuda())

    def call_op(self, input_tensor):
        q, k, v, q_scale, k_scale = input_tensor
        return forward(q, k, v, q_scale, k_scale)

    def get_gbps(self, input_tensor, runtime):
        q, k, v, _, _ = input_tensor
        total_bytes = (q.numel() + k.numel() + v.numel()) * q.element_size() * 2  # Read and write
        GBPS = total_bytes / (runtime / 1000) / 1e9
        return GBPS
    
    def get_tflops(self, input_tensor, runtime):
        q, k, v, _, _ = input_tensor
        num_operations = 2 * q.shape[2] * q.shape[3] * q.shape[3]  # Simplified FLOP count
        TFLOPS = num_operations / (runtime / 1000) / 1e12
        return TFLOPS

if __name__ == '__main__':
    op_perf = performance_metrics()
    op_perf.get_input_tensors()
    op_perf.get_do_bench_config(warmup=100, rep=1000)
    op_perf.run_benchmark()
