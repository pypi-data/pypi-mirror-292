# Metenox

AA module for Metenox management.

## Feature roadmap:
- [x] Estimate the value of moons by importing the [aa-moonmining](https://gitlab.com/ErikKalkoken/aa-moonmining) database
  - [ ] Displays the exact hourly pull of the moon
- [x] Import Metenoxes from a corp
  - [ ] Estimate corp monthly revenue
  - [ ] Notifications when low reagent/fuel
- [ ] Manager overview of corporations
  - [ ] Taxation?

### What this app won't do:
- Estimate moon price for athanor.
  Use [aa-moonmining](https://gitlab.com/ErikKalkoken/aa-moonmining)
- Ping when metenox are being reffed
  Use [aa-structures](https://gitlab.com/ErikKalkoken/aa-structures)

This module aims to be specific for Metenox management.

## Installation

### Step 1 - Check prerequisites

1. Metenox is a plugin for Alliance Auth. If you don't have Alliance Auth running already, please install it first before proceeding. (see the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/auth/allianceauth/) for details)

2. Metenox requires the Alliance Auth module [aa-moonmining](https://gitlab.com/ErikKalkoken/aa-moonmining) to function.
  The moon database and other utilities is imported from this module.

### Step 2 - Install app

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

```bash
pip install aa-metenox
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `'metenox'` to `INSTALLED_APPS`
- Add below lines to your settings file:

```python
CELERYBEAT_SCHEDULE['metenox_update_moon_prices'] = {
    'task': 'metenox.tasks.update_moon_prices',
    'schedule': crontab(minute='0', hour='*/12'),
}
CELERYBEAT_SCHEDULE['metenox_update_moons_from_moonminin'] = {
    'task': 'metenox.tasks.update_moons_from_moonmining',
    'schedule': crontab(minute='*/5'),
}
```

Optional: Alter the application settings.
The list can be found in [Settings](#settings)

### Step 4 - Finalize App installation

Run migrations & copy static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart your supervisor services for Auth.

### Setp 5 - Load Goo from ESI

Run the following management command to load all moon goos from ESI.
This only has to be ran once.

```bash
python manage.py metenox_load_eve
```

Wait until the command is finished before continuing.

### Step 5 - Load data

First load the data from the moonmining module using
```bash
python manage.py metenox_update_moons_from_moonmining
```

Once it's done update their prices with

```bash
python manage.py metenox_update_all_prices
```

## Settings

List of settings that can be modified for the application.
You can alter them by adding them in your `local.py` file.

| Name                                 | Descroption                                                                                      | Default |
|--------------------------------------|--------------------------------------------------------------------------------------------------|---------|
| 'METENOX_ADMIN_NOTIFICATIONS_ENABLE' | Whether admins will get notifications about important events like when someone adds a new owner. | True    |
|                                      |                                                                                                  |         |


## Dev notes

Load eveuniverse using
```shell
python manage.py eveuniverse_load_types --category_id_with_dogma 25 metenox
```

Generate `eveuniverse.json`
```shell
python ../myauth/manage.py test metenox.tests.testdata.create_eveuniverse --keepdb -v 2
```
