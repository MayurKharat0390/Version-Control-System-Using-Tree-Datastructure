from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from .vcs_core import Repository

repo = Repository()

@csrf_exempt
def index(request):
    return render(request, 'vcs_app/index.html')

@csrf_exempt
def reset_repo(request):
    if request.method == 'POST':
        repo.reset()
        return JsonResponse({'status': 'success', 'message': 'Tree erased successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def create_commit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', 'No message')
            commit = repo.create_commit(message)
            return JsonResponse({
                'status': 'success',
                'commit_id': commit.id,
                'message': commit.message,
                'timestamp': commit.timestamp
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def create_branch(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Branch name required'}, status=400)
            
            success, msg = repo.create_branch(name)
            if success:
                return JsonResponse({'status': 'success', 'message': msg})
            else:
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            branch_name = data.get('branch_name')
            if not branch_name:
                return JsonResponse({'status': 'error', 'message': 'Branch name required'}, status=400)
            
            success, msg = repo.checkout(branch_name)  # Note: repo.checkout logic needs to update HEAD
            if success:
                 return JsonResponse({'status': 'success', 'message': msg})
            else:
                 return JsonResponse({'status': 'error', 'message': msg}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def get_log(request):
    """Linear history from HEAD"""
    log = repo.get_log()
    return JsonResponse({'log': log})

def get_full_history(request):
    """Global history via DFS"""
    log = repo.get_full_history_dfs()
    return JsonResponse({'log': log})

def get_bfs_levels(request):
    """Level-wise view via BFS"""
    levels = repo.get_level_view_bfs()
    return JsonResponse({'levels': levels})

@csrf_exempt
def search_commit(request):
    """DFS-based commit search"""
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query')
        node = repo.find_commit_dfs(query)
        if node:
            return JsonResponse({'status': 'success', 'commit': node.get_details()})
        return JsonResponse({'status': 'error', 'message': 'Commit not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def get_lca(request):
    """Find LCA of two nodes"""
    if request.method == 'POST':
        data = json.loads(request.body)
        id1 = data.get('id1')
        id2 = data.get('id2')
        lca = repo.get_lca(id1, id2)
        if lca:
            return JsonResponse({'status': 'success', 'lca': lca})
    return JsonResponse({'status': 'error', 'message': 'LCA not found'}, status=404)

def get_node_analytics(request, commit_id):
    """Metrics: Depth, Path to Root, and Subtree (DFS)"""
    metrics = repo.get_node_metrics(commit_id)
    subtree = repo.get_subtree(commit_id)
    if metrics:
        return JsonResponse({
            'status': 'success',
            'metrics': metrics,
            'subtree': subtree
        })
    return JsonResponse({'status': 'error', 'message': 'Node not found'}, status=404)

def get_tree_data(request):
    tree = repo.get_tree_data()
    status = repo.get_status()
    return JsonResponse({'tree': tree, 'status': status})


# =============================================================================
# GRAPH API ENDPOINTS (new)
# =============================================================================

@csrf_exempt
def merge_branches(request):
    """GRAPH OPERATION: Create a merge commit with 2 parents (DAG cross-edge)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            source = data.get('source_branch')
            target = data.get('target_branch')
            if not source or not target:
                return JsonResponse({'status': 'error', 'message': 'source_branch and target_branch required'}, status=400)
            success, result = repo.merge_branches(source, target)
            if success:
                return JsonResponse({'status': 'success', 'result': result})
            return JsonResponse({'status': 'error', 'message': result}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def get_graph_data(request):
    """Returns full DAG adjacency list for graph (D3) visualization"""
    return JsonResponse(repo.get_graph_data())


@csrf_exempt
def get_shortest_path(request):
    """GRAPH ALGORITHM: BFS Shortest Path between two commit IDs"""
    if request.method == 'POST':
        data = json.loads(request.body)
        id1 = data.get('id1')
        id2 = data.get('id2')
        path = repo.get_shortest_path(id1, id2)
        if path:
            return JsonResponse({'status': 'success', 'path': path, 'length': len(path) - 1})
        return JsonResponse({'status': 'error', 'message': 'No path found between the given commits'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def get_topo_sort(request):
    """GRAPH ALGORITHM: Topological ordering via Kahn's Algorithm"""
    order = repo.get_topo_sort()
    return JsonResponse({'status': 'success', 'order': order})


def get_reachable(request, commit_id):
    """GRAPH ALGORITHM: DFS Reachability — all commits reachable from commit_id"""
    reachable = repo.get_reachable_from(commit_id)
    return JsonResponse({'status': 'success', 'reachable': reachable, 'count': len(reachable)})


def check_dag(request):
    """Validates the commit graph has no cycles (should always be True in a healthy VCS)"""
    is_valid = repo.check_is_dag()
    return JsonResponse({
        'status': 'success',
        'is_dag': is_valid,
        'message': '\u2705 Valid DAG \u2014 No cycles detected' if is_valid else '\u274c Cycle detected!'
    })
