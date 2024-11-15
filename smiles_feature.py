from rdkit import Chem
from rdkit.Chem import MolFromSmiles
import numpy as np
import pickle

degrees = [0, 1, 2, 3, 4, 5]


class Node(object):
    __slots__ = ['ntype', 'features', '_neighbors', 'rdkit_ix']
    def __init__(self, ntype, features, rdkit_ix):
        self.ntype = ntype
        self.features = features
        self._neighbors = []
        self.rdkit_ix = rdkit_ix

    def add_neighbors(self, neighbor_list):
        for neighbor in neighbor_list:
            self._neighbors.append(neighbor)
            neighbor._neighbors.append(self)

    def get_neighbors(self, ntype):
        return [n for n in self._neighbors if n.ntype == ntype]

class MolGraph(object):
    def __init__(self):
        self.nodes = {} # dict of lists of nodes, keyed by node type

    def new_node(self, ntype, features=None, rdkit_ix=None):
        new_node = Node(ntype, features, rdkit_ix)
        self.nodes.setdefault(ntype, []).append(new_node)
        return new_node

    def add_subgraph(self, subgraph):
        old_nodes = self.nodes
        new_nodes = subgraph.nodes
        for ntype in set(old_nodes.keys()) | set(new_nodes.keys()):
            old_nodes.setdefault(ntype, []).extend(new_nodes.get(ntype, []))

    def sort_nodes_by_degree(self, ntype):
        nodes_by_degree = {i : [] for i in degrees}
        for node in self.nodes[ntype]:
            nodes_by_degree[len(node.get_neighbors(ntype))].append(node)

        new_nodes = []
        for degree in degrees:
            cur_nodes = nodes_by_degree[degree]
            self.nodes[(ntype, degree)] = cur_nodes
            new_nodes.extend(cur_nodes)

        self.nodes[ntype] = new_nodes

    def feature_array(self, ntype):
        assert ntype in self.nodes
        return np.array([node.features for node in self.nodes[ntype]])

    def rdkit_ix_array(self):
        return np.array([node.rdkit_ix for node in self.nodes['atom']])

    def neighbor_list(self, self_ntype, neighbor_ntype):
        assert self_ntype in self.nodes and neighbor_ntype in self.nodes
        neighbor_idxs = {n : i for i, n in enumerate(self.nodes[neighbor_ntype])}
        return [[neighbor_idxs[neighbor]
                 for neighbor in self_node.get_neighbors(neighbor_ntype)]
                for self_node in self.nodes[self_ntype]]

def one_of_k_encoding(x, allowable_set):
    if x not in allowable_set:
        raise Exception("input {0} not in allowable set{1}:".format(
            x, allowable_set))
    return [x == s for s in allowable_set]


def one_of_k_encoding_unk(x, allowable_set):
    """Maps inputs not in the allowable set to the last element."""
    if x not in allowable_set:
        x = allowable_set[-1]
    return [x == s for s in allowable_set]


def atom_features(atom,
                  bool_id_feat=False,
                  explicit_H=False,
                  use_chirality=True):
    if bool_id_feat:
        return np.array([atom_to_id(atom)])
    else:
        results = one_of_k_encoding_unk(
          atom.GetSymbol(),
          [
            'B',
            'C',
            'N',
            'O',
            'F',
            'Si',
            'P',
            'S',
            'Cl',
            'As',
            'Se',
            'Br',
            'Te',
            'I',
            'At',
            'other'
          ]) + one_of_k_encoding(atom.GetDegree(),
                                 [0, 1, 2, 3, 4, 5]) + \
                  [atom.GetFormalCharge(), atom.GetNumRadicalElectrons()] + \
                  one_of_k_encoding_unk(atom.GetHybridization(), [
                    Chem.rdchem.HybridizationType.SP, Chem.rdchem.HybridizationType.SP2,
                    Chem.rdchem.HybridizationType.SP3, Chem.rdchem.HybridizationType.
                                        SP3D, Chem.rdchem.HybridizationType.SP3D2,'other'
                  ]) + [atom.GetIsAromatic()]
        # In case of explicit hydrogen(QM8, QM9), avoid calling `GetTotalNumHs`
        if not explicit_H:
            results = results + one_of_k_encoding_unk(atom.GetTotalNumHs(),
                                                      [0, 1, 2, 3, 4])
        if use_chirality:
            try:
                results = results + one_of_k_encoding_unk(
                    atom.GetProp('_CIPCode'),
                    ['R', 'S']) + [atom.HasProp('_ChiralityPossible')]
            except:
                results = results + [False, False
                                     ] + [atom.HasProp('_ChiralityPossible')]

        return np.array(results)


