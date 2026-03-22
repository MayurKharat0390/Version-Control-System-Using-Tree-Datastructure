import datetime
import json
import os
from collections import deque

STORAGE_FILE = "vcs_registry.json"

# =============================================================================
# DATA STRUCTURE: General Tree Node (Commit)
# Represents a single unit of work in the Version Control System.
# Follows academic node-based design principles.
# =============================================================================
class Commit:
    """
    Classical Tree Node structure.
    In academic terms, this is a General Rooted Tree Node.
    """
    def __init__(self, message, commit_id):
        # Unique Identifier for the Node
        # Time Complexity: O(1)
        self.id = commit_id 
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()
        
        # Pointer to Parent (Tree property: each node has exactly one parent)
        # Using None for the Root node.
        self.parent = None 
        
        # Pointers to Children (Tree property: a node can have multiple children)
        # Implemented using a list to store node references (simulating an array of pointers).
        self.children = []

    def get_details(self):
        """
        O(1) Operation: Retrieves node data without traversal.
        Used for displaying current state or single log entry.
        """
        parent_id = None
        # Explicit pointer check for parent existence
        if self.parent is not None:
             # Accessing parent property (Reference lookup)
            parent_id = self.parent.id
            
        return {
            "id": self.id,
            "message": self.message,
            "timestamp": self.timestamp,
            "parentId": parent_id,
            "childrenCount": len(self.children)
        }

