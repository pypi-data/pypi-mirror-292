# eurmlsdk

## Overview

Welcome to the eurmlsdk package! This package provides a set of commands to streamline model deployment, validation, and prediction tasks for machine learning models. Whether deploying models remotely, evaluating model performance, or making predictions, the eurmlsdk package offers a comprehensive set of tools to support various machine learning workflows.

## Features

- **Model Prediction:** Deploy pre-trained models for real-time object detection tasks.
- **Model Visualization:** Visualizing model for an deep dive understanding on model architecture and parameters
- **Validation Utilities:** Evaluate model performance with precisions.



## Getting Started

To get started with eurmlsdk, follow these steps:

1. Install the eurmlsdk package from python package index.
2. Refer to the documentation for detailed usage instructions.

## Installation

You can install eurmlsdk via pip:

```bash
pip install eurmlsdk

```
## eurmlsdk Package Commands - Generic

1. **Help Command:**
   - **Syntax:** `help | --h`
   - **Description:** Lists all available commands in the eurmlsdk package, providing users with quick access to command documentation and usage information.

2. **Predict Command:**
   - **Syntax:** `predict <model path> <dataset path>`
   - **Description:** Performs predection using the specified model on the provided dataset. Predicts labels for the data samples and saves the predicted results for further analysis or usage.

3. **Validate Command:**
   - **Syntax:** `validate <task> <model path>`
   - **Description:** Validates the specified model using a default dataset appropriate for the given task. Evaluates the model's performance and returns relevant metrics, allowing users to assess the model's accuracy and suitability for the intended application.

4. **Visualization Command**
   - **Syntax:** `visualize <model_name>`
   - **Description:** Visualize the model and inference the model data with detailed analysis and hoist the
   information, allowing users to access and have deep dive understanding on the model architecture. 

## PyTorch Commands

1. **PyTorch Predict Command:**
   - **Syntax:** `pt-predict <modelname>`
   - **Description:** Performs inference using a PyTorch model specified by `modelname`. Predicts labels for the given dataset and prints the predicted results to the console, enabling users to quickly inspect model predictions.

2. **PyTorch List Model Command:**
   - **Syntax:** `pt-list-model`
   - **Description:** Lists all available models from toruch-hub that can be used for inference tasks. Provides users with an overview of the available models, facilitating model selection and usage in their projects.

## Options

- `<dataset path>`: Path to the input dataset, which can be an image or video file.
- `<hostname>`: Hostname of the remote server where the model will be deployed.
- `<model path>`: Path to the model file to be deployed or used for prediction/validation.
- `<model type>`: Type of the model, either 'yolo' or 'pt' (PyTorch).
- `<password>`: Password required to access the remote server.
- `<task>`: Validation task, such as 'seg' (segmentation), 'pose' (pose estimation), 'detect' (object detection), or 'classify' (classification).
- `<username>`: Username required to access the remote server.

---

## Supported Devices:

- [Raspberry PI](http://gitlab.embedur.local/product/model-zoo-sdk/-/blob/demo/eur-mlsdk/eurmlsdk/Documentation/Raspberry%20PI/Raspberry.md)

These commands provide users with a convenient interface for deploying models to Raspberry Pi devices, performing validation tasks, and making predictions using both yolo and PyTorch models. Whether for remote deployment, local inference, or model evaluation, the eurmlsdk package offers a comprehensive set of tools to support various machine learning workflows.
