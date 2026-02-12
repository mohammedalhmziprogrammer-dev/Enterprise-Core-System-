import json
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Release, ReleaseApp, ReleaseModel, ReleaseService, ClientRelease
from users.models import Role, Permission
from codings.models import Coding, CodingCategory
from clients.models import Structure, Level, Beneficiary
from apps.models import App, AppVersion
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

CORE_APPS = ['users', 'activity_logs', 'clients', 'apps']  # apps is self-referential but good to have

class ReleaseService:
    @staticmethod
    @transaction.atomic
    def create_release(name, description=None, version=None, base_release=None, business_apps_labels=None):
        """
        Creates a new Release.
        - Inherits Core Apps automatically.
        - Adds selected Business Apps.
        - If base_release is provided, clones configurations.
        """
        release = Release.objects.create(
            name=name,
            descraption=description,
            version=version,
            base_release=base_release,
            status='draft'
        )

        # 1. Add Core Apps
        core_apps = App.objects.filter(is_core=True) | App.objects.filter(app_label__in=CORE_APPS)
        for app in core_apps.distinct():
            ReleaseService._add_app_to_release(release, app, is_core=True)

        # 2. Add Business Apps
        if business_apps_labels:
            biz_apps = App.objects.filter(app_label__in=business_apps_labels).exclude(app_label__in=core_apps.values_list('app_label', flat=True))
            for app in biz_apps:
                ReleaseService._add_app_to_release(release, app, is_core=False)

        # 3. Clone Base Release (if applicable) - TODO: Copy models/services config
        
        return release

    @staticmethod
    def _add_app_to_release(release, app, is_core=False):
        # Get latest version for now
        # version = AppVersion.objects.filter(app=app).order_by('-release_date').first()
        ReleaseApp.objects.get_or_create(
            release=release,
            app=app,
            defaults={'is_core': is_core}
        )
        
        # Populate Default Models
        content_types = ContentType.objects.filter(app_label=app.app_label)
        for ct in content_types:
            ReleaseModel.objects.get_or_create(
                release=release,
                app=app,
                content_type=ct
            )
            
        # Populate Services (Assuming Service Registry exists, for now placeholder)
        # ReleaseService.objects.create(...)

    @staticmethod
    def activate_release(release_id):
        release = Release.objects.get(id=release_id)
        # Validation
        core_checks = [app_label for app_label in CORE_APPS if not release.apps.filter(app_label=app_label).exists()]
        # Note: 'apps' in CORE_APPS might be redundant if the model 'App' is in 'apps' app, but for safely.
        
        # If is_core field is used, we check that too
        missing_cores = App.objects.filter(is_core=True).exclude(app_label__in=release.apps.values_list('app_label', flat=True))
        
        if missing_cores.exists():
             raise ValueError(f"Missing Core Apps: {list(missing_cores.values_list('name', flat=True))}")

        release.status = 'published'
        release.save()
        return release

    @staticmethod
    def assign_to_client(release, beneficiary_id, active_from=None):
        if release.status != 'published':
            raise ValueError("Cannot assign a draft/archived release.")
            
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        
        # Deactivate previous
        ClientRelease.objects.filter(beneficiary=beneficiary, is_active=True).update(is_active=False, active_to=timezone.now())
        
        ClientRelease.objects.create(
            release=release,
            beneficiary=beneficiary,
            is_active=True,
            active_from=active_from or timezone.now()
        )
        # Trigger Auto-Provisioning of Roles/Permissions here...


