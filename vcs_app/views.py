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
def create_commit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', 'No message')
            commit = repo.create_commit(message)
            return JsonResponse({
                'status': 'success',
                'commit_id': commit.unique_id,
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
    log = repo.get_log()
    return JsonResponse({'log': log})

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
