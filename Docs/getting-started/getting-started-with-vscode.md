# Getting Started with VSCode

This notebook has been generated to begin a new phase of the HFT projects evolution where others will be invited to join a github repository to track the development.

The intent is that the previous work will be added to this as it reaches a stage of maturity that it is no longer considered in an experimantal stage and is placed her for use in further development.

Instructions will be placed in this notebook to track all the activities that need to be done to setup similar projects.

To create a new workspace in Visual Studio Code and publish it to GitHub, follow these steps:

1. Open Visual Studio Code.
2. Go to `File > New Window` to open a new workspace.
3. Go to `File > Open Folder...` and create a new folder for your workspace. This will be the root directory of your new project.
4. Create a new file or start adding code to your workspace.
5. Ondce you get to this stage you can save a workspace file in the root directory of the project by Using File->Save Worksapce As ...
6. Once you're ready to publish your workspace to GitHub, you'll need to initialize it as a Git repository. Open the terminal in VS Code (`View > Terminal`), navigate to your project's root directory, and run the following command:

git init

7. Add all the files in your workspace to the Git repository:

git add .

8. Commit your changes:

git commit -m "Initial commit"

This creates a local git repository

9. Go to GitHub and create a new repository. Do not initialize it with a README, .gitignore, or License.
10. After creating the repository, you'll be shown a page with several options to set up your repository. Under the "..or push an existing repository from the command line" section, copy the lines that start with `git remote add origin` and `git push -u origin main`.

```
// git remote add origin https://github.com/vandel/Ki2_Alerts.git

git branch -M main

git push -u origin main
```

```
// git remote add origin https://github.com/vandel/Ki2_Alerts.git git branch -M master
 git push -u origin main
```

11. Go back to the terminal in VS Code and paste the lines you copied from GitHub.

Your workspace is now a Git repository and has been published to GitHub. You can view your code on GitHub by navigating to your repository's URL.

To initialize a Python environment in a new Visual Studio Code workspace, you can create a virtual environment. Here are the steps:

1. Open Visual Studio Code.
2. Go to `File > New Window` to open a new workspace.
3. Open the terminal in VS Code (`View > Terminal`).
4. Navigate to your project's root directory.
5. Create a new virtual environment. If you're using Python 3, you can use the `venv` module to create the virtual environment:

````
// ```python -m venv venv
```
````

This command creates a new virtual environment named `venv` in your project's root directory.

6. Activate the virtual environment. On Windows, you can do this with the following command:

````
// ```.\venv\Scripts\activate
```
````

Or on Linux or MAC OS

````
// ```source venv/bin/activate
```
````

7. Once the virtual environment is activated, you can install Python packages using `pip`. These packages will be installed in the virtual environment, not globally on your system.
8. In VS Code, you'll need to select the interpreter for the workspace. Go to `View > Command Palette`, then search for `Python: Select Interpreter`. Choose the interpreter that corresponds to the virtual environment you just created.

Your new VS Code workspace is now set up with a Python environment. You can start adding Python files to your workspace and they'll use the packages and settings from the virtual environment.