class ReleaseExportService:
    def __init__(self, release_id):
        self.release = Release.objects.get(id=release_id)

    def generate_export(self):
        data = {
            'release': {
                'name': self.release.name,
                'description': self.release.descraption,
                'version': self.release.name,
                'date': str(self.release.release_date),
                'generated_at': str(timezone.now()),
            },
            'beneficiaries': self._get_beneficiaries_data(),
            'apps': self._get_apps_data(),
            'groups': self._get_groups_data(),
            'users': self._get_users_data(),
        }
        
        json_content = json.dumps(data, indent=4, ensure_ascii=False)
        filename = f"release_{self.release.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.json"
        
        self.release.exported_file.save(filename, ContentFile(json_content))
        self.release.status = 'published'
        self.release.save()
        return self.release.exported_file.url

    def generate_source_export(self):
        import shutil
        import os
        import tempfile
        import re
        from django.conf import settings
        
        # Mapping Backend App Label -> Frontend Directory Name
        FRONTEND_MAPPING = {
            'users': 'UserManagement',
            'clients': 'ClientManagement',
            'apps': 'AppManagement',
            'activity_logs': 'LogManagement',
            'codings': 'Codings',
            'releases': 'ReleaseManagement',
            'crm': 'CRM',
        }
        
        # Mapping Backend App Label -> Frontend Route Variable Name (for cleaning App.jsx)
        ROUTE_MAPPING = {
            'users': 'UserRoutes',
            'clients': 'ClientRoutes',
            'apps': 'AppRoutes',
            'activity_logs': 'LogRoutes',
            'codings': 'CodingRoutes',
            'releases': 'ReleasesRoutes',
            'crm': 'CrmRoutes',
        }
        
        # Core Backend Apps that must always be included (System level)
        SYSTEM_APPS = ['api', 'export', 'media', 'static'] 
        
        # Get List of Allowed Apps (Backend Labels)
        allowed_apps = set([ra.app.app_label for ra in self.release.releaseapp_set.all()])
        # Ensure mandatory system apps (?) or allow release to define them? 
        # Usually 'users' and 'apps' are core. The release creation logic presumably handles this.
        # We will strictly trust the release object.
        
        # Add system folders to list of things to copy, but 'api' and 'export' are not "Release Apps"
        # so we handle them separately as folders.
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir_name = f"release_{self.release.version or self.release.id}_system"
            base_path = os.path.join(temp_dir, base_dir_name)
            os.makedirs(base_path)
            
            backend_dest = os.path.join(base_path, 'backend')
            frontend_dest = os.path.join(base_path, 'frontend')
            os.makedirs(backend_dest)
            os.makedirs(frontend_dest) 
            
            project_root = settings.BASE_DIR # c:/Server/home
            
            # =======================
            # 1. BACKEND EXPORT
            # =======================
            
            # Copy manage.py
            shutil.copy2(os.path.join(project_root, 'manage.py'), backend_dest)
            
            # Copy System Folders
            for item in SYSTEM_APPS:
                src = os.path.join(project_root, item)
                dst = os.path.join(backend_dest, item)
                if os.path.exists(src):
                    if os.path.isdir(src):
                        ignore_patterns = ['__pycache__', '*.pyc']
                        if item == 'media':
                            ignore_patterns.extend(['release_exports', '*.zip', '*.rar', 'frontend.rar'])
                            
                        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignore_patterns))
                    else:
                        shutil.copy2(src, dst)

            # Copy Allowed Apps
            for app_label in allowed_apps:
                if app_label in SYSTEM_APPS: continue # Already copied
                src = os.path.join(project_root, app_label)
                if os.path.exists(src):
                    shutil.copytree(src, os.path.join(backend_dest, app_label), dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

            # --- PROCESS settings.py ---
            settings_path = os.path.join(backend_dest, 'api', 'settings.py')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Process INSTALLED_APPS
                # Strategy: Iterate over all KNOWN apps in the project, and if they are NOT in allowed_apps, remove them.
                # However, we don't know all potential apps easily without scanning. 
                # Better Strategy: Regex match strings in INSTALLED_APPS list and check against allowed.
                
                # We will use a simpler approach: Read lines, identify if inside INSTALLED_APPS or PROJECT_APPS, 
                # and filter strings that look like app labels.
                
                new_lines = []
                in_installed_apps = False
                in_project_apps = False
                
                # Identify all project apps (directories in project root) to know what to filter
                all_project_apps = [d for d in os.listdir(project_root) if os.path.isdir(os.path.join(project_root, d)) and os.path.exists(os.path.join(project_root, d, 'apps.py'))]
                
                for line in content.splitlines():
                    stripped = line.strip()
                    
                    if stripped.startswith('INSTALLED_APPS = ['):
                        in_installed_apps = True
                        new_lines.append(line)
                        continue
                    if stripped.startswith('PROJECT_APPS = ['):
                        in_project_apps = True
                        new_lines.append(line)
                        continue
                    if stripped == ']':
                        in_installed_apps = False
                        in_project_apps = False
                        new_lines.append(line)
                        continue
                        
                    if in_installed_apps or in_project_apps:
                        # Extract app name from line (e.g., "    'crm',")
                        # Simple regex to find content between quotes
                        match = re.search(r"['\"](\w+)['\"]", stripped)
                        if match:
                            app_name = match.group(1)
                            # If it's a project app (known local app) AND not in allowed_apps, skip it.
                            # We assume external libs (django.contrib, rest_framework) are always kept.
                            # So we only filter if it is in 'all_project_apps' AND NOT in 'allowed_apps'
                            if app_name in all_project_apps and app_name not in allowed_apps and app_name not in SYSTEM_APPS:
                                continue # SKIP THIS LINE
                    
                    new_lines.append(line)
                
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))


            # --- PROCESS api/urls.py ---
            urls_path = os.path.join(backend_dest, 'api', 'urls.py')
            if os.path.exists(urls_path):
                with open(urls_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_lines = []
                for line in content.splitlines():
                    stripped = line.strip()
                    # Check for "path('crm/', include('crm.urls'))" patterns
                    # We regex search for include('appname.urls')
                    match = re.search(r"include\(['\"](\w+)\.urls['\"]\)", stripped)
                    if match:
                        app_name = match.group(1)
                        # If app_name is in all_project_apps but NOT in allowed_apps/system_apps, skip
                        if app_name in all_project_apps and app_name not in allowed_apps and app_name not in SYSTEM_APPS:
                            continue
                    
                    new_lines.append(line)
                
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))


            # =======================
            # 2. FRONTEND EXPORT
            # =======================
            fe_root = os.path.join(project_root, 'frontend')
            fe_src_root = os.path.join(fe_root, 'src')
            fe_dest_root = os.path.join(frontend_dest, 'src')
            os.makedirs(fe_dest_root)
            
            # Copy Root Files (package.json, etc)
            for item in os.listdir(fe_root):
                if os.path.isfile(os.path.join(fe_root, item)):
                    shutil.copy2(os.path.join(fe_root, item), frontend_dest)
            if os.path.exists(os.path.join(fe_root, 'public')):
                shutil.copytree(os.path.join(fe_root, 'public'), os.path.join(frontend_dest, 'public'), dirs_exist_ok=True)
            for item in os.listdir(fe_src_root):
                if os.path.isfile(os.path.join(fe_src_root, item)):
                    shutil.copy2(os.path.join(fe_src_root, item), fe_dest_root)

            # Copy Common Directories
            COMMON_DIRS = ['assets', 'components', 'config', 'context', 'hooks', 'locales', 'pages', 'services', 'utils', 'styles', 'layout', 'auth']
            for d in COMMON_DIRS:
                s = os.path.join(fe_src_root, d)
                if os.path.exists(s):
                    shutil.copytree(s, os.path.join(fe_dest_root, d), dirs_exist_ok=True)

            # Copy ONLY Allowed Apps
            apps_dest = os.path.join(fe_dest_root, 'apps')
            os.makedirs(apps_dest)
            
            allowed_fe_modules = set()
            for app_label in allowed_apps:
                mapped = FRONTEND_MAPPING.get(app_label)
                if mapped: allowed_fe_modules.add(mapped)
                
            for app_dir_name in allowed_fe_modules:
                s = os.path.join(fe_src_root, 'apps', app_dir_name)
                if os.path.exists(s):
                    shutil.copytree(s, os.path.join(apps_dest, app_dir_name), dirs_exist_ok=True)

            # --- PROCESS App.jsx ---
            app_jsx_path = os.path.join(fe_dest_root, 'App.jsx')
            if os.path.exists(app_jsx_path):
                with open(app_jsx_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_lines = []
                # Identify Routes to REMOVE based on variable names
                excluded_routes_vars = []
                for app_label, route_name in ROUTE_MAPPING.items():
                    if app_label not in allowed_apps:
                        excluded_routes_vars.append(route_name)
                
                lines = content.splitlines()
                skip_block = False
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # 1. Filter Imports
                    is_excluded_import = False
                    if stripped.startswith('import '):
                        for route_var in excluded_routes_vars:
                            if route_var in stripped:
                                is_excluded_import = True
                                break
                    if is_excluded_import: continue
                    
                    # 2. Filter Route Blocks
                    # Match exact pattern: <Route path="..." element={<AppGuard appLabel="crm" />}>
                    # Only the 'appLabel' is the source of truth
                    match = re.search(r'appLabel="(\w+)"', stripped)
                    if match:
                        app_lbl = match.group(1)
                        if app_lbl not in allowed_apps:
                            skip_block = True
                    
                    if skip_block:
                         if '</Route>' in stripped:
                             skip_block = False 
                         continue 
                    
                    new_lines.append(line)
                    
                with open(app_jsx_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                    
            # --- PROCESS modules.jsx (Navigation) ---
            modules_path = os.path.join(fe_dest_root, 'config', 'modules.jsx')
            if os.path.exists(modules_path):
                with open(modules_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_lines = []
                lines = content.splitlines()
                skip_block = False
                
                # We need to find keys in APP_MODULES object: 'crm': [ ... ]
                for line in lines:
                    stripped = line.strip()
                    if skip_block:
                        # Check if block ends. Usually indented.
                        # We count brackets or simply look for "]," which closes the array.
                        # Or next key string.
                        # Simplest: if line starts with '],' we might be done.
                        if stripped.startswith('],'):
                            skip_block = False
                            continue
                        if stripped.startswith(']'): # Last item
                            skip_block = False
                            continue
                        continue

                    # Detect key start: 'crm': [
                    match = re.match(r"['\"](\w+)['\"]:\s*\[", stripped)
                    if match:
                        app_key = match.group(1)
                        # Check if this app_key is a backend app label we know about?
                        # In the file viewed: 'users', 'clients', 'apps', 'codings', 'releases', 'crm'
                        # These match our backend app labels.
                        if app_key in all_project_apps and app_key not in allowed_apps and app_key not in SYSTEM_APPS:
                            skip_block = True
                            continue
                    
                    new_lines.append(line)

                with open(modules_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))


            # --- PROCESS components/Layout.jsx (Shared Layout Logic) ---
            layout_path = os.path.join(fe_dest_root, 'components', 'Layout.jsx')
            if os.path.exists(layout_path):
                with open(layout_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_layout_lines = []
                lines = content.splitlines()
                skip_block = False
                brace_count = 0
                
                # We need to filter `else if (path.includes('/crm')) { ... }` blocks
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Detection Logic for `else if (path.includes('/appname'))`
                    match = re.search(r"else if \(path\.includes\('/(\w+)'\)", stripped)
                    if match:
                        app_key = match.group(1)
                        if app_key in all_project_apps and app_key not in allowed_apps and app_key not in SYSTEM_APPS:
                            skip_block = True
                            brace_count = 0 
                            # Count opening brace in this line
                            brace_count += line.count('{')
                            brace_count -= line.count('}')
                            # If brace_count is 0, it was a one-liner (unlikely here but possible)
                            if brace_count == 0: 
                                skip_block = False
                            else:
                                continue # Skip the start line
                    
                    if skip_block:
                        brace_count += line.count('{')
                        brace_count -= line.count('}')
                        if brace_count <= 0:
                            skip_block = False
                        continue
                        
                    new_layout_lines.append(line)

                with open(layout_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_layout_lines))
            
                with open(layout_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_layout_lines))


            # --- PROCESS clients App (Remove Beneficiary Features) ---
            # 1. Backend: clients/urls.py
            clients_urls_path = os.path.join(backend_dest, 'clients', 'urls.py')
            if os.path.exists(clients_urls_path):
                with open(clients_urls_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = []
                for line in lines:
                    # Remove the router registration for beneficiaries
                    if "r'beneficiaries'" in line or 'BeneficiaryViewSet' in line:
                         if 'import' not in line: # Keep imports to avoid breaking if other things use it (though likely unused)
                             continue
                    new_lines.append(line)
                
                with open(clients_urls_path, 'w', encoding='utf-8') as f:
                    f.write(''.join(new_lines))

            # 2. Frontend: apps/ClientManagement/routes.jsx
            client_routes_path = os.path.join(fe_dest_root, 'apps', 'ClientManagement', 'routes.jsx')
            if os.path.exists(client_routes_path):
                with open(client_routes_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove Imports
                content = re.sub(r"import\s+Beneficiaries\s+from\s+['\"]./Beneficiaries['\"];\n?", "", content)
                
                # Remove Route Block
                # <Route element={<ModuleGuard appName="clients" moduleId="beneficiaries" />} key="guard-beneficiaries">
                #    <Route path="beneficiaries" element={<Beneficiaries />} key="beneficiaries" />
                # </Route>,
                # Regex to match this block loosely
                content = re.sub(r"\s*<Route[^>]*moduleId=['\"]beneficiaries['\"][^>]*>[\s\S]*?</Route>,?", "", content)
                
                with open(client_routes_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # 3. Frontend: config/modules.jsx (Remove 'beneficiaries' from 'clients' list)
            # (We already processed modules.jsx generally, but we need to re-process for this specific removal)
            modules_path = os.path.join(fe_dest_root, 'config', 'modules.jsx')
            if os.path.exists(modules_path):
                with open(modules_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # We need to remove the object `{ id: 'beneficiaries', ... },` inside 'clients' array.
                # Since parsing JS with regex is fragile, we look for the specific ID block.
                
                # Strategy: Identify lines for 'beneficiaries' block and skip them.
                lines = content.splitlines()
                new_lines = []
                skip_block = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Start of block detection
                    if "id: 'beneficiaries'" in stripped:
                         # We are likely inside the object, but we need to find the START of the object {
                         # Assuming standard formatting `{ ... id: 'beneficiaries' ... }` or multi-line
                         # If we are already appending lines, we might have appended the opening `{`.
                         # This is tricky without a parser.
                         
                         # Simpler Regex Replacement on the whole content might be safer for this specific structure
                         pass
                    
                    new_lines.append(line)
                
                # Regex approach on full content is risky with nested braces (JSX)
                # We use a brace counting strategy relative to the "id: 'beneficiaries'" position.
                
                def remove_object_by_id(text, id_value):
                    # 1. Find the ID
                    search_str = f"id: '{id_value}'"
                    id_idx = text.find(search_str)
                    if id_idx == -1: 
                        # Try double quotes
                        search_str = f'id: "{id_value}"'
                        id_idx = text.find(search_str)
                        if id_idx == -1: return text

                    # 2. Scan backwards for the OPENING brace '{' of this object
                    open_brace_idx = -1
                    brace_balance = 0
                    # We scan backwards. We expect to find '{' that encloses this property.
                    # Warning: simple scan back might hit a closing brace of a previous sibling's prop?
                    # But we are inside an object structure. 
                    # Let's assume the syntax is valid: { ... id: '...' ... }
                    
                    for i in range(id_idx, -1, -1):
                        char = text[i]
                        if char == '}':
                            brace_balance += 1
                        elif char == '{':
                            if brace_balance > 0:
                                brace_balance -= 1
                            else:
                                open_brace_idx = i
                                break
                    
                    if open_brace_idx == -1: return text
                    
                    # 3. Scan forwards for the CLOSING brace '}' of this object
                    close_brace_idx = -1
                    brace_balance = 1 # We start with the opening brace we found
                    length = len(text)
                    
                    for i in range(open_brace_idx + 1, length):
                        char = text[i]
                        if char == '{':
                            brace_balance += 1
                        elif char == '}':
                            brace_balance -= 1
                            if brace_balance == 0:
                                close_brace_idx = i
                                break
                    
                    if close_brace_idx == -1: return text
                    
                    # 4. Check for comma after closing brace
                    end_remove_idx = close_brace_idx + 1
                    # consume optional whitespace
                    while end_remove_idx < length and text[end_remove_idx].isspace():
                        end_remove_idx += 1
                    if end_remove_idx < length and text[end_remove_idx] == ',':
                        end_remove_idx += 1
                    
                    # Remove content
                    return text[:open_brace_idx] + text[end_remove_idx:]

                content = remove_object_by_id(content, 'beneficiaries')
                
                with open(modules_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 4. Frontend: Clean api.js (Remove excluded apps APIs and Beneficiaries specifically)
            api_js_path = os.path.join(fe_dest_root, 'api.js')
            if os.path.exists(api_js_path):
                with open(api_js_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # A. Remove Specific Beneficiary Functions (Robust Brace Counting)
                # We need to parse the content line by line or character by character to handle nested braces safely.
                # However, for simplicity and performance on a known file structure, we can iterate lines.
                
                beneficiary_funcs = ['getBeneficiaries', 'createBeneficiary', 'updateBeneficiary', 'deleteBeneficiary']
                
                # Helper to remove a function by name using brace counting
                def remove_js_function(file_content, func_name):
                    start_pattern = f"export const {func_name} = async"
                    start_idx = file_content.find(start_pattern)
                    if start_idx == -1:
                        return file_content
                    
                    # Search backwards from start_idx to find the start of the line (to remove indentation)
                    line_start = file_content.rfind('\n', 0, start_idx) + 1
                    
                    # Now assume start from line_start
                    # We need to find the ending '};' corresponding to this function block.
                    # We scan char by char starting from the first '{' we find after start_idx
                    
                    open_brace_idx = file_content.find('{', start_idx)
                    if open_brace_idx == -1: return file_content # Should not happen for these funcs
                    
                    brace_count = 1
                    current_idx = open_brace_idx + 1
                    length = len(file_content)
                    
                    while brace_count > 0 and current_idx < length:
                        char = file_content[current_idx]
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        current_idx += 1
                    
                    # Now current_idx is just after the closing brace '}'
                    # We usually have a semicolon ';' after it.
                    if current_idx < length and file_content[current_idx] == ';':
                        current_idx += 1
                    
                    # Also consume the newline after it if present
                    if current_idx < length and file_content[current_idx] == '\n':
                        current_idx += 1
                        
                    # Remove the slice [line_start : current_idx]
                    return file_content[:line_start] + file_content[current_idx:]

                for func in beneficiary_funcs:
                    content = remove_js_function(content, func)

                # B. Remove Excluded Apps Sections (including Releases if not allowed)
                # Map App Label to Section Header in api.js
                API_HEADERS = {
                    'crm': '// ============ CRM API ============',
                    'codings': '// ============ CODINGS API ============',
                    'apps': '// ============ APPS API ============',
                    'releases': '// ============ RELEASES API ============',
                }
                
                # Dynamic detection of all headers to ensure we stop at ANY header (including EXPORT API)
                # We re-read content to ensure it's fresh
                
                # 1. First, identifying all start positions of known headers
                # We use a loop because removing one section changes indices
                
                available_headers = list(API_HEADERS.items())
                
                for app_label, header in available_headers:
                    # Logic: If app is NOT in allowed apps OR it is 'releases' (explicit user request to remove it), remove it.
                    # Note: 'releases' might be in allowed_apps if it's the engine, but user wants it gone from export.
                    should_remove = False
                    if app_label in ['releases']: # Explicitly requested by user
                        should_remove = True
                    elif app_label not in allowed_apps and app_label not in SYSTEM_APPS:
                        should_remove = True
                        
                    if should_remove:
                        start_idx = content.find(header)
                        if start_idx != -1:
                            # Find the start of the NEXT header (any header)
                            # We search for "// ============ " to find the next one
                            next_header_match = re.search(r"// ============ .*? ============", content[start_idx + len(header):])
                            
                            if next_header_match:
                                next_header_idx = start_idx + len(header) + next_header_match.start()
                                end_idx = next_header_idx
                            else:
                                # No next header, go to end of file? 
                                # Be careful not to delete file end if it contains common exports.
                                # Usually API sections are stacked. relying on next header is safest.
                                # If no next header, maybe verify if we prefer to cut just until EOF.
                                end_idx = len(content)

                            content = content[:start_idx] + content[end_idx:]

                with open(api_js_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # --- PROCESS settings.py (Fix WSGI) ---
            # We already processed settings.py earlier, but let's do a targeted fix for WSGI
            settings_path = os.path.join(backend_dest, 'api', 'settings.py')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    final_settings = f.read()
                
                # Fix WSGI_APPLICATION
                if "WSGI_APPLICATION = 'wsgi.application'" in final_settings:
                    final_settings = final_settings.replace("WSGI_APPLICATION = 'wsgi.application'", "WSGI_APPLICATION = 'api.wsgi.application'")
                elif "WSGI_APPLICATION" not in final_settings:
                     # Append if missing? usually it's there.
                     pass
                     
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(final_settings)

            # --- PROCESS apps/views.py (Make Read-Only) ---
            apps_views_path = os.path.join(backend_dest, 'apps', 'views.py')
            if os.path.exists(apps_views_path):
                with open(apps_views_path, 'r', encoding='utf-8') as f:
                    apps_views_content = f.read()
                
                # 1. Add ReadOnlyModelViewSet import if not exists
                if 'ReadOnlyModelViewSet' not in apps_views_content:
                    apps_views_content = apps_views_content.replace(
                        'from rest_framework import viewsets, permissions',
                        'from rest_framework import viewsets, permissions\nfrom rest_framework.viewsets import ReadOnlyModelViewSet'
                    )
                
                # 2. Replace UnifiedModelViewSet with ReadOnlyModelViewSet for all ViewSets
                apps_views_content = apps_views_content.replace(
                    'class AppTypeViewSet(UnifiedModelViewSet):',
                    'class AppTypeViewSet(ReadOnlyModelViewSet):'
                )
                apps_views_content = apps_views_content.replace(
                    'class AppViewSet(UnifiedModelViewSet):',
                    'class AppViewSet(ReadOnlyModelViewSet):'
                )
                apps_views_content = apps_views_content.replace(
                    'class AppVersionViewSet(UnifiedModelViewSet):',
                    'class AppVersionViewSet(ReadOnlyModelViewSet):'
                )
                
                # 3. Remove create/update/delete code lines
                apps_views_content = re.sub(r'\s*created_code\s*=\s*[^\n]+\n', '\n', apps_views_content)
                apps_views_content = re.sub(r'\s*updated_code\s*=\s*[^\n]+\n', '\n', apps_views_content)
                apps_views_content = re.sub(r'\s*deleted_code\s*=\s*[^\n]+\n', '\n', apps_views_content)
                apps_views_content = re.sub(r'\s*frozen_code\s*=\s*[^\n]+\n', '\n', apps_views_content)
                
                # 4. Remove unused import for UnifiedModelViewSet
                if 'UnifiedModelViewSet' not in apps_views_content:
                    apps_views_content = re.sub(r'from api\.base import UnifiedModelViewSet\n?', '', apps_views_content)
                
                with open(apps_views_path, 'w', encoding='utf-8') as f:
                    f.write(apps_views_content)

            # --- PROCESS AppManagement Frontend (Make Read-Only UI) ---
            app_management_path = os.path.join(fe_dest_root, 'apps', 'AppManagement')
            if os.path.exists(app_management_path):
                
                # Helper function to make a component read-only
                def make_component_readonly(file_path, create_func, update_func, delete_func):
                    if not os.path.exists(file_path):
                        return
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Robust helper to remove JS functions using bracket counting
                    def remove_js_func_bracket_counting(text, func_signature_start):
                        """Remove a JS function by finding its signature and bracket-counting to the end.
                        Handles both {} (block body) and () (expression body with parens) arrow functions."""
                        start_idx = text.find(func_signature_start)
                        if start_idx == -1:
                            return text
                        
                        # Find line start
                        line_start = text.rfind('\n', 0, start_idx) + 1
                        
                        # Find the arrow '=>' first
                        arrow_idx = text.find('=>', start_idx)
                        if arrow_idx == -1:
                            return text
                        
                        # Look for the first opening bracket after the arrow (either { or ()
                        search_start = arrow_idx + 2
                        # Skip whitespace
                        while search_start < len(text) and text[search_start].isspace():
                            search_start += 1
                        
                        if search_start >= len(text):
                            return text
                        
                        open_char = text[search_start]
                        if open_char == '{':
                            close_char = '}'
                        elif open_char == '(':
                            close_char = ')'
                        else:
                            # Unknown pattern, skip
                            return text
                        
                        # Bracket counting
                        bracket_count = 1
                        current_idx = search_start + 1
                        length = len(text)
                        
                        while bracket_count > 0 and current_idx < length:
                            char = text[current_idx]
                            if char == open_char:
                                bracket_count += 1
                            elif char == close_char:
                                bracket_count -= 1
                            current_idx += 1
                        
                        # Skip optional semicolon and newlines
                        while current_idx < length and text[current_idx] in ';\n\r\t ':
                            current_idx += 1
                        
                        return text[:line_start] + text[current_idx:]
                    
                    # 1. Remove create/update/delete imports from api.js
                    content = re.sub(rf',?\s*{create_func}', '', content)
                    content = re.sub(rf',?\s*{update_func}', '', content)
                    content = re.sub(rf',?\s*{delete_func}', '', content)
                    
                    # 2. Remove the "New" button from header (SharedButton with pi-plus icon)
                    content = re.sub(
                        r'<SharedButton[^>]*icon="pi pi-plus"[^>]*onClick=\{handleCreate\}[^/]*/>',
                        '',
                        content
                    )
                    
                    # 3. Remove entire actionBodyTemplate function using bracket counting
                    content = remove_js_func_bracket_counting(content, 'const actionBodyTemplate = (rowData) =>')
                    
                    # 4. Remove Actions Column from DataTable
                    content = re.sub(r'<Column[^>]*header="Actions"[^/]*/>', '', content)
                    
                    # 5. Remove handler functions using bracket counting (handles nested try/catch)
                    content = remove_js_func_bracket_counting(content, 'const handleCreate = () =>')
                    content = remove_js_func_bracket_counting(content, 'const handleEdit = (')
                    content = remove_js_func_bracket_counting(content, 'const handleDelete = async')
                    content = remove_js_func_bracket_counting(content, 'const handleSubmit = async')
                    
                    # 6. Remove Form Modal JSX components (multi-line tags)
                    # Use [\s\S]*? to match across newlines
                    content = re.sub(r'<AppFormModal[\s\S]*?/>', '', content)
                    content = re.sub(r'<AppTypeFormModal[\s\S]*?/>', '', content)
                    content = re.sub(r'<AppVersionFormModal[\s\S]*?/>', '', content)
                    
                    # 7. Remove modal-related state variables
                    content = re.sub(r'const \[showModal, setShowModal\] = useState\([^)]*\);?\n?', '', content)
                    content = re.sub(r'const \[modalData, setModalData\] = useState\([^)]*\);?\n?', '', content)
                    
                    # 8. Remove modal imports
                    content = re.sub(r"import AppFormModal from ['\"][^'\"]+['\"];?\n?", '', content)
                    content = re.sub(r"import AppTypeFormModal from ['\"][^'\"]+['\"];?\n?", '', content)
                    content = re.sub(r"import AppVersionFormModal from ['\"][^'\"]+['\"];?\n?", '', content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Process Applications.jsx
                make_component_readonly(
                    os.path.join(app_management_path, 'Applications.jsx'),
                    'createApp', 'updateApp', 'deleteApp'
                )
                
                # Process AppTypes.jsx
                make_component_readonly(
                    os.path.join(app_management_path, 'AppTypes.jsx'),
                    'createAppType', 'updateAppType', 'deleteAppType'
                )
                
                # Process AppVersions.jsx
                make_component_readonly(
                    os.path.join(app_management_path, 'AppVersions.jsx'),
                    'createAppVersion', 'updateAppVersion', 'deleteAppVersion'
                )

            # 5. Frontend: Delete Beneficiaries.jsx File
            beneficiaries_file = os.path.join(fe_dest_root, 'apps', 'ClientManagement', 'Beneficiaries.jsx')
            if os.path.exists(beneficiaries_file):
                os.remove(beneficiaries_file)
            
            # 3. Create Archive
            zip_filename = f"release_system_{self.release.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            archive_path = shutil.make_archive(os.path.join(temp_dir, zip_filename), 'zip', root_dir=temp_dir, base_dir=base_dir_name)
            
            # 4. Save to FileField
            with open(archive_path, 'rb') as f:
                self.release.exported_file.save(f"{zip_filename}.zip", ContentFile(f.read()))
                
            return self.release.exported_file.url

    def _get_beneficiaries_data(self):
        data = []
        for rb in self.release.releasebeneficiary_set.all():
            benef = rb.beneficiary
            structures = Structure.objects.filter(beneficiary=benef)
            levels_ids = structures.values_list('level', flat=True).distinct()
            levels = Level.objects.filter(id__in=levels_ids)
            
            data.append({
                'public_name': benef.public_name,
                'private_name': benef.pravite_name,
                'structures': list(structures.values('name', 'is_branch', 'description', 'level__name')),
                'levels': list(levels.values('name', 'count'))
            })
        return data

    def _get_apps_data(self):
        data = []
        for ra in self.release.releaseapp_set.all():
            app = ra.app
            
            # Coding Categories & Codings
            # Use the new codings field or fallback to category logic
            if app.codings.exists():
                 codings_data = list(app.codings.values('name', 'category', 'order'))
            else:
                coding_categories = app.codingCategory.all()
                codings_data = []
                for cat in coding_categories:
                    codings = Coding.objects.filter(codingCategory=cat)
                    codings_data.append({
                        'category': cat.general_name,
                        'is_tree': cat.type == 'tree',
                        'codes': list(codings.values('name', 'order', 'parent__name'))
                    })
                
            # Permissions (Interfaces?)
            perms = Permission.objects.filter(content_type__app_label=app.app_label)
            
            data.append({
                'label': app.app_label,
                'name': app.name,
                'is_core': ra.is_core,
                'url': app.url,
                'codings': codings_data,
                'permissions': list(perms.values('codename', 'name'))
            })
        return data

    def _get_groups_data(self):
        data = []
        for rg in self.release.releasegroup_set.all():
            group = rg.group
            # Check if it's a Role
            is_role = Role.objects.filter(id=group.id).exists()
            perms = group.permissions.all()
            
            data.append({
                'name': group.name,
                'is_role': is_role,
                'permissions': list(perms.values_list('codename', flat=True))
            })
        return data

    def _get_users_data(self):
        data = []
        for ru in self.release.releaseuser_set.all():
            user = ru.user
            groups = user.groups.all()
            user_perms = user.user_permissions.all()
            
            data.append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': list(groups.values_list('name', flat=True)),
                'direct_permissions': list(user_perms.values_list('codename', flat=True))
            })
        return data