def bond_features(bond, use_chirality=True):
    bt = bond.GetBondType()
    bond_feats = [
        bt == Chem.rdchem.BondType.SINGLE, bt == Chem.rdchem.BondType.DOUBLE,
        bt == Chem.rdchem.BondType.TRIPLE, bt == Chem.rdchem.BondType.AROMATIC,
        bond.GetIsConjugated(),
        bond.IsInRing()
    ]
    if use_chirality:
        bond_feats = bond_feats + one_of_k_encoding_unk(
            str(bond.GetStereo()),
            ["STEREONONE", "STEREOANY", "STEREOZ", "STEREOE"])
    return np.array(bond_feats)

def graph_from_smiles(smiles):
    graph = MolGraph()
    mol = MolFromSmiles(smiles)
    if not mol:
        raise ValueError("Could not parse SMILES string:", smiles)
    atoms_by_rd_idx = {}
    for atom in mol.GetAtoms():
        new_atom_node = graph.new_node('atom', features=atom_features(atom), rdkit_ix=atom.GetIdx())
        atoms_by_rd_idx[atom.GetIdx()] = new_atom_node

    for bond in mol.GetBonds():
        atom1_node = atoms_by_rd_idx[bond.GetBeginAtom().GetIdx()]
        atom2_node = atoms_by_rd_idx[bond.GetEndAtom().GetIdx()]
        new_bond_node = graph.new_node('bond', features=bond_features(bond))
        new_bond_node.add_neighbors((atom1_node, atom2_node))
        atom1_node.add_neighbors((atom2_node,))

    mol_node = graph.new_node('molecule')
    mol_node.add_neighbors(graph.nodes['atom'])
    return graph

def array_rep_from_smiles(molgraph):
    """Precompute everything we need from MolGraph so that we can free the memory asap."""
    #molgraph = graph_from_smiles_tuple(tuple(smiles))
    degrees = [0,1,2,3,4,5]
    arrayrep = {'atom_features' : molgraph.feature_array('atom'),
                'bond_features' : molgraph.feature_array('bond'),
                'atom_list'     : molgraph.neighbor_list('molecule', 'atom'),
                'rdkit_ix'      : molgraph.rdkit_ix_array()}

    for degree in degrees:
        arrayrep[('atom_neighbors', degree)] = \
            np.array(molgraph.neighbor_list(('atom', degree), 'atom'), dtype=int)
        arrayrep[('bond_neighbors', degree)] = \
            np.array(molgraph.neighbor_list(('atom', degree), 'bond'), dtype=int)
    return arrayrep

def gen_descriptor_data(smilesList):
    smiles_to_fingerprint_array = {}

    for i, smiles in enumerate(smilesList):
        #         if i > 5:
        #             print("Due to the limited computational resource, submission with more than 5 molecules will not be processed")
        #             break
        smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles), isomericSmiles=True)
        try:

            molgraph = graph_from_smiles(smiles)
            molgraph.sort_nodes_by_degree('atom')
            arrayrep = array_rep_from_smiles(molgraph)

            smiles_to_fingerprint_array[smiles] = arrayrep

        except:
            print(smiles,"%%%%%%%%")
            # time.sleep(3)
    return smiles_to_fingerprint_array

