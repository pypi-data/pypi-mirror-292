from tqdm import tqdm
from typing import Callable, Iterable, Union, Sized
from pathos.multiprocessing import Pool


def parallel_map(
    func: Callable, data: Iterable, workers: int = 2, chunksize=None, **kwargs
):
    pool = Pool(workers, **kwargs)
    mapped_values = pool.map(func, data, chunksize=chunksize)
    pool.close()
    pool.join()
    return mapped_values


def iter_parallel_map(
    func: Callable, data: Union[Iterable, Sized], workers: int = 2, bar=True
):
    pool = Pool(workers)
    if bar:
        mapped_values = list(tqdm(pool.imap(func, data), total=len(data)))
    else:
        mapped_values = list(pool.imap(func, data))
    return mapped_values
