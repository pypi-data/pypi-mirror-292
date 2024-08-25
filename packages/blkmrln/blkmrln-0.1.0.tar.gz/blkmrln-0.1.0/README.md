# blkmrln
 A python build tool optimized to setup for projects of any scale using modern python packaging and repository standards. Black formatting built in the name "blkmrln" is short for Black Marlin since this library will cut down your development time and skewer your dependencies all with black formatting. 

 ## Usage of the package
 To start using the package run "pip install blkmrln" from your terminal or command prompt. Once installed, if you would like to create a new project with blkmrln you can run the following 
 command: blkmrln build -n enter_project_name -e /full/path/to/folder/you/want/venvs/stored

 Note that whereever this command is run it will treat the current directory as the working directory and create a new folder within your current directory with which name you provide after
 the n flag. The primary advantage to using blkmrln is that we provide a single source of truth for your python projects, and we emphasize development standards at every step of the build process. 

 You will notice after running the build command a message is printed showing you how to activate the virtual environment for the project and how to cd to the project path. blkmrln creates a
 build object that automatically links all of your projects to their appropriate dependencies and allows for the rest of the commands within the library to always have context on the current
 project build definition. With this type of relationship between source code and build blkmrln attempts to introduce a first of its kind formal build process for python that meets all the needs of your modern developer coming from any language background.

 Other commands are still in active development, but you can see the architectural outline for each command with the /blkmrln folder or within their respective source folder.  

 ### Media

 #### Basic Commands Outside of Project Folder
 ![Basic Commands Outside of Project Folder](https://github.com/nickornator9000/blkmrln/blob/9ff534d352e3dda014e61928e54bd40e552507df/media/Basic%20Commands.png)

#### Basic Commands Inside of Project Folder
  ![Basic Commands Inside of Project Folder](https://github.com/nickornator9000/blkmrln/blob/9ff534d352e3dda014e61928e54bd40e552507df/media/Basic%20Commands%20Project%20Context.png)

## Developing the package
If you would like to develop the package please follow the outlined procedure and ensure that you read all steps before starting:
1. Fork the Repository: The contributor creates a personal copy (fork) of the original repository (often called the "upstream" repository) in their GitHub account or another platform. This gives them their own version of the project to work on.
2. Clone the Forked Repository: The contributor clones their forked repository to their local machine to work on it.
3. Create a New Branch: Before making changes, the contributor creates a new branch in their local repository. This branch is usually named after the feature, bug fix, or enhancement they are working on.
4. Make Changes and Commit: The contributor makes changes to the codebase in their new branch. They should commit these changes with clear and descriptive commit messages.
5. Push the Changes to the Fork: After making and committing changes locally, the contributor pushes the changes to their forked repository on GitHub (or another platform).

Please note that all changes must first be done in the /src folder of the repository within the folder corresponding to the command the developer is changing. Once the change is implemented you will need to create unit tests to ensure that the code is as covered as possible without veering into the territory of integration testing. Once all of your code and in /src and your unit tests are written follow the next steps:

6. Create a Pull Request (PR): Once the changes are pushed, the contributor creates a pull request from their forked repository's branch to the original repository's main branch (or another branch if specified).
7. Review and Feedback: The maintainers of the original repository review the pull request. They may ask for changes or provide feedback. The contributor makes any necessary updates and pushes them to the same branch in their forked repository, which automatically updates the pull request.
8. If the change is approved, you will take the code that you have written in the respective /src folder and implement it within your forked repo in the necessary file within the "blkmrln" package directory. Write the necessary integration tests to prove that your change does not break the package and then repeat steps 6 and 7. 
9. Once integration testing is done and approved the change will be merged into the package. 

## Architecture & Class Structure
### Media

#### Architecture
![Architecture](https://github.com/nickornator9000/blkmrln/blob/cac201426938922a6c9117252e4046bfae4a0ec2/media/Architecture.png)

#### Inheritance Model
![Basic Commands Inside of Project Folder](https://github.com/nickornator9000/blkmrln/blob/cac201426938922a6c9117252e4046bfae4a0ec2/media/Inheritance%20Model.png)
