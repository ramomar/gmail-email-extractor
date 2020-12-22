# gmail-email-extractor

This is an script for extracting emails from Gmail.

## Usage

In order to use it:

1. Install the project dependencies.
2. Go to the Google console and download your `credentials.json` in the root of the project.
3. Run `python main.py $QUERY`.

The script should download your emails to the `emails` folder in the root of the project.

## Example

```bash
python main.py ~/emails 'after:2019/05/05 from:notificacionesbanorte@banorte.com OR from:notificaciones@banorte.com'
```
