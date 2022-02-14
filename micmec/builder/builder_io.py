#!/usr/bin/env python
# File name: system.py
# Description: The construction of a system of micromechanical nodes.
# Author: Joachim Vandewalle
# Date: 17-10-2021

import numpy as np

__all__ = ["build_output", "build_input"]

def build_output(data, colors_types, grid):
        """
        **Input**
        data
            A dictionary with the names of the micromechanical nanocell types as keys. The corresponding values are
            dictionaries which contain all of the relevant data about the cell type.
            Example: input_data["fcu"] = {"elasticity": [np.array([[[[...]]]])], "cell": ...}

        colors_types
            A dictionary with integer keys. These integers appear in the input_grid.
            The values corresponding to the keys are tuples of a color and the name of a type.
            Example: input_colors_types[1] = ("#0000FF", "fcu")

        grid
            An array containing integers, which refer to the types of micromechanical nanocells.
            Example: input_grid[kappa, lambda, mu] = 0 is an empty cell at (kappa, lambda, mu).
                     input_grid[kappa', lambda', mu'] = 1 is an fcu cell at (kappa', lambda', mu').

        **Output**
        output
            A dictionary which is ready to be stored as a .chk file.
            It contains node positions, reference node positions...
        """
        pbc = True # periodic boundary conditions

        output = {}
        
        for key, color_type in colors_types.items():
            name = color_type[1]
            color = color_type[0]
            if name in data.keys():
                type_data = data[name]
                for key_, value in type_data.items():
                    output["type" + str(key) + "/" + str(key_)] = value
            output["type" + str(key) + "/name"] = name
            output["type" + str(key) + "/color"] = color
        
        output["grid"] = grid
        
        nx, ny, nz = np.shape(grid)
        
        # Each node has at most eight neighboring cells.
        neighbor_cells = [
            ( 0, 0, 0),
            (-1, 0, 0),
            ( 0,-1, 0),
            ( 0, 0,-1),
            (-1,-1, 0),
            (-1, 0,-1),
            ( 0,-1,-1),
            (-1,-1,-1)
        ]
        # Each cell always has eight neighboring nodes.
        neighbor_nodes = [
            (0,0,0),
            (1,0,0),
            (0,1,0),
            (0,0,1),
            (1,1,0),
            (1,0,1),
            (0,1,1),
            (1,1,1)
        ]

        # Get majority type in the grid.
        index_maj_type = np.argmax(np.bincount(np.array(grid.flatten(), dtype=int))[1:]) + 1
        maj_type = colors_types[index_maj_type][1]
        maj_type_data = data[maj_type]

        # Get dimensions of majority type cell.
        dx, dy, dz = np.diag(maj_type_data["cell"][0])
        
        if pbc:
            nx_nodes = nx
            ny_nodes = ny
            nz_nodes = nz
        else:
            nx_nodes = nx + 1
            ny_nodes = ny + 1
            nz_nodes = nz + 1
        
        
        # Avoid nested for-loops by keeping the coordinates of the nodes in a 1D list.
        nodes_idxs = []
        for k in range(nx_nodes):
            for l in range(ny_nodes):
                for m in range(nz_nodes):
                    for neighbor_cell in neighbor_cells:
                        kappa = k + neighbor_cell[0]
                        lambda_ = l + neighbor_cell[1]
                        mu = m + neighbor_cell[2]
                        if grid[(kappa, lambda_, mu)] != 0:
                            nodes_idxs.append((k, l, m))
                            break
        nnodes = len(nodes_idxs)
        
        
        # Avoid nested for-loops by keeping the coordinates of the cells in a 1D list.
        cells_idxs = []
        cells_types = []
        for kappa in range(nx):
            for lambda_ in range(ny):
                for mu in range(nz):
                    # Ensure that there is a cell present at (kappa, lambda, mu).
                    if grid[(kappa, lambda_, mu)] != 0:
                        cells_idxs.append((kappa, lambda_, mu))
                        cells_types.append(grid[(kappa, lambda_, mu)])
        ncells = len(cells_idxs)
        
        cell_matrices = []
        inv_cell_matrices = []
        elasticity_tensors = []

        # Initialize masses of the nodes.
        masses = np.zeros(nnodes)
        
        cell_ref = np.zeros((ncells, 3, 3))

        surrounding_nodes = [[] for _ in range(ncells)]
        surrounding_cells = [[] for _ in range(nnodes)]
        
        # Iterate over each cell.
        for cell_index, cell_idxs in enumerate(cells_idxs):
            
            kappa = cell_idxs[0]
            lambda_ = cell_idxs[1]
            mu = cell_idxs[2]
            
            index_type = grid[(kappa, lambda_, mu)]
            color, type_ = colors_types[index_type]
            data_type = data[type_]
            
            cell_ref[cell_index, :, :] = np.array([[dx, 0.0, 0.0],
                                                   [0.0, dy, 0.0],
                                                   [0.0, 0.0, dz]])
            cell_matrices.append(data_type["cell"])
            inv_cell_matrices.append([np.linalg.inv(cell) for cell in data_type["cell"]])
            elasticity_tensors.append(data_type["elasticity"])      

            # Iterate over the eight neighboring nodes of the cell.
            for neighbor_index, neighbor_node in enumerate(neighbor_nodes):

                # Consider node (k, l, m).
                k = (kappa + neighbor_node[0]) % nx_nodes
                l = (lambda_ + neighbor_node[1]) % ny_nodes
                m = (mu + neighbor_node[2]) % nz_nodes
                
                # Go to the index of node (k, l, m).
                for node_index, node_idxs in enumerate(nodes_idxs):
                    if k == node_idxs[0] and l == node_idxs[1] and m == node_idxs[2]:
                        surrounding_nodes[cell_index].append((neighbor_index, node_index))
                        surrounding_cells[node_index].append((neighbor_index, cell_index))
                        masses[node_index] += 0.125*data_type["mass"]
                        break 
        
        # Initialize the positions of the nodes.
        pos = np.zeros((nnodes, 3))
        pos_ref = np.zeros((nnodes, 3))

        # Iterate over each node.
        for node_index, node_idxs in enumerate(nodes_idxs):
            
            # Consider node (k, l, m).
            k = node_idxs[0]
            l = node_idxs[1]
            m = node_idxs[2]
            
            # The initial positions of the nodes are those of a rectangular grid.
            pos[node_index, :] += np.array([k*dx, l*dy, m*dz])
            pos_ref[node_index, :] += np.array([k*dx, l*dy, m*dz])
        

        output["pos"] = pos
        output["pos_ref"] = pos_ref
        output["cell_ref"] = cell_ref

        output["equilibrium_cell_matrices"] = cell_matrices
        output["equilibrium_inv_cell_matrices"] = inv_cell_matrices
        output["elasticity_tensors"] = elasticity_tensors

        output["surrounding_cells"] = surrounding_cells
        output["surrounding_nodes"] = surrounding_nodes

        output["masses"] = masses
        
        return output


def build_input(output):
    
    data = {}
    colors_types = {}
    
    grid = output["grid"]

    temp = {}
    for field, value in output.items():
        if "type" in field:
            field_lst = field.split("/")
            key = int(field_lst[0][4:])
            key_ = field_lst[1]
            if key not in temp.keys():
                temp[key] = []
            temp[key].append((key_, value))
    
    for key, tups in temp.items():
        type_dict = {}
        for tup in tups:
            if tup[0] == "name":
                name = tup[1]
            elif tup[0] == "color":
                color = tup[1]
            else:
                type_dict[tup[0]] = tup[1]
        if key != 0:
            data[name] = type_dict
        colors_types[key] = (color, name)
            
    
    return data, colors_types, grid


            



