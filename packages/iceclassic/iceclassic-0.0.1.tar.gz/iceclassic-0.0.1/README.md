# iceclassic

Toolkit for exploring data.

Long-term plan: public PyPI package with tools for manipulating data easily.

## Context

Primary use:
- used in class settings as a demonstration tool
- used by students to work on assignments
- used in interactive TeachBooks pages
- open source community for expanding applications

Related:
- `iceclassic` documentation: Sphinx pages (numpy documentation style) that illustrates the package features only (TeachBook  for application)
- TeachBook that introduces the Ice Classic, the package and explores various science, engineering, programming, modelling concepts
- Contributors should somehow be able to set up more complex analyses and share them with the community

## Features

Highest level:
- summarizes breakup record (and includes data in package) via ability to export data in many formats: as output (formatted tables, figures, etc) as well as in several ready-to-go data types (ndarray, dataframe, etc)
- includes a short list of extremely simple models (e.g., linear regression, univariate probability distributions, etc)
- facilitates exploration of modelling concepts (calibration, verification, validation)
- standardizes the way a prediction is defined, presented, etc
- let's one choose/explore assumption of "start date" for the year or "reference date"
- let's one explore the concept of prediction, extrapolation, etc (i.e., which info do you include, prediction variables, etc)

Lower levels:
- students will be asked to read documentation and read code explicitly to teach good practices for programming
- if possible, consider usage of various data types as well as OOP versus functional paradigms
- names of objects are chosen very carefully
- Consider how decorators, BMI, etc, could be used to incorporate contributions and modularity
- advanced visualization is supported by the package via the design and implementation, but not accomplished internally
- figures must be handled carefully to ensure that best practices are illustrated; must be easy to produce and modify them

## Implementation

- pure Python package
- minimize dependencies (limit to common tools like Numpy, Scipy, etc)
- avoid large packages (import in webassembly should be fast)
- consider adopting BMI, or related frameworks
- object oriented, but not exclusively so
- should come packaged with a set of essential data (e.g., breakup record, discharge, stage, temperature, precipitation, snowfall, etc)

Can create a second package for "heavy" stuff, if needed. For example, setting up and running models.
