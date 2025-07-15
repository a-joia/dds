import os
import importlib.util
import sys
import traceback
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

# Discover all .py files in scripts/
def discover_scripts():
    return [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_path):
        return None
    with open(config_path, 'r') as f:
        try:
            return yaml.safe_load(f)
        except Exception:
            return None

def run_script(script_path):
    spec = importlib.util.spec_from_file_location('test_module', script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load spec for {script_path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules['test_module'] = module
    spec.loader.exec_module(module)
    failures = []
    # Run main() if present, else run all test_ functions
    if hasattr(module, 'main'):
        print(f'Running main() in {os.path.basename(script_path)}...')
        try:
            module.main()
        except Exception as e:
            failures.append((f'{os.path.basename(script_path)}:main', e, traceback.format_exc()))
    else:
        for name in dir(module):
            if name.startswith('test_') and callable(getattr(module, name)):
                print(f'Running {name} in {os.path.basename(script_path)}...')
                try:
                    getattr(module, name)()
                except Exception as e:
                    failures.append((f'{os.path.basename(script_path)}:{name}', e, traceback.format_exc()))
    return failures

def main():
    config = load_config()
    if config and 'scripts' in config and config['scripts']:
        scripts = config['scripts']
    else:
        scripts = discover_scripts()
    all_failures = []
    for script in scripts:
        script_path = os.path.join(SCRIPTS_DIR, script)
        if not os.path.exists(script_path):
            print(f'SKIPPING {script}: not found in scripts directory')
            continue
        failures = run_script(script_path)
        if not failures:
            print(f'{script} PASSED')
        else:
            print(f'{script} had {len(failures)} failure(s)')
            all_failures.extend(failures)
    if all_failures:
        print('\n--- TEST FAILURES SUMMARY ---')
        for testname, exc, tb in all_failures:
            print(f'FAILED: {testname}\nError: {exc}\nTraceback:\n{tb}\n')
        sys.exit(1)
    else:
        print('All tests PASSED')

if __name__ == '__main__':
    main()
