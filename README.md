# Meta-GAT + Multi-Modal for Molecular Property Prediction

This repository implements a Meta-Learning framework combined with Multi-Modal Learning for molecular property prediction tasks. The core model integrates **Meta-GAT** and **SGGRL** (Sequence, Graph, and Geometric Representations Learning), providing a novel approach for molecular analysis.

## Features

- **Meta-Learning**: Utilize Meta-GAT to adaptively learn molecular tasks. Employ meta-learning techniques for fast task adaptation.
- **Multi-Modal Learning**: Combine sequence-based, graph-based, and geometric representations for comprehensive molecular property analysis.

---

## Installation

### Install dependencies

Run the following commands to install the required packages:

```bash
conda env create -f environment.yml
```
---

## Usage

### Data Preparation
The project utilizes the following datasets for molecular property prediction:

1. **MUV**: A dataset for classification tasks, focusing on molecular activity prediction.
2. **TOX21**: A classification dataset for toxicology prediction, containing molecular data labeled with various toxicological endpoints.
3. **SIDER**: A classification dataset used for side effect prediction in molecular compounds.
4. **QM9**: A regression dataset containing quantum mechanical properties of molecules.


> **Note**: Due to the large size of the QM9 datasets, the repository does not include QM9 files.
If you are looking for related information or wish to download the QM9 dataset, you can refer to the original QM9 paper: [https://arxiv.org/abs/1703.00564](https://arxiv.org/abs/1703.00564).
---

## Running

```bash
python Meta-GAT.py
```
> **Note:** Due to the integration of SGGRL and Meta-MM in this model, it is not "lightweight." Please ensure that your GPU has sufficient memory for running the model. The results presented are based on an RTX 3080 GPU.

---

## Key Files

### 1. `models.py`

- **Integration of Meta-GAT and SGGRL Models**: Combines the multi-modal features from SGGRL with the meta-learning framework from Meta-GAT.
- **Prediction Fusion**: Uses `fusion_emb` to concatenate and pass multi-modal features through a fully connected layer for final prediction.
- **Error Calculation**: Implements SGGRL's error calculation strategy for multi-modal representation learning.

### 2. `MetaLearner` and `MetaLearnerReg` Classes

- **Meta-Learning Optimization**: Updates fastweights using the meta-learning optimization method from Meta-GAT.
- **Forward Propagation Adjustments**: Removes SGGRL modules that do not participate in forward propagation to ensure fastweights are correctly updated.

---
## Performance of Meta-MM

The performance of **Meta-MM** on two benchmark datasets is shown below:

| Dataset | ROC-AUC |
| ------- | ------- |
| MUV     | 0.67    |
| Sider   | 0.79    |

---
## Acknowledgments

This project integrates techniques from **Meta-GAT** and **SGGRL**, and we are deeply grateful to the original authors for their outstanding work. Readers interested in their methods can refer to the following resources:

- **SGGRL Paper and Code**: [https://arxiv.org/abs/2401.03369](https://arxiv.org/abs/2401.03369)
- **Meta-GAT Code**: [https://github.com/lvqiujie/Meta-GAT](https://github.com/lvqiujie/Meta-GAT)
- **Meta-GAT Paper**: [https://doi.org/10.1109/TNNLS.2023.3250324](https://doi.org/10.1109/TNNLS.2023.3250324)


## Copyright Notice

This code is jointly developed by @GargitMoe and S.W. If you encounter any issues or have any questions, feel free to reach out, and we will do our best to assist you.
If this work has been helpful to your project, please consider citing our original GitHub repository.


