import os.path as osp
import os
import random

# globals
dest_names = ['bofa', 'church', 'gas_station', 'high_school', 'mcdonalds']

class Node(object):
  def __init__(self, id, lat, lng, im_idx, city_name, nbrs=[]):
    """
    :param id: string
    :param lat: float
    :param lng: float
    :param im_idx: int
    :param city_name: string
    :param nbrs: [id0, id1, ...]
    """
    self.id = id
    self.im_idx = im_idx
    self.lat = lat
    self.lng = lng
    self.city_name = city_name
    self.nbrs = nbrs

def node_img_path(n):
  """
  :return: path to image represented by this node
  """
  im_dir = osp.join('..', 'data', 'dataset', n.city_name, 'images')
  node_id = n.id.split('_')[0]
  im_path = osp.join(im_dir, '{:s}_{:d}.png'.format(node_id, n.im_idx))
  return im_path

def heading2str(h):
  """converts the heading to NSEW string"""
  if (h < 45) and (h >= 315):
    return 'N'
  elif (h < 135) and (h >= 45):
    return 'E'
  elif (h < 225) and (h >= 135):
    return 'S'
  else:
    return 'W'

def other_directions(dir):
  if dir == 'N':
    other_dirs = random.shuffle(['S', 'E', 'W'])
  elif dir == 'S':
    other_dirs = random.shuffle(['N', 'E', 'W'])
  elif dir == 'E':
    other_dirs = random.shuffle(['S', 'N', 'W'])
  elif dir == 'W':
    other_dirs = random.shuffle(['S', 'E', 'N'])
  else:
    raise ValueError
  return other_dirs

class City(object):
  def __init__(self, name):
    self.name = name
    self.nodes = {}
    self.dsts = {k: [] for k in dest_names}
    self.data_path = osp.join('..', 'data', 'dataset', self.name)

  def construct(self):
    """
    creates the city graph
    :return: nothing
    """
    # collect info about nodes
    nodes_path = osp.join(self.data_path, 'nodes')
    nodes = {}
    for nodes_filename in os.listdir(nodes_path):
      with open(osp.join(nodes_path, nodes_filename), 'r') as f:
        lines = [l.rstrip() for l in f]
        lines = lines[3:]
        for l in lines:
          node_id, lat, lng = l.split(',')
          nodes[node_id] = (float(lat), float(lng))

    # collect info about links
    links_path = osp.join(self.data_path, 'nodes')
    links = {}
    for links_filename in os.listdir(links_path):
      node_id = links_filename.split('.')[0]
      node_links = []
      with open(osp.join(links_path, links_filename), 'r') as f:
        lines = [l.rstrip() for l in f]
        for im_idx, l in enumerate(lines):
          nbr_id, heading, dist = l.split(',')
          node_links.append((nbr_id, float(heading), float(dist), im_idx))
      links[node_id] = node_links

    # construct the graph as a dict
    print('constructing inital graph...')
    for node_id, [lat, lng] in nodes.items():
      if not node_id in links:
        continue

      for link in links[node_id]:
        nbr_id, heading, dist, im_idx = link
        heading = heading2str(heading)
        n = Node(id='{:s}_{:s}'.format(node_id, heading), lat=lat, lng=lng,
          im_idx=im_idx, city_name=self.name,
          nbrs=['{:s}_{:s}'.format(nbr_id, heading)])
        self.nodes[n.id] = n

    # fix neighbours that don't have an image e.g. T-junction
    print('fixing neighbours...')
    for node in self.nodes.values():
      for idx, nbr_id in enumerate(node.nbrs):
        if nbr_id not in self.nodes:
          # try other directions
          nbr_id, dir = nbr_id.split('_')
          other_dirs = other_directions(dir)
          for other_dir in other_dirs:
            other_nbr_id = '{:s}_{:s}'.format(nbr_id, other_dir)
            if other_nbr_id in self.nodes:
              self.nodes[node.id].nbrs[idx] = other_nbr_id
              break
          else:  # no other directions were valid
            del self.nodes[node.id].nbrs[idx]

    # add turning links
    print('adding turning links...')


  def path(self, n, dest_name):
    """
    returns A* path from node to the nearest (straight line) destination
    :param n: Node
    :param dest_name:
    :return: list of Node
    """
    assert dest_name in dest_names
    return []