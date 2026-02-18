import datetime

class Commit:
    def __init__(self, unique_id, message, parent=None):
        self.unique_id = unique_id
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()
        self.parent = parent
        self.children = []
    
    def to_dict(self):
        """Recursively convert the tree (or subtree) to a dictionary for JSON serialization."""
        return {
            "id": self.unique_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "children": [child.to_dict() for child in self.children]
        }
    
    def get_details(self):
        """Get details for a single node without recursion."""
        return {
            "id": self.unique_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "parentId": self.parent.unique_id if self.parent else None,
            "childrenCount": len(self.children)
        }

class Repository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Repository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Create root commit
        self.root = Commit("root", "Initial Commit")
        self.head = self.root
        self.branches = {"main": self.root}
        self.current_branch = "main"
        self.commits_map = {"root": self.root}  # Map for O(1) lookup
        self.commit_counter = 0

    def get_new_id(self):
        self.commit_counter += 1
        return f"c{self.commit_counter}"

    def create_commit(self, message):
        # validation: single parent rule enforced by structure
        # O(1) Commit
        new_id = self.get_new_id()
        new_commit = Commit(new_id, message, parent=self.head)
        
        # Add to parent's children
        self.head.children.append(new_commit)
        
        # Move HEAD to new commit
        self.head = new_commit
        
        # Update current branch pointer
        if self.current_branch:
            self.branches[self.current_branch] = new_commit
            
        # Add to map for quick lookup
        self.commits_map[new_id] = new_commit
        
        return new_commit

    def create_branch(self, branch_name):
        # O(1) Branch Creation
        if branch_name in self.branches:
            return False, "Branch already exists"
        
        self.branches[branch_name] = self.head
        return True, "Branch created"

    def checkout(self, branch_name):
        # O(1) Checkout
        if branch_name not in self.branches:
            return False, "Branch does not exist"
        
        self.head = self.branches[branch_name]
        self.current_branch = branch_name
        return True, f"Switched to branch {branch_name}"

    def get_log(self):
        # O(n) Traversal
        log = []
        current = self.head
        while current:
            log.append(current.get_details())
            current = current.parent
        return log

    def get_tree_data(self):
        # Return full tree structure for visualization
        return self.root.to_dict()

    def get_status(self):
         return {
            "current_branch": self.current_branch,
            "head_id": self.head.unique_id,
            "branches": {k: v.unique_id for k, v in self.branches.items()}
        }