# =============================================================================
# CONTROLLER: Repository (Manages Tree Operations)
# Handles physical object references (pointers) and structural logic.
# =============================================================================
class Repository:
    """
    Data Structure Controller for the Rooted Tree.
    Manages head pointers, traversals, and structural integrity.
    """
    _instance = None

    def reset(self):
        """
        DATA STRUCTURE OPERATION: Re-initialization
        Time Complexity: O(1) pointer resets
        Clears all node references and starts the Tree from a fresh root.
        """
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        self._initialize()

    def __new__(cls):
        # Singleton Pattern ensures one Tree structure exists in memory
        if cls._instance is None:
            cls._instance = super(Repository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # O(1) Space: Initializing the Root node of the General Tree
        self.root = Commit("Initial Commit", "root")
        
        # Pointer to current working node (HEAD)
        # In VCS, HEAD is the node currently being worked on.
        self.head = self.root
        
        # HashMap (Dictionary) for Branch management: 
        # Maps branch strings to direct Node references (Pointers)
        self.branches = {"main": self.root}
        self.current_branch = "main"
        
        # Auxiliary HashMap for O(1) node lookup by ID
        self.commits_map = {"root": self.root}
        self.commit_counter = 0

        # Load from disk if exists
        self.load_state()

    def save_state(self):
        """
        ADS OPERATION: Serialization
        Purpose: Persistence of Tree structure across restarts.
        """
        def serialize(node):
            return {
                "id": node.id,
                "message": node.message,
                "timestamp": node.timestamp,
                "children": [serialize(c) for c in node.children]
            }

        data = {
            "root": serialize(self.root),
            "head_id": self.head.id,
            "current_branch": self.current_branch,
            "branches": {name: node.id for name, node in self.branches.items()},
            "commit_counter": self.commit_counter
        }
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_state(self):
        """
        ADS OPERATION: Deserialization
        Purpose: Reconstruction of Tree pointers from JSON.
        """
        if not os.path.exists(STORAGE_FILE): return

        try:
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)
            
            # Reset current in-memory state
            self.commits_map = {}
            
            def deserialize(node_data, parent=None):
                commit = Commit(node_data["message"], node_data["id"])
                commit.timestamp = node_data["timestamp"]
                commit.parent = parent
                self.commits_map[commit.id] = commit
                for child_data in node_data["children"]:
                    child = deserialize(child_data, commit)
                    commit.children.append(child)
                return commit

            self.root = deserialize(data["root"])
            self.commit_counter = data["commit_counter"]
            self.current_branch = data["current_branch"]
            self.head = self.commits_map.get(data["head_id"], self.root)
            self.branches = {name: self.commits_map[cid] for name, cid in data["branches"].items()}
        except Exception as e:
            print(f"LOAD ERROR: {e}. Starting fresh.")
    def get_new_id(self):
        """O(1) Utility: Generates sequential ID for new nodes."""
        self.commit_counter += 1
        return f"c{self.commit_counter}"

    def create_commit(self, message):
        """
        DATA STRUCTURE OPERATION: Insertion (Leaf addition)
        Time Complexity: O(1)
        Space Complexity: O(1) per commit
        
        Logic:
        1. Instantiate New Node
        2. Assign Parent Link (Strict single-parent rule)
        3. Assign Child Link (Tree expansion)
        4. Reassign HEAD pointer
        """
        # Step 1: Instantiate new node with unique ID
        new_id = self.get_new_id()
        new_node = Commit(message, new_id)
        
        # Step 2: Assign parent pointer (Ensuring Strict Tree Property)
        # The new node's parent is the current HEAD.
        new_node.parent = self.head
        
        # Step 3: Add child reference to parent's children list (Tree expansion)
        # This confirms the bidirectional link between Parent and Child.
        self.head.children.append(new_node)
        
        # Step 4: Move HEAD pointer to the newly created node
        # This reflects the linear growth in the current branch.
        self.head = new_node
        
        # Step 5: Update the active branch pointer in the HashMap
        if self.current_branch is not None:
            self.branches[self.current_branch] = new_node
            
        # Step 6: Maintain lookup map for O(1) access
        self.commits_map[new_id] = new_node
        
        # PERSIST STATE
        self.save_state()
        
        return new_node

    def create_branch(self, branch_name):
        """
        DATA STRUCTURE OPERATION: Pointer Mapping
        Time Complexity: O(1)
        
        Adds a new entry to the branches HashMap, pointing to the current HEAD.
        """
        # Validation: check for duplicates in the HashMap
        if branch_name in self.branches:
            return False, "Branch already exists"
        
        # Assign new branch name to the current HEAD reference (Pointer)
        self.branches[branch_name] = self.head
        self.save_state()
        return True, "Branch created successfully"

    def checkout(self, branch_name):
        """
        DATA STRUCTURE OPERATION: Pointer Reassignment
        Time Complexity: O(1)
        
        Swaps the HEAD pointer to point to a different node in the Tree.
        """
        if branch_name not in self.branches:
            return False, "Target branch does not exist"
        
        # Physical pointer swap: HEAD now points to the branch's last node
        # Time Complexity: O(1)
        self.head = self.branches[branch_name]
        self.current_branch = branch_name
        self.save_state()
        return True, f"Switched pointer to branch: {branch_name}"

    def get_log(self):
        """
        DATA STRUCTURE OPERATION: Linear Traversal (Backtracking)
        Time Complexity: O(N) - Traversing from current node to Root
        Method: Iterative pointer hopping (No Recursion used here)
        """
        log_data = []
        # Cursor for traversal
        current_node = self.head
        
        # Traverse upwards until Root (where parent pointer is None)
        while current_node is not None:
            # Manually append node details to our results list
            details = current_node.get_details()
            log_data.append(details)
            
            # Hop to parent node (Pointer traversal)
            current_node = current_node.parent
            
        return log_data

    def get_tree_data(self):
        """
        DATA STRUCTURE OPERATION: Deep Tree Traversal (Depth-First)
        Time Complexity: O(N) where N is total nodes
        Space Complexity: O(H) recursion stack where H is tree height
        
        Returns full tree structure as a dictionary for 3D visualization.
        """
        def serialize_node(node):
            # Explicit dictionary construction (Node-level serialization)
            node_dict = {
                "id": node.id,
                "message": node.message,
                "timestamp": node.timestamp,
                "children": []
            }
            # Manually iterate through children list (Explicit Loop over List Comprehension)
            for child in node.children:
                # Perform recursive serialization step
                child_serialized = serialize_node(child)
                node_dict["children"].append(child_serialized)
            return node_dict

        # Start traversal from Root
        return serialize_node(self.root)

    def get_status(self):
        """
        O(1) Status Check: Retrieves current pointer positions from the HashMap.
        """
        branch_pointers = {}
        # Iterate through HashMap to extract branch-to-ID mappings
        for name, node in self.branches.items():
            # Get the unique ID from the node reference (Pointer)
            branch_pointers[name] = node.id
            
        return {
            "current_branch": self.current_branch,
            "head_id": self.head.id,
            "branches": branch_pointers,
            "total_commits": len(self.commits_map),
            "tree_height": self.get_tree_height()
        }

    # =========================================================================
    # CORE ADS ALGORITHMS (DFS, BFS, LCA, SEARCH)
    # Refactored for Classic Logic (as per C++ Standard implementation)
    # =========================================================================

    def get_full_history_dfs(self):
        """
        ADS ALGORITHM: DEPTH-FIRST SEARCH (DFS) - CLASSIC RECURSION
        Logic: Visit Current (Pre-order) -> Recurse into all Children
        Equivalent to: std::vector<Node*> search(Node* root) in C++
        """
        result = []
        
        def traverse(node):
            if node is None:
                return
            
            # Step 1: 'Visit' the node (Pre-order logic)
            result.append(node.get_details())
            
            # Step 2: Recursively call DFS for each 'child' pointer
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
        return result

    def get_level_view_bfs(self):
        """
        ADS ALGORITHM: BREADTH-FIRST SEARCH (BFS) - CLASSIC QUEUE Logic
        Logic: Enqueue Root -> While Queue not empty: Dequeue, Visit, Enqueue Children
        Equivalent to: std::queue<Node*> q in C++
        """
        levels = {}
        if not self.root:
            return levels
            
        # Step 1: Initialize Queue with Root and Depth indicator
        queue = deque([(self.root, 0)])
        
        while queue:
            # Step 2: Extract current node from front (O(1))
            current_node, depth = queue.popleft()
            
            # Step 3: 'Visit' the node and map it to its level
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(current_node.get_details())
            
            # Step 4: Enqueue all children for processing in next level
            for child in current_node.children:
                queue.append((child, depth + 1))
        
        return levels

    def find_commit_dfs(self, query):
        """
        ADS ALGORITHM: TREE SEARCH (DFS-BASED)
        Logic: Search entire tree recursively for a matching value.
        """
        def search(node):
            if not node:
                return None
            
            # Step 1: Check match (ID or Message)
            if node.id == query or query.lower() in node.message.lower():
                return node
                
            # Step 2: Recurse through all subtrees
            for child in node.children:
                found = search(child)
                if found:
                    return found
            return None
            
        return search(self.root)

    def get_lca(self, id1, id2):
        """
        ADS ALGORITHM: LOWEST COMMON ANCESTOR (LCA)
        Logic: Standard Path Intersection (Constant Pointer Hopping)
        Time Complexity: O(D) where D is depth
        """
        node1 = self.commits_map.get(id1)
        node2 = self.commits_map.get(id2)
        if not node1 or not node2:
            return None
        
        # Step 1: Record Path 1 from Node to Root
        path1 = set()
        curr = node1
        while curr:
            path1.add(curr.id)
            curr = curr.parent # Pointer hopping to parent
            
        # Step 2: Traverse from Node 2 to Root and find 1st intersection
        curr = node2
        while curr:
            if curr.id in path1:
                return curr.get_details() # Found common ancestor
            curr = curr.parent
            
        return None

    def get_subtree(self, commit_id):
        """
        ADS ALGORITHM: SUBTREE EXTRACTION (DFS)
        Logic: Recursively collect all descendant IDs.
        """
        start = self.commits_map.get(commit_id)
        if not start: return []
        
        subtree_ids = []
        def collect(node):
            subtree_ids.append(node.id)
            for child in node.children:
                collect(child)
        
        collect(start)
        return subtree_ids

    def get_tree_height(self):
        """
        ADS ALGORITHM: HEIGHT CALCULATION (RECURSIVE)
        Logic: Height = 1 + max(Height of Children)
        Equivalent to: return 1 + max_child_height
        """
        def calculate(node):
            if not node.children:
                return 0 # Leaf node height is 0
            
            max_child = 0
            for child in node.children:
                h = calculate(child)
                if h > max_child:
                    max_child = h
            return 1 + max_child
            
        return calculate(self.root)

    def get_node_metrics(self, commit_id):
        """
        ADS ALGORITHM: NODE ANALYTICS (DEPTH & LINEAGE)
        Logic: Iterative parent traversal to measure distance from root.
        """
        node = self.commits_map.get(commit_id)
        if not node: return None
        
        depth = 0
        lineage = []
        curr = node
        
        while curr:
            lineage.append(curr.id)
            if curr.parent:
                depth += 1
            curr = curr.parent
            
        return {
            "depth": depth,
            "path_to_root": lineage
        }
