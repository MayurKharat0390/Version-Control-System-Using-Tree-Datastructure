import datetime
import json
import os
from collections import deque

STORAGE_FILE = "vcs_registry.json"

# =============================================================================
# DATA STRUCTURE 1: General Tree Node (Commit)
# Participates in both Tree AND Graph (DAG) structures.
# =============================================================================
class Commit:
    """
    Unified Node: works as a Tree node (single parent) and a Graph node
    (merge_parent adds the second incoming edge for merge commits).
    """
    def __init__(self, message, commit_id):
        self.id = commit_id
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()

        # --- Tree property ---
        self.parent = None          # Single primary parent (strict tree)
        self.children = []          # Child list (shared with graph)

        # --- Graph extension ---
        self.merge_parent = None    # Second parent (only set on merge commits)
        self.is_merge = False       # Flag: is this a merge commit?

    def get_details(self):
        """O(1) accessor for node metadata."""
        return {
            "id": self.id,
            "message": self.message,
            "timestamp": self.timestamp,
            "parentId": self.parent.id if self.parent else None,
            "mergeParentId": self.merge_parent.id if self.merge_parent else None,
            "is_merge": self.is_merge,
            "childrenCount": len(self.children)
        }


# =============================================================================
# DATA STRUCTURE 2: Commit Graph (DAG — Directed Acyclic Graph)
# Adjacency-list representation of the full commit history.
# Enables multi-parent (merge) commits — impossible in a pure Tree.
# =============================================================================
class CommitGraph:
    """
    Graph DS: Directed Acyclic Graph
      adj[node]  = [parent IDs]   (incoming edges)
      radj[node] = [child IDs]    (outgoing edges)

    Time complexities follow standard graph-algorithm conventions.
    """

    def __init__(self):
        self.adj = {}    # node -> [parents]
        self.radj = {}   # node -> [children]

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------

    def add_node(self, commit_id):
        """O(1) — Register an isolated node."""
        if commit_id not in self.adj:
            self.adj[commit_id] = []
            self.radj[commit_id] = []

    def add_edge(self, parent_id, child_id):
        """O(1) — Add directed edge: parent → child."""
        self.add_node(parent_id)
        self.add_node(child_id)
        if parent_id not in self.adj[child_id]:
            self.adj[child_id].append(parent_id)
        if child_id not in self.radj[parent_id]:
            self.radj[parent_id].append(child_id)

    # ------------------------------------------------------------------
    # GRAPH ALGORITHM 1: Kahn's Topological Sort (BFS-based)
    # ------------------------------------------------------------------
    def topological_sort(self):
        """
        GRAPH ALGORITHM: Kahn's Algorithm
        Time Complexity : O(V + E)
        Output          : Commits in dependency order
                          (every parent guaranteed to appear before its children)
        Logic:
          1. Compute in-degree for every node.
          2. Enqueue all zero-in-degree nodes (roots).
          3. Dequeue, record, decrement children's in-degrees; re-enqueue if 0.
        """
        in_degree = {node: len(parents) for node, parents in self.adj.items()}
        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for child in self.radj.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        return result

    # ------------------------------------------------------------------
    # GRAPH ALGORITHM 2: BFS Shortest Path
    # ------------------------------------------------------------------
    def shortest_path(self, start_id, end_id):
        """
        GRAPH ALGORITHM: BFS Shortest Path
        Time Complexity : O(V + E)
        Output          : Minimum-hop commit path, or None
        Logic:
          Standard BFS from start — first time end_id is dequeued
          gives the shortest path (fewest edges).
        """
        if start_id not in self.radj:
            return None
        visited = {start_id}
        queue = deque([(start_id, [start_id])])
        while queue:
            node, path = queue.popleft()
            if node == end_id:
                return path
            for child in self.radj.get(node, []):
                if child not in visited:
                    visited.add(child)
                    queue.append((child, path + [child]))
        return None

    # ------------------------------------------------------------------
    # GRAPH ALGORITHM 3: DFS Reachability
    # ------------------------------------------------------------------
    def get_reachable(self, start_id):
        """
        GRAPH ALGORITHM: DFS Reachability
        Time Complexity : O(V + E)
        Output          : Set of all commits reachable (forward) from start_id
        """
        visited = set()

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            for child in self.radj.get(node, []):
                dfs(child)

        dfs(start_id)
        return list(visited)

    # ------------------------------------------------------------------
    # GRAPH ALGORITHM 4: Cycle Detection (3-colour DFS)
    # ------------------------------------------------------------------
    def detect_cycle(self):
        """
        GRAPH ALGORITHM: Cycle Detection
        Time Complexity : O(V + E)
        Method          : 3-colour DFS marking (WHITE / GRAY / BLACK)
        Returns True if a cycle exists (which would break DAG property).
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in self.adj}

        def dfs(node):
            color[node] = GRAY          # currently on DFS stack
            for child in self.radj.get(node, []):
                if color.get(child, WHITE) == GRAY:
                    return True         # back-edge → cycle
                if color.get(child, WHITE) == WHITE and dfs(child):
                    return True
            color[node] = BLACK         # fully processed
            return False

        for node in self.adj:
            if color[node] == WHITE:
                if dfs(node):
                    return True
        return False

    # ------------------------------------------------------------------
    # GRAPH ALGORITHM 5: All Paths (DFS backtracking)
    # ------------------------------------------------------------------
    def get_all_paths(self, start_id, end_id):
        """
        GRAPH ALGORITHM: All Paths via DFS
        Time Complexity : O(V! worst-case)
        Output          : Every possible commit path between two nodes
        """
        all_paths = []

        def dfs(node, current_path, visited):
            if node == end_id:
                all_paths.append(list(current_path))
                return
            for child in self.radj.get(node, []):
                if child not in visited:
                    visited.add(child)
                    current_path.append(child)
                    dfs(child, current_path, visited)
                    current_path.pop()
                    visited.remove(child)

        dfs(start_id, [start_id], {start_id})
        return all_paths

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def get_adjacency_data(self):
        """Serialize full adjacency list for the API / frontend."""
        return {
            "nodes": list(self.adj.keys()),
            "edges": [
                {"from": parent, "to": child}
                for child, parents in self.adj.items()
                for parent in parents
            ],
            "adjacency_list": {
                node: {
                    "parents": self.adj.get(node, []),
                    "children": self.radj.get(node, [])
                }
                for node in self.adj
            }
        }


# =============================================================================
# CONTROLLER: Repository
# Manages Tree + Graph structures together.
# =============================================================================
class Repository:
    """
    Unified data-structure controller.
    Maintains:
      • Rooted General Tree  (commit history — parent / children pointers)
      • DAG CommitGraph      (merge topology — adjacency list)
    """
    _instance = None

    # ------------------------------------------------------------------
    # Singleton + Initialisation
    # ------------------------------------------------------------------
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Repository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def reset(self):
        """Erase persistent state and reinitialise to a fresh root."""
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        self._initialize()

    def _initialize(self):
        self.root = Commit("Initial Commit", "root")
        self.head = self.root
        self.branches = {"main": self.root}
        self.current_branch = "main"
        self.commits_map = {"root": self.root}
        self.commit_counter = 0

        # Graph layer
        self.graph = CommitGraph()
        self.graph.add_node("root")

        self.load_state()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_state(self):
        def serialize(node):
            return {
                "id": node.id,
                "message": node.message,
                "timestamp": node.timestamp,
                "is_merge": node.is_merge,
                "merge_parent_id": node.merge_parent.id if node.merge_parent else None,
                "children": [serialize(c) for c in node.children]
            }

        data = {
            "root": serialize(self.root),
            "head_id": self.head.id,
            "current_branch": self.current_branch,
            "branches": {name: node.id for name, node in self.branches.items()},
            "commit_counter": self.commit_counter,
            "graph": {
                "adj": self.graph.adj,
                "radj": self.graph.radj
            }
        }
        try:
            with open(STORAGE_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except (IOError, OSError) as e:
            print(f"STORAGE ERROR (read-only env): {e}")

    def load_state(self):
        if not os.path.exists(STORAGE_FILE):
            return
        try:
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)

            self.commits_map = {}
            merge_parent_refs = {}

            def deserialize(node_data, parent=None):
                commit = Commit(node_data["message"], node_data["id"])
                commit.timestamp = node_data["timestamp"]
                commit.parent = parent
                commit.is_merge = node_data.get("is_merge", False)
                self.commits_map[commit.id] = commit
                mp_id = node_data.get("merge_parent_id")
                if mp_id:
                    merge_parent_refs[commit.id] = mp_id
                for child_data in node_data["children"]:
                    child = deserialize(child_data, commit)
                    commit.children.append(child)
                return commit

            self.root = deserialize(data["root"])

            # Resolve merge-parent references (post-order)
            for cid, mp_id in merge_parent_refs.items():
                if mp_id in self.commits_map:
                    self.commits_map[cid].merge_parent = self.commits_map[mp_id]

            self.commit_counter = data["commit_counter"]
            self.current_branch = data["current_branch"]
            self.head = self.commits_map.get(data["head_id"], self.root)
            self.branches = {
                name: self.commits_map[cid]
                for name, cid in data["branches"].items()
            }

            if "graph" in data:
                self.graph.adj = data["graph"]["adj"]
                self.graph.radj = data["graph"]["radj"]
            else:
                # Migration: rebuild graph from existing tree data
                self._rebuild_graph_from_tree()

        except Exception as e:
            print(f"LOAD ERROR: {e}. Starting fresh.")

    def _rebuild_graph_from_tree(self):
        """Migration helper: reconstruct adjacency list from the tree."""
        self.graph = CommitGraph()

        def traverse(node):
            self.graph.add_node(node.id)
            for child in node.children:
                self.graph.add_edge(node.id, child.id)
                traverse(child)

        traverse(self.root)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def get_new_id(self):
        self.commit_counter += 1
        return f"c{self.commit_counter}"

    # ------------------------------------------------------------------
    # TREE OPERATIONS
    # ------------------------------------------------------------------

    def create_commit(self, message):
        """
        TREE OPERATION: Insert leaf node
        Also registers node + edge in the Graph layer.
        Time Complexity: O(1)
        """
        new_id = self.get_new_id()
        new_node = Commit(message, new_id)
        new_node.parent = self.head
        self.head.children.append(new_node)
        self.head = new_node

        if self.current_branch:
            self.branches[self.current_branch] = new_node
        self.commits_map[new_id] = new_node

        # Graph: register node + directed edge
        self.graph.add_node(new_id)
        if new_node.parent:
            self.graph.add_edge(new_node.parent.id, new_id)

        self.save_state()
        return new_node

    def create_branch(self, branch_name):
        """TREE OPERATION: O(1) HashMap entry"""
        if branch_name in self.branches:
            return False, "Branch already exists"
        self.branches[branch_name] = self.head
        self.save_state()
        return True, "Branch created successfully"

    def checkout(self, branch_name):
        """TREE OPERATION: O(1) HEAD pointer swap"""
        if branch_name not in self.branches:
            return False, "Target branch does not exist"
        self.head = self.branches[branch_name]
        self.current_branch = branch_name
        self.save_state()
        return True, f"Switched to branch: {branch_name}"

    def get_log(self):
        """TREE TRAVERSAL: Backtrack from HEAD → root  O(N)"""
        log_data = []
        current_node = self.head
        while current_node is not None:
            log_data.append(current_node.get_details())
            current_node = current_node.parent
        return log_data

    def get_tree_data(self):
        """TREE TRAVERSAL: Full DFS pre-order serialisation  O(N)"""
        def serialize_node(node):
            return {
                "id": node.id,
                "message": node.message,
                "timestamp": node.timestamp,
                "is_merge": node.is_merge,
                "children": [serialize_node(c) for c in node.children]
            }
        return serialize_node(self.root)

    def get_status(self):
        return {
            "current_branch": self.current_branch,
            "head_id": self.head.id,
            "branches": {name: node.id for name, node in self.branches.items()},
            "total_commits": len(self.commits_map),
            "tree_height": self.get_tree_height()
        }

    # ------------------------------------------------------------------
    # GRAPH OPERATIONS (new)
    # ------------------------------------------------------------------

    def merge_branches(self, source_branch, target_branch):
        """
        GRAPH OPERATION: Create Merge Commit (2-parent node)
        This cross-edge between branches is only possible in a DAG —
        not in a pure Tree.
        Time Complexity: O(1) for commit creation
        """
        if source_branch not in self.branches:
            return False, f"Source branch '{source_branch}' not found"
        if target_branch not in self.branches:
            return False, f"Target branch '{target_branch}' not found"
        if source_branch == target_branch:
            return False, "Cannot merge a branch into itself"

        source_tip = self.branches[source_branch]
        target_tip = self.branches[target_branch]

        # Calculate LCA for context info
        lca = self.get_lca(source_tip.id, target_tip.id)

        # Create merge commit node
        new_id = self.get_new_id()
        merge_node = Commit(f"Merge '{source_branch}' into '{target_branch}'", new_id)
        merge_node.is_merge = True

        # Primary parent: target branch tip  (tree-compatible)
        # Append to target's children so tree serialization includes this node ONCE
        merge_node.parent = target_tip
        target_tip.children.append(merge_node)

        # Secondary parent = source branch tip (Graph-only edge)
        # NOTE: Do NOT append to source_tip.children — that would cause the merge
        # commit to appear TWICE in the tree serialization (once under each parent).
        # The merge relationship is captured exclusively in the DAG adjacency list.
        merge_node.merge_parent = source_tip

        self.commits_map[new_id] = merge_node
        self.branches[target_branch] = merge_node
        self.head = merge_node
        self.current_branch = target_branch

        # Graph: add node + TWO directed edges
        self.graph.add_node(new_id)
        self.graph.add_edge(target_tip.id, new_id)   # primary edge
        self.graph.add_edge(source_tip.id, new_id)   # merge (cross) edge

        self.save_state()
        return True, {
            "merge_commit": merge_node.get_details(),
            "lca": lca
        }

    def get_graph_data(self):
        """Returns full graph data for D3 DAG visualisation."""
        node_details = {
            cid: {
                "id": cid,
                "message": commit.message,
                "timestamp": commit.timestamp,
                "is_merge": commit.is_merge,
                "is_head": (cid == self.head.id),
                "mergeParentId": commit.merge_parent.id if commit.merge_parent else None
            }
            for cid, commit in self.commits_map.items()
        }
        graph_raw = self.graph.get_adjacency_data()
        return {
            **graph_raw,
            "node_details": node_details,
            "branch_tips": {name: node.id for name, node in self.branches.items()},
            "head_id": self.head.id,
            "current_branch": self.current_branch
        }

    # ------------------------------------------------------------------
    # TREE ALGORITHMS (preserved from original)
    # ------------------------------------------------------------------

    def get_full_history_dfs(self):
        """DFS pre-order traversal of entire tree."""
        result = []

        def traverse(node):
            if node is None:
                return
            result.append(node.get_details())
            for child in node.children:
                traverse(child)

        traverse(self.root)
        return result

    def get_level_view_bfs(self):
        """BFS level-order traversal."""
        levels = {}
        if not self.root:
            return levels
        queue = deque([(self.root, 0)])
        while queue:
            current_node, depth = queue.popleft()
            levels.setdefault(depth, []).append(current_node.get_details())
            for child in current_node.children:
                queue.append((child, depth + 1))
        return levels

    def find_commit_dfs(self, query):
        """DFS search by ID or message substring."""
        def search(node):
            if not node:
                return None
            if node.id == query or query.lower() in node.message.lower():
                return node
            for child in node.children:
                found = search(child)
                if found:
                    return found
            return None

        return search(self.root)

    def get_lca(self, id1, id2):
        """LCA via path-intersection. O(D) where D = tree depth."""
        node1 = self.commits_map.get(id1)
        node2 = self.commits_map.get(id2)
        if not node1 or not node2:
            return None
        path1 = set()
        curr = node1
        while curr:
            path1.add(curr.id)
            curr = curr.parent
        curr = node2
        while curr:
            if curr.id in path1:
                return curr.get_details()
            curr = curr.parent
        return None

    def get_subtree(self, commit_id):
        """DFS subtree collection."""
        start = self.commits_map.get(commit_id)
        if not start:
            return []
        subtree_ids = []

        def collect(node):
            subtree_ids.append(node.id)
            for child in node.children:
                collect(child)

        collect(start)
        return subtree_ids

    def get_tree_height(self):
        """Recursive height calculation. O(N)."""
        def calculate(node):
            if not node.children:
                return 0
            return 1 + max(calculate(c) for c in node.children)

        return calculate(self.root)

    def get_node_metrics(self, commit_id):
        """Depth + path-to-root via parent traversal."""
        node = self.commits_map.get(commit_id)
        if not node:
            return None
        depth, lineage, curr = 0, [], node
        while curr:
            lineage.append(curr.id)
            if curr.parent:
                depth += 1
            curr = curr.parent
        return {"depth": depth, "path_to_root": lineage}

    # ------------------------------------------------------------------
    # GRAPH ALGORITHMS (new)
    # ------------------------------------------------------------------

    def get_topo_sort(self):
        """Topological sort using Kahn's Algorithm."""
        order = self.graph.topological_sort()
        return [self.commits_map[cid].get_details() for cid in order if cid in self.commits_map]

    def get_shortest_path(self, id1, id2):
        """BFS shortest path — tries both directions."""
        path = self.graph.shortest_path(id1, id2)
        if not path:
            rev = self.graph.shortest_path(id2, id1)
            if rev:
                path = list(reversed(rev))
        return path

    def get_reachable_from(self, commit_id):
        """DFS reachability from a given commit."""
        return self.graph.get_reachable(commit_id)

    def check_is_dag(self):
        """Returns True if the commit graph is a valid DAG (no cycles)."""
        return not self.graph.detect_cycle()

    def get_all_paths_between(self, id1, id2):
        """All paths between two commits via DFS backtracking."""
        return self.graph.get_all_paths(id1, id2)
