# Bandit SAST Testing Documentation for Django Applications

## 1. Overview

**Bandit** is an open-source Static Application Security Testing (SAST) tool used to identify common security issues in Python source code. It analyzes code for known insecure coding patterns and reports vulnerabilities.

This guide explains how to install, configure, and run Bandit on a Django application inside a Python virtual environment (`env`).

---

## 2. Prerequisites

Ensure the following are installed:

- Python 3.8 or higher
- pip (Python package manager)
- A Django application
- Virtual environment tool (`venv` or `virtualenv`)

---

## 3. Setting Up the Virtual Environment

### 3.1 Create Virtual Environment


```bash
python -m venv env
```

### 3.2 Activate Virtual Environment

```bash
env\Scripts\activate
```

### 4. Installing Bandit

```bash
pip install bandit 
```

### 4. Using bandit for our project scope

We will use bandit on the following code folders that we developed:

1. accounts
2. cart
3. dashboard
3. mystore 
5. orders
6. products
7. templates 

For scanning a specific folder in bandit, we will run the following command in terminal:

```bash
bandit -r .\folder_name\ 
```

Note: Supply chain attacks are excluded from our SAST testing scope. In other words, We will not test extra backages or libraries that exsit in our virtual environment. 

