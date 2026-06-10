# Meta-MM: Meta-Learning with Multi-Modal Fusion for Molecular Property Prediction

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A meta-learning framework combining graph attention networks (Meta-GAT) with multi-modal molecular representations (sequence, graph, geometry) for accurate molecular property prediction.**

| Dataset | Task | ROC-AUC |
|---------|------|---------|
| MUV | Classification | 0.67 |
| SIDER | Classification | **0.79** |

---

## Overview

Molecular property prediction is critical in drug discovery. This project proposes **Meta-MM**, which integrates two key ideas:

- **Meta-GAT**: A meta-learning framework built on Graph Attention Networks (GAT), enabling fast adaptation across molecular tasks via learning-to-learn.
- **SGGRL (Sequence, Graph & Geometric Representations Learning)**: Multi-modal molecular encoding that captures sequential (SMILES), topological (graph), and 3D geometric information.

The fusion of meta-learning + multi-modal representations provides robust generalization, especially on small-sample tasks.

### Architecture

```
                          ┌─────────────────────┐
SMILES ──► Sequence Encoder ──► seq_emb ─┐       │
SMILES ──► Graph Encoder   ──► gnn_emb ──┤ concat │──► fusion_emb
SMILES ──► Geo Encoder     ──► geo_emb ─┘       │
                          └─────────────────────┘
                                    │
                                    ▼
                           Meta-GAT (fast weights)
                                    │
                                    ▼
                              ┌──────────┐
                              │ Predictor │──► ROC-AUC
                              └──────────┘
```

---

## Datasets

This repository includes public benchmark datasets used in the experiments:

| Dataset | Type | # Compounds | Description |
|---------|------|-------------|-------------|
| [MUV](https://pubs.acs.org/doi/10.1021/ci8002649) | Classification | ~93K | Maximum Unbiased Validation |
| [SIDER](http://sideeffects.embl.de/) | Classification | ~1.4K | Drug side effect database |
| [TOX21](https://tripod.nih.gov/tox21/challenge/) | Classification | ~8K | Toxicology predictions |
| [QM9](https://arxiv.org/abs/1703.00564) | Regression | ~134K | Quantum mechanical properties |

**Note:** `dataGithub/` contains pre-processed MUV, SIDER, and TOX21 CSV files. The QM9 dataset is **not included** due to its large size (~300 MB+). To run QM9 experiments, download it from the [official source](https://arxiv.org/abs/1703.00564) and follow the preprocessing steps in `meta_origin/`.

---

## Requirements

- Python ≥ 3.8
- PyTorch ≥ 1.9
- RDKit (for molecular featurization)
- CUDA-capable GPU recommended (tested on RTX 3080/3090)

### Install with conda

```bash
conda env create -f environment.yml
conda activate metam
```

### Or install with pip

```bash
pip install torch rdkit-pypi numpy pandas scikit-learn
```

---

## Usage

### Data Preparation

Pre-processed CSV files are provided in [`dataGithub/`](dataGithub/). The model expects SMILES strings with corresponding labels. Prepare your custom data in the same format:

```
smiles,label
CC(=O)Oc1ccccc1C(=O)O,0
CN1C(=NC2=C1C(=O)N(C(=O)N2C)C)O,1
```

### Training & Evaluation

Run the full pipeline (data loading → meta-training → evaluation):

```bash
python Meta-GAT.py
```

This executes the main entry point:
1. Loads molecular data and constructs multi-modal features
2. Trains the Meta-GAT meta-learner with episodic sampling
3. Evaluates on the held-out tasks

### Key Configuration Options

See [`parser_args.py`](parser_args.py) for all configurable hyperparameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset` | `sider` | Dataset selection (muv/sider/tox21) |
| `--lr` | 0.0001 | Meta-learning rate |
| `--n_shot` | 16 | Number of support samples per task |
| `--n_query` | 16 | Number of query samples per task |
| `--epochs` | 100 | Meta-training epochs |
| `--seed` | 42 | Random seed |

---

## Project Structure

```
Meta-MM/
├── Meta-GAT.py                    # Main entry point
├── MetaLearner.py                 # Meta-learner (classification)
├── MetaLearnerReg.py              # Meta-learner (regression)
├── model.py                       # Multi-modal fusion model
├── model_tranfer.py               # Transfer learning variant
├── dataset.py                     # Dataset loading
├── regdataset.py                  # Regression dataset
├── parser_args.py                 # CLI arguments
├── smiles_feature.py              # SMILES featurization
├── build_vocab.py                 # Vocabulary builder
├── build_corpus.py                # Corpus builder
├── data_3d.py                     # 3D geometry feature extraction
├── deepchem.py                    # DeepChem integration
├── utilss.py                      # Utility functions
├── chemprop/                      # Chemprop (MPNN) submodule
├── models_lib/                    # Model building blocks
│   ├── gnn_block.py               # GNN layers
│   ├── compound_encoder.py        # Molecular encoder
│   ├── gem_model.py               # GEM model
│   ├── multi_modal.py             # Multi-modal fusion
│   └── seq_model.py               # Sequence model
├── featurizers/
│   └── gem_featurizer.py          # GEM featurization
├── model_configs/                 # Model configs (JSON)
├── utils/                         # Shared utilities
├── dataGithub/                    # Public benchmark datasets
└── environment.yml                # Conda environment
```

---

## Performance

| Dataset | ROC-AUC | Model |
|---------|---------|-------|
| **SIDER** | **0.79** | Meta-MM |
| MUV | 0.67 | Meta-MM |
| TOX21 | *in progress* | Meta-MM |
| QM9 | *in progress* | Meta-MM (regression) |

---

## Citation

If you find this work useful, please cite:

```bibtex
@misc{liang2024metamm,
  author = {Liang, Jiajie},
  title = {Meta-MM: Meta-Learning with Multi-Modal Fusion for Molecular Property Prediction},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/GargitMoe/Meta-MM-Drug-prediction-model}
}
```

---

## Acknowledgments

This project builds upon two excellent prior works:

- **SGGRL** — Sequence, Graph, Geometric Representations Learning  
  [Paper](https://arxiv.org/abs/2401.03369) | [Code](https://github.com/GargitMoe/SGGRL-master)

- **Meta-GAT** — Meta-Learning with Graph Attention Networks  
  [Paper](https://doi.org/10.1109/TNNLS.2023.3250324) | [Code](https://github.com/lvqiujie/Meta-GAT)

---

## License

[MIT](LICENSE) © 2024 GargitMoe Wang Shuai(SYSU)
