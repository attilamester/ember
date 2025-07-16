import json
import math
from concurrent.futures import ProcessPoolExecutor
from typing import Type, List, Tuple, NamedTuple
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import numpy as np

from data import DatasetProvider
from data.bodmas import Bodmas
from data.malimg import MalImg
from emberlib.features import PEFeatureExtractor
from model.sample import Sample
from processors import process_samples
from util import config
from util.logger import Logger
from util.misc import list_stats, list_occurrences_nested


class ScanResult(NamedTuple):
    v: np.ndarray
    ex: PEFeatureExtractor
    numstrings: int
    avlength: float
    printables: int
    entropy: float
    paths: List[str]
    urls: List[str]
    registry: List[str]
    mz: int
    size: int
    exports: List[str]
    imports: List[str]
    machine: str
    subsystem: str
    entry: int
    section_names: List[str]
    import_libs: List[str]
    import_funcs: List[str]
    export_funcs: List[str]


def get_domain(url: str) -> str:
    try:
        o = urlparse(url)
    except:
        Logger.error(f"Invalid URL: {url}")
        return url

    if o.hostname:
        return o.hostname
    return url


def scan_sample(dset: Type[DatasetProvider], sample: Sample) -> Tuple[Sample, ScanResult]:
    v, ex = sample.get_ember_features()

    # for name, feature in ex.named_features._asdict().items():
    #     feature: FeatureType
    #     print(f"{feature}")

    return sample, ScanResult(
        v,
        ex,
        ex.named_features.string_extractor.raw_features["numstrings"],
        ex.named_features.string_extractor.raw_features["avlength"],
        ex.named_features.string_extractor.raw_features["printables"],
        ex.named_features.string_extractor.raw_features["entropy"],
        ex.named_features.string_extractor.paths,
        [get_domain(url) for url in ex.named_features.string_extractor.urls],
        ex.named_features.string_extractor.registry,
        ex.named_features.string_extractor.raw_features["MZ"],
        ex.named_features.general_file_info.raw_features["size"],
        ex.named_features.general_file_info.raw_features["exports"],
        ex.named_features.general_file_info.raw_features["imports"],
        ex.named_features.header_file_info.raw_features["coff"]["machine"],
        ex.named_features.header_file_info.raw_features["optional"]["subsystem"],
        ex.named_features.section_info.raw_features["entry"],
        [s["name"] for s in ex.named_features.section_info.raw_features["sections"]],
        list(ex.named_features.imports_info.raw_features.keys()),
        [f for f in ex.named_features.imports_info.raw_features.values()],
        ex.named_features.exports_info.raw_features
    )


