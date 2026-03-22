import datetime
from collections import deque

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
    # ADVANCED TREE OPERATIONS (DFS, BFS, LCA)
    # =========================================================================

    def get_full_history_dfs(self):
        """
        ADS OPERATION: Depth-First Search (DFS)
        Purpose: System-wide full history exploration.
        Time Complexity: O(N)
        """
        result = []
        def dfs(node):
            # Process current node (Pre-order)
            result.append(node.get_details())
            # Recursively visit all children
            for child in node.children:
                dfs(child)
        
        dfs(self.root)
        return result

    def get_level_view_bfs(self):
        """
        ADS OPERATION: Breadth-First Search (BFS)
        Purpose: Analyze structural density level-by-level.
        Time Complexity: O(N)
        """
        levels = {}
        # Explicit Queue-based traversal
        queue = deque([(self.root, 0)])
        
        while queue:
            node, d = queue.popleft()
            if d not in levels:
                levels[d] = []
            levels[d].append(node.get_details())
            
            # Add all children to queue for next level processing
            for child in node.children:
                queue.append((child, d + 1))
        
        return levels

    def find_commit_dfs(self, query):
        """
        ADS OPERATION: Search via DFS
        Purpose: Locate a specific commit in global history.
        """
        def search(node):
            # Check ID or Message match
            if node.id == query or query.lower() in node.message.lower():
                return node
            for child in node.children:
                found = search(child)
                if found:
                    return found
            return None
            
        return search(self.root)

    def get_lca(self, id1, id2):
        """
        ADS OPERATION: Lowest Common Ancestor (LCA)
        Purpose: Identify divergence point of two branches.
        Method: Path Reconstruction (Pointer-based)
        Time Complexity: O(D) where D is depth
        """
        node1 = self.commits_map.get(id1)
        node2 = self.commits_map.get(id2)
        if not node1 or not node2:
            return None
        
        # Step 1: Trace path from node1 to Root and store in HashSet
        path1 = set()
        curr = node1
        while curr:
            path1.add(curr.id)
            curr = curr.parent
            
        # Step 2: Trace path from node2 to Root until an ID exists in path1
        curr = node2
        while curr:
            if curr.id in path1:
                return curr.get_details()
            curr = curr.parent
        return None

    def get_subtree(self, commit_id):
        """
        ADS OPERATION: Subtree Extraction (DFS)
        Purpose: Visualize descendants of a specific commit.
        """
        start_node = self.commits_map.get(commit_id)
        if not start_node: return []
        
        subtree = []
        def dfs(node):
            subtree.append(node.id)
            for child in node.children:
                dfs(child)
        dfs(start_node)
        return subtree

    def get_tree_height(self):
        """
        ADS OPERATION: Height Calculation (Recursive)
        Time Complexity: O(N)
        """
        def calculate_height(node):
            if not node.children:
                return 0
            # Height = 1 + max height of subtrees
            return 1 + max(calculate_height(child) for child in node.children)
            
        return calculate_height(self.root)

    def get_node_metrics(self, commit_id):
        """
        ADS OPERATION: Node Metrics (Depth)
        """
        node = self.commits_map.get(commit_id)
        if not node: return None
        
        # Calculate Depth (Path to Root)
        depth = 0
        curr = node
        path = []
        while curr:
            path.append(curr.id)
            if curr.parent:
                depth += 1
            curr = curr.parent
            
        return {
            "depth": depth,
            "path_to_root": path
        }
