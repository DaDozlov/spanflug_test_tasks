# spanflug_test_tasks
Spanflug test tasks

# Task 1: Python and Data Analysis

## Getting started and Prerequisites

Ensure you have the following software installed on your system:
- **Python 3.11+** (For Python setup and dependencies)
- **Linux** (For example WSL Ubuntu or similar)

### To install python:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```


## Installation:

### Clone the Repository

```bash
git clone https://github.com/DaDozlov/spanflug_test_tasks
cd spanflug_test_tasks
```

## Python Setup

1. **Create a virtual environment using Python 3.11:**

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies using requirements**

   ```bash
   pip install -r requirements.txt
   ```

## Run the project

1. **Create a virtual environment using Python 3.11:**

   ```bash
   python first_task.py
   ```


## What can be seen there?

1. **The script preprocesses all the data files needed for the project.**
2. **The data is then cleaned and new features added.**
3. **After this, two files will be automatically downloaded: top 10 customers and top 10 suppliers.**
4. **Extra: you can uncomment line with fig.show to display the plotly bar chart with customers in your browser.**