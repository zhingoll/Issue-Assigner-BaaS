# Issue-Assigner
Issue-Assigner is a comprehensive solution designed to automate the assignment of issues in a repository. It integrates seamlessly with your development workflow to recommend the most suitable developers for resolving specific issues, thereby enhancing efficiency and collaboration.
<div align=center>
<img src="issueassign_framework.png" width="650px">
</div>
<p align="center">Issue-Assigner Framework</p>

## Features
### 1. Frontend Plugin Functionality
- **Display Recommendations:** Shows recommended developers for the current issue directly within the issue interface.
- **Model Selection:** Allows users to choose from different available models to view various recommendation results.
- **Feedback Mechanism:** Users can provide feedback on the recommendations using a thumbs-up (approve) or thumbs-down (disapprove).
### 2. Issue Assignment Task Benchmark
- **Unified Framework:** Implements various models for training and testing under a unified framework using [PyTorch Geometric (PyG)](https://github.com/pyg-team/pytorch_geometric).
- **Module composition:** Includes dataset construction, data loading, and model design tailored for issue assignment tasks.
### 3. Backend Service Functionality
- **Result Storage:** Stores the recommended results post-model testing for frontend display.
- **Feedback Storage and Evaluation:** Records real user feedback from the frontend and utilizes the [OpenRank](https://dl.acm.org/doi/10.1145/3639477.3639734) for subsequent model evaluation (feature under development).

## Project Structure
```plaintext
├── config/             # Model configuration files
├── data/               # Data loading
├── dataset/            # Dataset construction and preprocessing
├── frontend/           # Frontend plugin files
├── model/              # Model implementation, training, and testing
├── server/             # Backend service using FastAPI
├── tools/              # Some toolkits, such as NLP processing and logging tools
├── IssueAssign.py      # IssueAssign class for unified management of models
├── main.py             # Entry point for model training and testing
├── LICENSE             # Open source software license
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Installation
### Prerequisites
- **Python:** 3.10.15
- **Torch:** 1.13.1
- **Git:** To clone the repository
- **Node.js and npm:** For frontend development (if you plan to modify the frontend)
- **Browser:** Currently only tested on Edge
- **MongoDB:** 7.0.1
### Clone the Repository
```bash
git clone https://github.com/zhingoll/Issue-Assigner.git
```
### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
### Running the Main Application
Navigate to the project's root directory and run:
```bash
python main.py
```
This command initiates the training and testing of models related to the issue assignment tasks.
### Using the Frontend Plugin
#### 1.Load the Plugin in the Browser
- Open the Edge browser (currently tested only on Edge).
- Enter developer mode by navigating to `edge://extensions/`.
- Enable the **Developer mode** toggle.
- Click on **Load unpacked** and select the `frontend` folder from the project directory.
#### 2.Start the Backend Service
In a new terminal window, navigate to the server directory:
```bash
cd server
```
Start the FastAPI service using Uvicorn:
```bash
uvicorn server:app --reload
```
#### 3.Interact with the Plugin
As the project is still in the experimental stage, the suggested issue is specified in the file `opened_issues.csv`. The project path example for this file is: `dataset\opendigger\raw\`. You can experience the functionality of the plugin by using the issue number provided in this file. 
- Use the provided interface to **select different models** and view their recommendations.
- Provide **feedback** using the thumbs-up or thumbs-down icons.

## Future Plans
- Feedback Integration: Utilize user feedback combined with the OpenRank algorithm for enhanced model evaluation (feature under development).
- Model Expansion: Incorporate additional models and algorithms to improve recommendation accuracy.
- Browser Compatibility: Extend plugin support to other browsers like Chrome and Firefox.

## Contact
If you have any questions or suggestions, feel free to open an issue~

## License
This project is licensed under the [Apache-2.0 license](LICENSE), please make sure abide by the licenses when using the project.







