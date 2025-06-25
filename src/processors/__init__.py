import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Type, Callable, Union, List, Tuple, Any

from data import DatasetProvider
from model.sample import Sample
from util.logger import Logger


def process_samples(dset: Type[DatasetProvider], fn: Callable[[Type[DatasetProvider], Sample], Tuple[Sample, Any]],
                    batch_size: int = 1000,
                    max_batches: int = None, pool: Union[ThreadPoolExecutor, ProcessPoolExecutor] = None) \
        -> List[Tuple[Sample, Any]]:
    sample: Sample
    b = 0
    batch = []
    result: List[Tuple[Sample, Any]] = []

    for sample in dset.get_samples():
        batch.append(sample)
        if len(batch) == batch_size:
            b += 1
            batch_result = process_sample_batch(dset, batch, b, fn, pool)
            batch = []
            result.extend(batch_result)

            if max_batches and b == max_batches:
                Logger.info(f"Max batches {max_batches} reached, stopping.")
                return result

    if batch:
        b += 1
        batch_result = process_sample_batch(dset, batch, b, fn, pool)
        result.extend(batch_result)
    if pool:
        pool.shutdown(wait=True)

    return result


def process_sample_batch(dset: Type[DatasetProvider], batch: List[Sample], batch_number: int, fn: Callable,
                         pool: Union[ThreadPoolExecutor, ProcessPoolExecutor] = None) -> List[Tuple[Sample, Any]]:
    Logger.info(f"[Batch {batch_number}] {len(batch)} samples")
    i = 0
    ts = time.perf_counter()
    batch_result: List[Tuple[Sample, Any]] = []

    def log_eta(start_ts, i):
        dt = time.perf_counter() - start_ts
        eta = round((len(batch) * dt) / i - dt, 2)
        Logger.info(f"[Batch {batch_number}] {i} samples done, ETA: {eta}s")

    if pool is None:
        for sample in batch:
            res = fn(dset, sample)
            i += 1
            log_eta(ts, i)
            batch_result.append((sample, res))

    else:
        for res in pool.map(fn, [dset] * len(batch), batch):
            i += 1
            log_eta(ts, i)

            batch_result.append(res)

    return batch_result