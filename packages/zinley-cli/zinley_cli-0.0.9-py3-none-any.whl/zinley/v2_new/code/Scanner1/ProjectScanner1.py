import os
import subprocess
import aiohttp
import asyncio
import sys
import time
from .ScannerAgent import ScannerAgent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zinley.v2_new.code.ResultsManager1 import ResultsManager1

class ProjectScanner1:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens, max_agents=20):
        self.project_path = project_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.max_agents = max_agents
        self.agents = []
        self.results_manager1 = ResultsManager1()

    def create_agents(self):
        """Create the specified number of ScannerAgent instances."""
        self.agents = [ScannerAgent(self.project_path, self.api_key, self.endpoint, self.deployment_id, self.max_tokens) for _ in range(self.max_agents)]

    def get_tree_txt_files(self):
        """Scan for tree.txt files in the specified directory."""
        tree_txt_files = []
        tree_path = os.path.join(self.project_path, "Zinley/Project_analysis")

        if not os.path.exists(tree_path):
            print(f"Directory does not exist: {tree_path}")
            return tree_txt_files

        for root, _, files in os.walk(tree_path):
            for file in files:
                if file == 'tree.txt':
                    file_path = os.path.join(root, file)
                    tree_txt_files.append(file_path)

        return tree_txt_files

    def get_txt_files(self):
        """Scan for all txt files in the specified directory."""
        txt_files = []
        txt_path = os.path.join(self.project_path, "Zinley/Project_analysis")

        if not os.path.exists(txt_path):
            print(f"Directory does not exist: {txt_path}")
            return txt_files

        for root, _, files in os.walk(txt_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

    async def update_tree(self):
        """Update the project directory tree and save to tree.txt."""
        try:
            tree_path = self.project_path
            output_dir = os.path.join(tree_path, "Zinley", "Project_analysis")
            os.makedirs(output_dir, exist_ok=True)
            tree_file_path = os.path.join(output_dir, "tree.txt")

            result = subprocess.run(['tree', self.project_path, '-I', 'Zinley'], stdout=subprocess.PIPE, text=True)

            with open(tree_file_path, 'w') as f:
                f.write(result.stdout)
        except Exception as e:
            print(f"Failed to update tree: {e}")

    def list_dependencies(self):
        """List all dependencies for the project by scanning the project files and checking for installed dependencies."""
        dependencies = set()
        for root, _, files in os.walk(self.project_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.py'):
                    dependencies.update(self.scan_python_file(file_path))
                elif file == 'package.json':
                    dependencies.update(self.parse_package_json(file_path))
                elif file == 'requirements.txt':
                    dependencies.update(self.parse_requirements_txt(file_path))
                elif file == 'Pipfile':
                    dependencies.update(self.parse_pipfile(file_path))
                elif file == 'pyproject.toml':
                    dependencies.update(self.parse_pyproject_toml(file_path))
                elif file == 'pom.xml':
                    dependencies.update(self.parse_pom_xml(file_path))
                elif file == 'build.gradle' or file == 'build.gradle.kts':
                    dependencies.update(self.parse_gradle_file(file_path))
                elif file == 'Gemfile':
                    dependencies.update(self.parse_gemfile(file_path))
                elif file == 'Cargo.toml':
                    dependencies.update(self.parse_cargo_toml(file_path))
                elif file == 'composer.json':
                    dependencies.update(self.parse_composer_json(file_path))
                elif file == 'project.clj':
                    dependencies.update(self.parse_project_clj(file_path))
                elif file == 'deps.edn':
                    dependencies.update(self.parse_deps_edn(file_path))
                elif file == 'packages.config':
                    dependencies.update(self.parse_packages_config(file_path))
                elif file == 'paket.dependencies':
                    dependencies.update(self.parse_paket_dependencies(file_path))
                elif file == 'Podfile':
                    dependencies.update(self.parse_podfile(file_path))
                elif file == 'spm.package.resolved':
                    dependencies.update(self.parse_spm_package_resolved(file_path))

        installed_dependencies = self.check_installed_dependencies(dependencies)
        return installed_dependencies

    def scan_python_file(self, file_path):
        """Scan a Python file for imported modules."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*(import|from)\s+([\w\.]+)', line)
                if match:
                    dependencies.add(match.group(2).split('.')[0])
        return dependencies

    def parse_package_json(self, file_path):
        """Parse dependencies from package.json."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return set(data.get('dependencies', {}).keys())

    def parse_requirements_txt(self, file_path):
        """Parse dependencies from requirements.txt."""
        with open(file_path, 'r') as file:
            dependencies = file.readlines()
        return {dep.strip().split('==')[0] for dep in dependencies if dep.strip()}

    def parse_pipfile(self, file_path):
        """Parse dependencies from Pipfile."""
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return set(data.get('packages', {}).keys())

    def parse_pyproject_toml(self, file_path):
        """Parse dependencies from pyproject.toml."""
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return set(data.get('tool', {}).get('poetry', {}).get('dependencies', {}).keys())

    def parse_pom_xml(self, file_path):
        """Parse dependencies from pom.xml."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        dependencies = set()
        for dependency in root.findall(".//dependency"):
            group_id = dependency.find("groupId").text
            artifact_id = dependency.find("artifactId").text
            dependencies.add(f"{group_id}:{artifact_id}")
        return dependencies

    def parse_gradle_file(self, file_path):
        """Parse dependencies from build.gradle or build.gradle.kts."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*(implementation|compile)\s*["\']([\w:]+)["\']', line)
                if match:
                    dependencies.add(match.group(2))
        return dependencies

    def parse_gemfile(self, file_path):
        """Parse dependencies from Gemfile."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*gem\s*["\']([\w-]+)["\']', line)
                if match:
                    dependencies.add(match.group(1))
        return dependencies

    def parse_cargo_toml(self, file_path):
        """Parse dependencies from Cargo.toml."""
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return set(data.get('dependencies', {}).keys())

    def parse_composer_json(self, file_path):
        """Parse dependencies from composer.json."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return set(data.get('require', {}).keys())

    def parse_project_clj(self, file_path):
        """Parse dependencies from project.clj."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*\[\s*([\w.-]+)\s*["\']([\w.-]+)["\']', line)
                if match:
                    dependencies.add(match.group(1))
        return dependencies

    def parse_deps_edn(self, file_path):
        """Parse dependencies from deps.edn."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*:\s*([\w.-]+)\s*{', line)
                if match:
                    dependencies.add(match.group(1))
        return dependencies

    def parse_packages_config(self, file_path):
        """Parse dependencies from packages.config."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        dependencies = set()
        for dependency in root.findall(".//package"):
            dependencies.add(dependency.get("id"))
        return dependencies

    def parse_paket_dependencies(self, file_path):
        """Parse dependencies from paket.dependencies."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*nuget\s*([\w.-]+)', line)
                if match:
                    dependencies.add(match.group(1))
        return dependencies

    def parse_podfile(self, file_path):
        """Parse dependencies from Podfile."""
        dependencies = set()
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r'^\s*pod\s*["\']([\w-]+)["\']', line)
                if match:
                    dependencies.add(match.group(1))
        return dependencies

    def parse_spm_package_resolved(self, file_path):
        """Parse dependencies from Package.resolved (Swift Package Manager)."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return {pin['package'] for pin in data.get('object', {}).get('pins', [])}

    def check_installed_dependencies(self, dependencies):
        """Check if dependencies are installed and return their status."""
        installed_dependencies = {}
        for dep in dependencies:
            if self.is_python_installed(dep):
                installed_dependencies[dep] = "installed (Python)"
            elif self.is_npm_installed(dep):
                installed_dependencies[dep] = "installed (npm)"
            elif self.is_gem_installed(dep):
                installed_dependencies[dep] = "installed (gem)"
            elif self.is_cargo_installed(dep):
                installed_dependencies[dep] = "installed (cargo)"
            elif self.is_composer_installed(dep):
                installed_dependencies[dep] = "installed (composer)"
            else:
                installed_dependencies[dep] = "not installed"
        return installed_dependencies

    def is_python_installed(self, dep):
        """Check if a Python dependency is installed."""
        result = subprocess.run(['pip', 'show', dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0

    def is_npm_installed(self, dep):
        """Check if an npm dependency is installed."""
        result = subprocess.run(['npm', 'list', dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return dep in result.stdout

    def is_gem_installed(self, dep):
        """Check if a gem dependency is installed."""
        result = subprocess.run(['gem', 'list', '-i', dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "true" in result.stdout

    def is_cargo_installed(self, dep):
        """Check if a Cargo dependency is installed."""
        result = subprocess.run(['cargo', 'search', dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return dep in result.stdout

    def is_composer_installed(self, dep):
        """Check if a Composer dependency is installed."""
        result = subprocess.run(['composer', 'show', dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0

    def scan_project_files(self):
        """Scan the project directory for all coding files, ignoring images, videos, third-party dependencies, and IDE files."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.ico', '.webp'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}

        ignore_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.env', 'vendor', 'Pods', 'Carthage', '.git',
            '.idea', '.vscode', '__pycache__', 'build', 'dist', '.gradle', '.m2', '.bundle',
            '.cxx', 'DerivedData', 'Assets.xcassets', 'Preview Assets.xcassets', 'xcuserdata', 'xcshareddata', 'Zinley'
        }

        ignore_files = {
            '.gitignore', '.gitattributes', 'README.md', 'LICENSE', 'yarn.lock', 'package-lock.json',
            'Pipfile.lock', '.DS_Store', '.env', 'Gemfile.lock', 'Cargo.lock', '.classpath',
            '.project', 'Thumbs.db', 'npm-debug.log', 'pip-log.txt', '.metadata', '.pbxproj', '.xcworkspace', '.DS_Store', '.xcodeproj'
        }

        code_extensions = {
            # Programming languages
            '.py', '.pyc', '.pyo', '.pyw', '.pyx', '.pxd', '.pyd', # Python
            '.js', '.jsx', '.ts', '.tsx', # JavaScript/TypeScript
            '.java', '.class', '.jar', # Java
            '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hh', '.hxx', '.ino', # C/C++
            '.cs', '.csproj', # C#
            '.go', # Go
            '.rb', '.rbw', '.rake', '.gemspec', '.rhtml', # Ruby
            '.php', '.phtml', '.php3', '.php4', '.php5', '.php7', '.phps', '.phpt', # PHP
            '.kt', '.kts', # Kotlin
            '.swift', # Swift
            '.m', '.mm', # Objective-C
            '.r', '.rdata', '.rds', '.rda', '.rproj', # R
            '.pl', '.pm', '.t', # Perl
            '.sh', '.bash', '.bats', '.zsh', '.ksh', '.csh', # Shell scripts
            '.lua', # Lua
            '.erl', '.hrl', '.beam', # Erlang
            '.ex', '.exs', # Elixir
            '.ml', '.mli', '.fs', '.fsi', '.fsx', '.fsscript', # OCaml/F#
            '.scala', '.sbt', '.sc', # Scala
            '.jl', # Julia
            '.hs', '.lhs', # Haskell
            '.clj', '.cljs', '.cljc', '.edn', # Clojure
            '.groovy', '.gvy', '.gy', '.gsh', # Groovy
            '.v', '.vh', '.sv', '.svh', # Verilog/SystemVerilog
            '.vhd', '.vhdl', # VHDL
            '.adb', '.ads', '.ada', # Ada
            '.d', '.di', # D
            '.nim', '.nims', # Nim
            '.rs', '.rlib', # Rust
            '.cr', # Crystal
            '.cmake', '.make', '.mak', '.mk', # Build files
            '.bat', '.cmd', # Batch files
            # Markup and stylesheets
            '.html', '.htm', '.xhtml', '.jhtml', # HTML
            '.css', '.scss', '.sass', '.less', # CSS and preprocessors
            '.xml', '.xsl', '.xslt', '.xsd', '.dtd', '.wsdl', # XML
            '.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.rst', '.adoc', '.asciidoc', # Markdown/AsciiDoc/ReStructuredText
            # Configuration files
            '.json', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.toml', '.plist', '.env', '.editorconfig',
            '.eslintrc', '.prettierrc', '.babelrc', '.stylelintrc', '.dockerfile', '.dockerignore',
            '.gitlab-ci.yml', '.travis.yml', '.circleci/config.yml',
            # Data files
            '.csv', '.tsv', '.parquet', '.avro', '.orc', '.json', '.xml',
            # iOS-specific
            '.nib', '.xib', '.storyboard', # iOS
            # Android-specific
            '.gradle', '.pro', '.aidl', '.rs', '.rsh', '.xml',
            # Desktop app specific
            '.desktop', '.manifest', '.rc', '.resx', '.xaml', '.appxmanifest', '.csproj', '.vbproj',
            # Web app specific
            '.asp', '.aspx', '.ejs', '.hbs', '.jsp', '.jspx', '.php', '.cfm',
            # Database related
            '.sql', '.db', '.db3', '.sqlite', '.sqlite3', '.rdb', '.mdb', '.accdb', '.pdb',
            # Others
            '.tex', '.bib', '.log', '.txt'
        }

        files_list = []

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d.lower() not in {dir_name.lower() for dir_name in ignore_dirs}]

            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                file_name = os.path.basename(file).lower()

                if file_ext in image_extensions or file_ext in video_extensions or file_name in ignore_files or file_ext not in code_extensions:
                    continue

                files_list.append(file)

        return files_list

    async def scanner(self, file, agent):
        """Generate idea plans based on user prompt and available files."""
        return await agent.get_file_summaries(file)


    async def scan_files_with_agents(self, files):
        """Distribute files among agents and scan them."""
        # Step to remove all empty files from the list
        files = [file for file in files if file]

        print(f"Final touching: {files}")
        tasks = []
        num_files = len(files)
        num_agents = min(self.max_agents, num_files)

        self.create_agents()

        for i in range(num_files):
            agent = self.agents[i % num_agents]
            tasks.append(self.scanner(files[i], agent))

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                self.results_manager1.update_results(self.project_path, result[0]['file_path'], result[0]['summary'])
            except Exception as e:
                print(f"Error processing file with agent: {e}")


    async def scan_total_files_with_agents(self, files):
        """Distribute files among agents and scan them."""
        # Step to remove all empty files from the list
        files = [file for file in files if file]
        print(f"Final touching: {files}")
        tasks = []
        num_files = len(files)
        num_agents = min(self.max_agents, num_files)

        self.create_agents()

        for i in range(num_files):
            agent = self.agents[i % num_agents]
            tasks.append(self.scanner(files[i], agent))

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                self.results_manager1.update_total_results(self.project_path, result[0]['file_path'], result[0]['summary'])
            except Exception as e:
                print(f"Error processing file with agent: {e}")


    async def get_started(self):
        print("Start scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            files = self.scan_project_files()
            files = [file for file in files if file]
            dependencies = self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_total_files_with_agents(files)
            print("Done scanning")
        except Exception as e:
            print(f"Error during scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        print(f"Scanning completed in {duration:.2f} seconds")


    async def scanning_files(self, files):
        print("Start scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            dependencies = self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_files_with_agents(files)
            print("Done scanning")
        except Exception as e:
            print(f"Error during scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        print(f"Scanning completed in {duration:.2f} seconds")

    async def get_incremental_scan_started(self, files):
        print("Start incremental scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            dependencies = self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_total_files_with_agents(files)
            print("Done incremental scanning")
        except Exception as e:
            print(f"Error during incremental scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        print(f"Incremental Scanning completed in {duration:.2f} seconds")

async def main():
    project_path = "../../projects/stitchlab-ios"
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "gpt-4o"
    max_tokens = 4096

    controller = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
    await controller.get_started()

if __name__ == "__main__":
    asyncio.run(main())
