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
    # Flatten tree or send as is? 
    # For D3/Three.js, hierarchical JSON is often good.
    # The prompt asked for: { "id": "c1", "children": [...] }
    # My repo.get_tree_data() returns exactly that.
    return JsonResponse({
        'tree': tree,
        'status': status
    })
