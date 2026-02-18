# Tree-Based Version Control System with 3D Visualization

A simplified Version Control System (VCS) built to demonstrate **Advanced Data Structure** concepts, specifically the **General Rooted Tree**. unlike Git which uses a Directed Acyclic Graph (DAG), this system enforces a strict tree structure where every commit has exactly one parent (except the root).

## 🚀 Key Features

*   **Strict Tree Structure**: maintained manually using pure Python classes (`Commit`, `Repository`).
*   **Core VCS Operations**:
    *   **Commit**: O(1) time complexity. Adds a child to the current HEAD.
    *   **Branch Creation**: O(1) time complexity. Maps a name to a commit pointer.
    *   **Checkout**: O(1) time complexity. Swaps the HEAD pointer.
    *   **Log**: O(N) traversal from HEAD to Root.
*   **Interactive 3D Visualization**:
    *   Built with **Three.js**.
    *   **Cyber/Tech Theme**: Deep blue background, floating data particles, and a perspective grid.
    *   **Visual Elements**: Commits are represented as cubic data blocks growing downwards.
    *   **Real-time Updates**: The tree updates dynamically as you commit and branch.

## 🛠️ Technology Stack

*   **Backend**: Django (Python) - Handles API logic and tree data structure.
*   **Frontend**: HTML5, JavaScript, Three.js - Handles the interactive 3D rendering.
*   **Data Structure**: Custom Python `Commit` nodes (No database hierarchy libraries used).

## 📦 Setup & Run

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/MayurKharat0390/Version-Control-System-Using-Tree-Datastructure.git
    cd Version-Control-System-Using-Tree-Datastructure
    ```

2.  **Install Django**:
    ```bash
    pip install django
    ```

3.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

4.  **Start the Server**:
    ```bash
    python manage.py runserver
    ```

5.  **View the App**:
    Open your browser and navigate to: `http://127.0.0.1:8000/vcs/`

## 🎮 How to Use

1.  **Commit**: Enter a message in the "Controls" panel and click **Commit**. Watch a new block appear connected to the current one.
2.  **Branch**: Enter a name (e.g., `feature-xyz`) and click **Create Branch**. A colored marker will appear on the current node.
3.  **Checkout**: Select a branch from the dropdown and click **Checkout**. Any new commits will now branch off from that point, creating a new subtree.
4.  **Explore**: Click and drag to rotate the 3D view. Scroll to zoom in/out. Hover over nodes to see details.

## 🧠 Academic Context

This project serves as a practical implementation of **General Trees**. By simplifying the complex DAG structure of real-world VCS (like Git) into a strict Tree, we can clearly visualize parent-child relationships, subtrees, and the efficiency of pointer-based operations in a hierarchical data structure.
