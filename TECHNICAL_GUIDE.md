# 📘 Version Control System (VCS) - Technical Implementation Guide

This document provides a comprehensive breakdown of the classes, functions, and algorithms used in the Version Control System. It is designed to help you explain the code confidently and understand the underlying Computer Science concepts.

---

## 1. System Theme: Tree vs. Directed Acyclic Graph (DAG)

### The Concept
*   **Initial State (Tree)**: In a simple history, every commit has exactly one parent. This forms a **General Rooted Tree**.
*   **Advanced State (DAG)**: When we introduce **Merge Commits**, a single commit can have **two parents**. Mathematically, this transitions the data structure into a **Directed Acyclic Graph (DAG)**.
    *   **Directed**: Relationships (edges) have a specific direction (Parent -> Child).
    *   **Acyclic**: There are no cycles. You can never follow a path of commits and end up back where you started (no "time travel").

---

## 2. Core Module: `vcs_core.py`

### Class: `Commit`
**The Data Node**
*   **Role**: Represents a single "save point" in history.
*   **Key Attributes**:
    *   `id`: A unique identifier (e.g., "root", "c1").
    *   `parent`: Link to the primary parent node.
    *   `merge_parent`: Link to the second parent (used only for merge commits).
    *   `children`: A list of nodes that were created from this commit.
*   **Presentation Tip**: Explain this as a "Node in a Linked Structure."

### Class: `CommitGraph`
**The Adjacency List Manager**
This class handles all complex graph logic using **Adjacency Lists**.
*   **`self.adj` (In-degree)**: Maps a node ID to its parents. Used for traversing backward in time.
*   **`self.radj` (Out-degree)**: Maps a node ID to its children. Used for traversing forward in time.

#### 🚀 Key Algorithms (The "Main Event")

1.  **Topological Sort (Kahn’s Algorithm)**
    *   **What it is**: Finds a linear ordering of nodes such that for every directed edge $U \to V$, $U$ comes before $V$.
    *   **Why use it?**: To determine the "Logical Build Order." In VCS, it ensures parents are always listed before their children.
    *   **How it works**: It repeatedly "plucks" nodes that have 0 incoming edges (no dependencies left) and adds them to the list.

2.  **BFS (Shortest Path)**
    *   **What it is**: Breadth-First Search.
    *   **Why use it?**: To find the minimum number of "hops" between two commits.
    *   **Confidence Tip**: BFS is guaranteed to find the shortest path in an unweighted graph because it explores all nodes at distance 1, then all at distance 2, and so on.

3.  **DFS (Reachability)**
    *   **What it is**: Depth-First Search.
    *   **Why use it?**: To check if commit $X$ is an ancestor of commit $Y$.
    *   **How it works**: It dives deep into one branch until it hits the end, then backtracks. It's efficient for checking "can I get there from here?"

4.  **Cycle Detection (3-Color Marking)**
    *   **White**: Unvisited.
    *   **Gray**: Currently visiting (on the recursion stack).
    *   **Black**: Fully visited.
    *   **The Logic**: If we ever encounter a **Gray** node while traversing, we have found a **Cycle**. In a VCS, this shouldn't happen!

---

## 3. Web Module: `views.py`

This module acts as the **Controller**. It takes HTTP requests from the browser and calls the appropriate method in the `Repository` class.
*   **`merge_branches`**: Core logic for combining history.
*   **`get_graph_data`**: Serializes the `CommitGraph` into JSON format for the frontend.
*   **`check_dag`**: Runs the cycle detection and returns a "True/False" status.

---

## 4. Frontend Module: `index.html`

### Visualization Engines
1.  **Three.js (The 3D Tree)**:
    *   Uses a **Hierarchical Tree Layout**.
    *   Positions nodes in 3D space based on their depth in the tree.
    *   Best for visualizing "Branching."

2.  **D3.js (The 2D DAG)**:
    *   Uses a **Hierarchical SVG Layout**.
    *   **The Custom Trick**: I implemented a layout where the $Y$ coordinate is strictly determined by the node's **Topological Level**. This makes all arrows point generally in one direction (Top to Bottom), making even complex merges look clean.

---

## 5. Summary "Elevator Pitch" for your Project

> "My project demonstrates a Version Control System implemented using **Advanced Data Structures**. It transitions from a **General Rooted Tree** to a **Directed Acyclic Graph (DAG)** to support merge operations. I've implemented core graph algorithms like **Kahn's Topological Sort** for history ordering, **BFS** for shortest path analysis, and **DFS** for reachability and cycle detection. The UI provides a dual-view: a **3D immersive tree** using Three.js and a **clean hierarchical graph** using D3.js."

---
