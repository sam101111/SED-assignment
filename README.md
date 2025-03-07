# Software engineering & DevOps assignment
For the Software engineering And DevOps assignment I have created a help desk where users can raise different types of issues which can then be reviewed by administrators. As specified in the brief, admins have full CRUD while users can only read,write and update. For privacy and security, users can only view their own issues they have raised while admins can view all issues and delete them if needed.

## installation
to run the application a few third party packages need to be installed, run the command bellow in the root directory:

```bash
pip install -r requirements.txt
```

## Running the application locally
> [!CAUTION]
> This application requires Python 3.12, it is highly suggested to use Python 3.12.4. Do not use 3.13.

to run a local instance of the application you can run the following command in the root of the project:

```bash
uvicorn app.main:app --reload   
```
## Deployed application
> [!CAUTION]
> The application may cold start and take a few minutes to be accessible due to the limitations of the free plan on the provider.

The application is deployed on: https://help-desk-app-assignment.onrender.com/login

## testing
Within this project both End-2-End and unit tests have been created.

> [!CAUTION]
> To run the playwright command you must first run ```bash pip install -r requirements.txt``` in the root of the project

to run the playwright end-2-end tests a you first need to run the following the in the root of the project:

```bash
playwright install
```
next run the following to run the unit tests and End-2-End tests:

```bash
pytest -vv
```

To run just the unit tests you can run:
```bash
pytest -k "unit"
```

To run just the e2e tests you can run:
```bash
pytest -k "e2e"
```


