# flask-gem
A Library to generate a Flask app.

# Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Prerequisites

Before installing, make sure you have the following installed:

- Python 3.x
- pip

## Installation

### Installing via pip
Install the library using `pip`:

```sh
pip install flask-gem
```
### Manual Installation
If you prefer, you can manually install the library by cloning the repository:
```sh
git clone https://github.com/sushmithapopuri/flask-gem.git
cd flask-generator
pip install .
```
## Usage
### App Generation
this command helps to generate a skeleton flask app.
```sh
scaffold new <app-name>
```
Installing requirements and the app is ready
```sh
cd <app-name>
pip install -r requirements.txt
```
### Resource Generation
Generating a controller, a model and a view made simple
```sh
scaffold generate scaffold posts author:string description:text
```
For generating a controller/ model alone:
```sh
scaffold generate model posts author:string description:text
scaffold generate controller posts author:string description:text
scaffold generate view posts author:string description:text
```
### Starting the App
Migrating the DB, SQLITE here using flask-migrate and the app is ready for demo
```sh
flask db init
flask db migrate
flask db upgrade
flask run
```

## Features

<ol>
<li> Generate a Flask application from scratch</li>
<li> Create controllers, views with simple commands in rails style</li>
<li> Web pages neatly aligned</li>
<li> Cleanup of code using destroy command</li>
</ol>

## Contributing
Contributions are welcome! Please follow these steps:
<ol>
<li>Fork the repository.</li>
<li>Create a new branch: git checkout -b feature-branch.</li>
<li>Make your changes.
<li>Commit your changes: git commit -m 'Add some feature'.</li>
<li>Push to the branch: git push origin feature-branch.</li>
<li>Open a pull request.</li>
</ol>

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any questions, issues, or suggestions, please reach out:

Maintainer: Sushmitha Popuri
Email: sushmithapopuri@ymail.com
