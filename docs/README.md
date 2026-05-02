---
layout: home
permalink: index.html

# Please update this with your repository name and title
repository-name: e20-co523-C_LITE-Interpreter
title: C-Lite Interpreter
---

[comment]: # "This is the standard layout for the project, but you can clean this and use your own template"

# C-Lite Interpreter

---

<!--
This is a sample image, to show how to add images to your page. To learn more options, please refer [this](https://projects.ce.pdn.ac.lk/docs/faq/how-to-add-an-image/)

![Sample Image](./images/sample.png)
 -->

## Team

- E/20/157, Janakantha S.M.B.G., [e20157@eng.pdn.ac.lk](mailto:e20157@eng.pdn.ac.lk)

## Table of Contents

1. [Introduction](#introduction)
2. [Other Sub Topics](#other-sub-topics)
3. [Links](#links)

---

## Introduction

This project implements a Python-based interpreter for C-Lite, a simplified
subset of the C programming language. It demonstrates a complete language
processing pipeline with lexical analysis, recursive descent parsing, and
semantic evaluation. The interpreter is designed for educational use in
CO523 – Programming Languages at the University of Peradeniya.

## Other Sub Topics

### Features

- Two data types: int and float
- Variable declarations, assignments, and block scoping
- Arithmetic and comparison operators with correct precedence
- if/else conditional execution
- printf for multi-argument output
- Clear error reporting for lexer, parser, and runtime errors

### Usage

- Run a file: python main.py examples/sample.c
- Start REPL: python main.py
- Built-in tests: python main.py --test
- Pytest suite: pytest tests/

### Project Structure

- src/lexer.py: lexical analyzer
- src/parser.py: recursive descent parser
- src/ast_nodes.py: AST node definitions
- src/interpreter.py: tree-walking interpreter
- docs/index.html: project page and demo

### Report

- Project report (PDF): general/CO523_CLite_Report.pdf

## Links

- [Project Repository](https://github.com/cepdnaclk/20-co523-C_LITE-Interpreter)
- [Project Report (PDF)](../general/CO523_CLite_Report.pdf){:target="\_blank"}
- [Department of Computer Engineering](http://www.ce.pdn.ac.lk/)
- [University of Peradeniya](https://eng.pdn.ac.lk/)

[//]: # "Please refer this to learn more about Markdown syntax"
[//]: # "https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet"
