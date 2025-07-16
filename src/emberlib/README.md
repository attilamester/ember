# EMBER features

* copy of the [Elastic Malware Benchmark for Empowering Researchers](https://github.com/elastic/ember/blob/master/ember/features.py)
* diff from the original `ember/features.py`:
https://github.com/attilamester/ember/compare/ef03106771576b209efac1d1d1832ad10110ce60...master#diff-d7086d064175580cfb7e554ac8b1cd08d102d813eb26187204421f80a3e9b9a9

## Usage

```
ex = PEFeatureExtractor(2, print_feature_warning=False)
print(ex.feature_vector(pe_binary_content))
print(ex.named_features.general_file_info.raw_features["imports"])
```

## Features

* `ex.named_features` has the following format:
```
class Features(NamedTuple):
    byte_histogram: ByteHistogram = None
    byte_entropy_histogram: ByteEntropyHistogram = None
    string_extractor: StringExtractor = None
    general_file_info: GeneralFileInfo = None
    header_file_info: HeaderFileInfo = None
    section_info: SectionInfo = None
    imports_info: ImportsInfo = None
    exports_info: ExportsInfo = None
    data_directories: DataDirectories = None
```
* `<feature>.raw_features` has the original value format, 
calculated in the function `raw_features`, as defined originally in [EMBER](https://github.com/elastic/ember) 

## Disclaimer
> This project, `emberlib`, is **not affiliated with** or **officially maintained** by the original authors of the [EMBER](https://github.com/elastic/ember) repository.  
It is a **community-driven wrapper** that builds upon the original codebase, adding additional features and improvements.  
All credit for the foundational work goes to the original developers.