def save_smiles_dicts(smilesList, filename):
    # first need to get the max atom length
    max_atom_len = 0
    max_bond_len = 0
    num_atom_features = 0
    num_bond_features = 0
    smiles_to_rdkit_list = {}

    smiles_to_fingerprint_features = gen_descriptor_data(smilesList)

    for smiles, arrayrep in smiles_to_fingerprint_features.items():

        atom_features = arrayrep['atom_features']
        bond_features = arrayrep['bond_features']

        rdkit_list = arrayrep['rdkit_ix']
        smiles_to_rdkit_list[smiles] = rdkit_list

        atom_len, num_atom_features = atom_features.shape
        bond_len, num_bond_features = bond_features.shape

        if atom_len > max_atom_len:
            max_atom_len = atom_len
        if bond_len > max_bond_len:
            max_bond_len = bond_len

    # then add 1 so I can zero pad everything
    max_atom_index_num = max_atom_len
    max_bond_index_num = max_bond_len

    max_atom_len += 1
    max_bond_len += 1

    smiles_to_atom_info = {}
    smiles_to_bond_info = {}

    smiles_to_atom_neighbors = {}
    smiles_to_bond_neighbors = {}

    smiles_to_atom_mask = {}

    degrees = [0, 1, 2, 3, 4, 5]
    # then run through our numpy array again
    for smiles, arrayrep in smiles_to_fingerprint_features.items():
        mask = np.zeros((max_atom_len))

        # get the basic info of what
        #    my atoms and bonds are initialized
        atoms = np.zeros((max_atom_len, num_atom_features))
        bonds = np.zeros((max_bond_len, num_bond_features))

        # then get the arrays initlialized for the neighbors
        atom_neighbors = np.zeros((max_atom_len, len(degrees)))
        bond_neighbors = np.zeros((max_atom_len, len(degrees)))

        # now set these all to the last element of the list, which is zero padded
        atom_neighbors.fill(max_atom_index_num)
        bond_neighbors.fill(max_bond_index_num)

        atom_features = arrayrep['atom_features']
        bond_features = arrayrep['bond_features']

        for i, feature in enumerate(atom_features):
            mask[i] = 1.0
            atoms[i] = feature

        for j, feature in enumerate(bond_features):
            bonds[j] = feature

        atom_neighbor_count = 0
        bond_neighbor_count = 0
        working_atom_list = []
        working_bond_list = []
        for degree in degrees:
            atom_neighbors_list = arrayrep[('atom_neighbors', degree)]
            bond_neighbors_list = arrayrep[('bond_neighbors', degree)]

            if len(atom_neighbors_list) > 0:

                for i, degree_array in enumerate(atom_neighbors_list):
                    for j, value in enumerate(degree_array):
                        atom_neighbors[atom_neighbor_count, j] = value
                    atom_neighbor_count += 1

            if len(bond_neighbors_list) > 0:
                for i, degree_array in enumerate(bond_neighbors_list):
                    for j, value in enumerate(degree_array):
                        bond_neighbors[bond_neighbor_count, j] = value
                    bond_neighbor_count += 1

        # then add everything to my arrays
        smiles_to_atom_info[smiles] = atoms
        smiles_to_bond_info[smiles] = bonds

        smiles_to_atom_neighbors[smiles] = atom_neighbors
        smiles_to_bond_neighbors[smiles] = bond_neighbors

        smiles_to_atom_mask[smiles] = mask

    del smiles_to_fingerprint_features
    feature_dicts = {}
    #     feature_dicts['smiles_to_atom_mask'] = smiles_to_atom_mask
    #     feature_dicts['smiles_to_atom_info']= smiles_to_atom_info
    feature_dicts = {
        'smiles_to_atom_mask': smiles_to_atom_mask,
        'smiles_to_atom_info': smiles_to_atom_info,
        'smiles_to_bond_info': smiles_to_bond_info,
        'smiles_to_atom_neighbors': smiles_to_atom_neighbors,
        'smiles_to_bond_neighbors': smiles_to_bond_neighbors,
        'smiles_to_rdkit_list': smiles_to_rdkit_list
    }
    pickle.dump(feature_dicts, open(filename, "wb"))
    print('feature dicts file saved as ' + filename)
    return feature_dicts

def get_smiles_array(smilesList, feature_dicts):
    x_mask = []
    x_atom = []
    x_bonds = []
    x_atom_index = []
    x_bond_index = []
    for smiles in smilesList:
        if isinstance(smiles, tuple):
            smiles = smiles[0]
        smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles), isomericSmiles=True)
        x_mask.append(feature_dicts['smiles_to_atom_mask'][smiles])
        x_atom.append(feature_dicts['smiles_to_atom_info'][smiles])
        x_bonds.append(feature_dicts['smiles_to_bond_info'][smiles])
        x_atom_index.append(feature_dicts['smiles_to_atom_neighbors'][smiles])
        x_bond_index.append(feature_dicts['smiles_to_bond_neighbors'][smiles])
    return np.asarray(x_atom), np.asarray(x_bonds), np.asarray(x_atom_index),\
        np.asarray(x_bond_index), np.asarray(x_mask), feature_dicts['smiles_to_rdkit_list']