# Scriptmanager

The script creation system facilitates a contributor of the allotted FOSS category to create/upload and edit a script (in two column format i.e. cue and narration) for the Spoken Tutorial. There is a facility to add, remove, duplicate, and reorder the rows (scenes) in a script. The reviewer reviews the script(s) in the assigned FOSS category. He/She can publish and unpublish a script. Contributors and reviewers can communicate with each other using the Comments module. The comment creator can edit/delete/resolve the comment while the other can mark it as done indicating that the changes are incorporated. Revisions are maintained for each row (when the row of the script is saved). One can also revert to a particular version (row/scene) if needed. Once the script is published it cannot be edited and can be viewed by anyone.

## Installation
Before proceeding further make sure that you have pulled the code from the appropriate branch and have activated the virtual environment (if any).

### Requirements
```
sudo apt-get install python3.6-dev libmysqlclient-dev
pip install -r requirments.txt
pip install -r requirements-dev.txt
pip install -r requirements-py3.txt
pip install -r requirements.txt
```

### Libre Office
```
sudo apt-get install libreoffice
```

## Migrations and Collectstatic
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### Supporting Unicode Characters
To support special characters and other languages, two tables need to be altered. The MySQL commands are given below.

```
ALTER TABLE scriptmanager_script
   DEFAULT CHARACTER SET utf8mb4,
   MODIFY suggested_title varchar(255)
     CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL;
```

```
ALTER TABLE scriptmanager_scriptdetail
  DEFAULT CHARACTER SET utf8mb4,
   MODIFY cue longtext
     CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
   MODIFY narration longtext
     CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL;
```

## Changes needed to the build 
* This is applicable on Test/Production server that does not have Angular
* Edit /static/scriptmanager/main.js
* Locate 'localhost:8000' in the file and replace with the desired IP/Domain:Port
  ```
  i={production:!0,apiUrlScript:"http://<IP/Domain:Port>/scripts/api"}
  return this.http.post("http://<IP/Domain:Port>/api-token-auth/"
  ```

## Restart services
This is applicable on Test/Production server
```
sudo service nginx restart
sudo service supervisor restart
```

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 7.3.9.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
