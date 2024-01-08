# HttpEpHealthChecker
An HTTP endpoint health checker designed to test and monitor the availability of various endpoints

## Prerequisites
- Python 3.8 or higher
- PyYAML library (install using `pip install pyyaml`)
- requests library (install using `pip install requests`)
- keyboard library (install using `pip install keyboard`)

## Installation
1. Clone the repository: `git clone https://github.com/mladen995/HttpEpHealthChecker.git`
2. Install required dependencies: `pip install -r requirements.txt`

## How to Use
1. To run the script, the `-f` argument is mandatory. Use `-f` to specify the required file path (.yaml file) and optionally use `-h` to display usage instructions.
2. Run the script using the command: `python main.py -f path\to\your\file.yaml`
   
### Required Argument:
- `-f, --file`: Path or name of the file containing input data.
### Optional Argument:
- `-h, --help`: Show program usage.

## Example
```bash
python2 main.py -f test\config.yaml
