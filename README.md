# Run TrueLove 

This repository contains the source code for the TrueLove

## Features

- Provides backend functionality for the TrueLove application.
- Integrates with Firebase for data storage and management.
- Includes endpoints for user authentication, profile management, and more.

## Requirements
- Firebase project with Realtime Database enabled
- Docker:
  - **MacOS**: Follow the installation instructions on the [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/) page.
  - **Windows**: Follow the installation instructions on the [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/) page.
  - **Linux**: Refer to the installation instructions for your specific Linux distribution on the [Docker Engine](https://docs.docker.com/engine/install/) page.


## Installation

1. Clone the repository:

```bash
git clone https://github.com/jdom1824/TrueLove.git 
```
2. Navigate to the project directory:

```bash
cd TrueLove
```
3. Load the Docker Image from the .tar File
Use the following command to load the Docker image from the downloaded .tar file:

```bash
docker load -i TrueLove.tar
```
4. Run the Docker Container
Now that the Docker image is loaded, you can run the container using the following command:

```bash
docker run -it truelove /bin/bash
```
5. Run TrueLove
```bash
./Init
```
6. Register User

```bash
No users.
Enter your username to register:
```

7. KEEP YOUR PRIVATE KEY IN A SAFE PLACE FOR FUTURE REWARDS

```bash
ID: 1, Username: user, Public Key: XXXXX, Private Key: XXXX
```
8. **Check Your Progress on the DASHBOARD**
   [https://truelove-78718.web.app/](https://truelove-78718.web.app/)

# Contribution
We welcome contributions from the community to improve and enhance the TrueLove project. Whether you're fixing a bug, adding a new feature, or improving the documentation, your efforts can help make TrueLove even better for everyone. To contribute, simply fork the repository, make your changes, and submit a pull request. Don't hesitate to reach out if you have any questions or need assistance. Together, let's make TrueLove the best it can be!
