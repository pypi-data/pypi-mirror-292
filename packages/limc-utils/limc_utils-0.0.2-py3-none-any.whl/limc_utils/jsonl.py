import json
from typing import Set, List, Iterable, Any, Callable
from tqdm import tqdm
from .parallel import iter_parallel_map


class JsonLReader:

    def __init__(self, file: str, encoding="utf-8", keys: Iterable[str] = None):
        """
        :param file: json line file path.
        :param encoding: default "utf-8"
        """
        self.file = file
        self.encoding = encoding
        self.keys = keys

    def yield_read(self, max_lines: int = None):
        if max_lines is None or max_lines < 1:
            max_lines = float("inf")
        file = open(self.file, "r", encoding=self.encoding)
        index = -1
        while True:
            line = file.readline()
            index = index + 1
            if index + 1 >= max_lines:
                break
            elif line is None or len(line) == 0:
                break
            else:
                yield self.json_load(line)
        file.close()

    def json_load(self, line) -> dict:
        line = line.strip()
        if self.keys is None:
            data = json.loads(line)
        else:
            data = json.loads(line)
            data = {key: data[key] for key in self.keys}
        return data

    def read(self, bar=True, max_lines: int = None) -> List[dict]:
        if bar or (max_lines is not None):
            return list(
                tqdm(self.yield_read(max_lines=max_lines), desc=f"reading {self.file}")
            )
        else:
            file = open(self.file, "r", encoding=self.encoding)
            content = file.readlines()
            file.close()
            return [self.json_load(each) for each in content]

    def read_idx(self, idx: int) -> dict:
        file = open(self.file, "r", encoding=self.encoding)
        index = -1
        while index <= idx:
            line = file.readline()
            index = index + 1
            if index == idx:
                return self.json_load(line)
        file.close()

    def head(self, lines: int = 1):
        return list(self.yield_read(max_lines=lines))


class JsonLWriter:
    def __init__(self, file: str, mode: str = "w+", encoding="utf-8"):
        self.file = None
        self.file = open(file, mode, encoding=encoding)

    def close(self):
        if self.file:
            self.file.close()

    def save_one(self, item: dict):
        self.file.write(self.dumps_line(item))

    def save(self, data: Iterable[dict], bar=True):
        if bar:
            data = tqdm(data)
            data.set_description(f"Saving to {self.file.name}")
        for each in data:
            self.save_one(each)
        self.close()

    @staticmethod
    def dumps_line(item: dict):
        return json.dumps(item) + "\n"

    def __del__(self):
        self.close()


class JsonLFix:

    def __init__(self, file: str, out_file: str = None):
        self.file = file
        self.out_file = out_file if out_file is not None else file
        self.reader = JsonLReader(file)

    def apply(self, func: Callable, workers: int = 4):
        if workers > 1:
            self.parallel_apply(func, workers)
        else:
            self.serial_apply(func)

    def serial_apply(self, func: Callable):
        data = self.reader.read(bar=True)
        writer = JsonLWriter(self.out_file)
        bar = tqdm(data)
        bar.set_description(f"apply {func} to {self.file}")
        applied = 0
        deleted = 0
        for each in bar:
            item = func(each)
            if item is not None:
                writer.save_one(item)
                applied += 1
                bar.set_postfix(applied=applied, deleted=deleted)
            else:
                deleted += 1
                bar.set_postfix(applied=applied, deleted=deleted)

    def parallel_apply(self, func: Callable, workers: int):
        data = self.reader.read(bar=True)
        writer = JsonLWriter(self.out_file)
        mapped = iter_parallel_map(func, data, workers=workers, bar=True)
        applied = 0
        deleted = 0
        bar = tqdm(mapped)
        bar.set_description(f"applied {func} to {self.file}")
        for item in bar:
            if item is not None:
                writer.save_one(item)
                applied += 1
                bar.set_postfix(applied=applied, deleted=deleted)
            else:
                deleted += 1
                bar.set_postfix(applied=applied, deleted=deleted)