def display_stats(res: List[Tuple[Sample, ScanResult]], title: str):
    f_strings_numstrings = [r[1].numstrings for r in res]
    f_strings_avlength = [r[1].avlength for r in res]
    f_strings_printables = [r[1].printables for r in res]
    f_strings_entropy = [r[1].entropy for r in res]
    f_strings_paths = [r[1].paths for r in res]
    f_strings_urls = [r[1].urls for r in res]
    f_strings_registry = [r[1].registry for r in res]
    f_strings_mz = [r[1].mz for r in res]
    f_general_size = [r[1].size for r in res]
    f_general_exports = [r[1].exports for r in res]
    f_general_imports = [r[1].imports for r in res]
    f_header_machine = [r[1].machine for r in res]
    f_header_subsys = [r[1].subsystem for r in res]
    f_section_entry = [r[1].entry for r in res]
    f_section_names = [r[1].section_names for r in res]
    f_import_libs = [r[1].import_libs for r in res]
    f_import_func = [r[1].import_funcs for r in res]
    f_export_func = [r[1].export_funcs for r in res]

    features = {
        "f_strings_numstrings": f_strings_numstrings,
        "f_strings_avlength": f_strings_avlength,
        "f_strings_printables": f_strings_printables,
        "f_strings_entropy": f_strings_entropy,
        "f_strings_paths": f_strings_paths,
        "f_strings_urls": f_strings_urls,
        "f_strings_registry": f_strings_registry,
        "f_strings_mz": f_strings_mz,
        "f_general_size": f_general_size,
        "f_general_exports": f_general_exports,
        "f_general_imports": f_general_imports,
        "f_header_machine": f_header_machine,
        "f_header_subsys": f_header_subsys,
        "f_section_entry": f_section_entry,
        "f_section_names": f_section_names,
        "f_import_libs": f_import_libs,
        "f_import_func": f_import_func,
        "f_export_func": f_export_func
    }

    stats = {
        "f_strings_numstrings": list_stats(f_strings_numstrings),
        "f_strings_avlength": list_stats(f_strings_avlength),
        "f_strings_printables": list_stats(f_strings_printables),
        "f_strings_entropy": list_stats(f_strings_entropy),
        "f_strings_paths": list_occurrences_nested(f_strings_paths),
        "f_strings_urls": list_occurrences_nested(f_strings_urls),
        "f_strings_registry": list_occurrences_nested(f_strings_registry),
        "f_strings_mz": list_stats(f_strings_mz),
        "f_general_size": list_stats(f_general_size),
        "f_general_exports": list_stats(f_general_exports),
        "f_general_imports": list_stats(f_general_imports),
        "f_header_machine": list_occurrences_nested(f_header_machine),
        "f_header_subsys": list_occurrences_nested(f_header_subsys),
        "f_section_entry": list_occurrences_nested(f_section_entry),
        "f_section_names": list_occurrences_nested(f_section_names),
        "f_import_libs": list_occurrences_nested(f_import_libs),
        "f_import_func": list_occurrences_nested(f_import_func),
        "f_export_func": list_occurrences_nested(f_export_func)
    }

    numerical_features = [
        "f_strings_numstrings",
        "f_strings_avlength",
        "f_strings_printables",
        "f_strings_entropy",
        "f_strings_mz",
        "f_general_size",
        "f_general_exports",
        "f_general_imports"
    ]
    categorical_features = [
        "f_strings_paths",
        "f_strings_urls",
        "f_strings_registry",
        "f_header_machine",
        "f_header_subsys",
        "f_section_entry",
        "f_section_names",
        "f_import_libs",
        "f_import_func",
        "f_export_func"
    ]
    with open(f"{title}_stats.json", "w") as f:
        json.dump(stats, f, indent=4)
    plot_numerical_features(features, numerical_features, title)
    plot_categorical_features(features, categorical_features, title)


def get_subplots_grid(num_plots: int) -> (int, int):
    # find the closest square root
    sq = round(math.sqrt(num_plots))
    closest_square_root = sq ** 2
    if closest_square_root < num_plots:
        rows = sq + 1
    else:
        rows = sq
    cols = math.ceil(num_plots / rows)
    return rows, cols


def plot_numerical_features(stats, feature_names: List[str], title: str):
    numerical_features = [stats[name] for name in feature_names]
    rows, cols = get_subplots_grid(len(feature_names))
    fig = plt.figure(figsize=(20, 20))
    for i, feature in enumerate(numerical_features):
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.boxplot(feature, showmeans=True)
        ax.set_title(feature_names[i])
        ax.set_ylabel("Value")
    plt.savefig(f"{title}_numerical_features.pdf", bbox_inches="tight")


def plot_categorical_features(stats, feature_names: List[str], title: str):
    categorical_features = [stats[name] for name in feature_names]
    rows, cols = get_subplots_grid(len(categorical_features))
    fig = plt.figure(figsize=(20, 40))
    for i, feature in enumerate(categorical_features):
        ax = fig.add_subplot(rows, cols, i + 1)

        occurences = list_occurrences_nested(feature)[::-1][:100]
        values = [i[1] for i in occurences]
        labels = [i[0].replace("$", "") for i in occurences]

        ax.barh(range(len(values)), values, tick_label=labels, color='skyblue')
        ax.set_title(feature_names[i])
        ax.set_ylabel("Value")
    plt.savefig(f"{title}_categorical_features.pdf", bbox_inches="tight")


if __name__ == "__main__":
    config.load_env()
    res = process_samples(Bodmas, scan_sample, batch_size=100, max_batches=None,
                          pool=ProcessPoolExecutor(max_workers=8))
    # res = process_samples(MalImg, scan_sample, batch_size=100, max_batches=None, pool=ProcessPoolExecutor(max_workers=8))
    display_stats(res, f"bodmas_armed{len(res)}")
