import io
import os
from contextlib import redirect_stdout

from flask import Flask, render_template, request

from catalog_utils import create_catalog
from conflict_resolver import resolve_all
from import_media import import_media
from sync_lib import sync

app = Flask(__name__)

_HOME = os.path.expanduser('~')
MEDIA_MANAGER_DIR = os.path.join(_HOME, 'Media Manager')
PHOTO_IN_DIR = os.path.join(MEDIA_MANAGER_DIR, 'Photo In')
PHOTO_STREAM_DIR = os.path.join(MEDIA_MANAGER_DIR, 'Photo Stream')


def ensure_dirs():
    os.makedirs(PHOTO_IN_DIR, exist_ok=True)
    os.makedirs(PHOTO_STREAM_DIR, exist_ok=True)


@app.route('/')
def index():
    return render_template('import.html',
                           default_src=PHOTO_IN_DIR,
                           default_dest=PHOTO_STREAM_DIR)


@app.route('/import', methods=['GET', 'POST'])
def import_page():
    if request.method == 'POST':
        src = request.form['src'].strip()
        dest = request.form['dest'].strip()
        is_catalog = 'catalog' in request.form
        is_remove = 'remove' in request.form
        is_norename = 'norename' in request.form
        is_copyright = 'copyright' in request.form
        is_watermark = 'watermark' in request.form
        is_photo_stream = 'photo_stream' in request.form

        if not os.path.isdir(src):
            return render_template('import.html', error=f"Source path not found: {src}",
                                   default_src=PHOTO_IN_DIR, default_dest=PHOTO_STREAM_DIR)
        if not os.path.isdir(dest):
            return render_template('import.html', error=f"Destination path not found: {dest}",
                                   default_src=PHOTO_IN_DIR, default_dest=PHOTO_STREAM_DIR)

        db_loc = os.path.join(dest, 'catalog.db')
        if not os.path.exists(db_loc) and not is_catalog:
            return render_template('import.html',
                                   error="No catalog found at destination. Check 'Create catalog' to create one.",
                                   default_src=PHOTO_IN_DIR, default_dest=PHOTO_STREAM_DIR)

        output = io.StringIO()
        error = None
        try:
            with redirect_stdout(output):
                if not os.path.exists(db_loc) and is_catalog:
                    create_catalog(dest)
                import_media(src, dest,
                             is_remove=is_remove,
                             catalog=is_catalog,
                             norename=is_norename,
                             is_copyright=is_copyright,
                             is_watermark=is_watermark,
                             is_photo_stream=is_photo_stream)
        except Exception as e:
            error = str(e)

        return render_template('result.html', output=output.getvalue(), error=error, back='/import')

    return render_template('import.html',
                           default_src=PHOTO_IN_DIR,
                           default_dest=PHOTO_STREAM_DIR)


@app.route('/sync', methods=['GET', 'POST'])
def sync_page():
    if request.method == 'POST':
        src = request.form['src'].strip()
        dest = request.form['dest'].strip()
        is_test = 'test' in request.form

        if not os.path.isdir(src):
            return render_template('sync.html', error=f"Source path not found: {src}")
        if not os.path.isdir(dest):
            return render_template('sync.html', error=f"Destination path not found: {dest}")

        output = io.StringIO()
        error = None
        try:
            with redirect_stdout(output):
                sync(src, dest, test=is_test)
        except Exception as e:
            error = str(e)

        return render_template('result.html', output=output.getvalue(), error=error, back='/sync')

    return render_template('sync.html')


@app.route('/conflicts', methods=['GET', 'POST'])
def conflicts_page():
    if request.method == 'POST':
        directory = request.form['directory'].strip()
        dry_run = 'apply' not in request.form

        if not os.path.isdir(directory):
            return render_template('conflicts.html', error=f"Directory not found: {directory}")

        count, results = resolve_all(directory, dry_run=dry_run)
        mode = 'Dry run' if dry_run else 'Applied'
        output = f"[{mode}] {count} conflict(s) found\n\n" + '\n'.join(results)
        return render_template('result.html', output=output, back='/conflicts')

    return render_template('conflicts.html',
                           default_dir=PHOTO_STREAM_DIR)


if __name__ == '__main__':
    ensure_dirs()
    app.run(debug=True, host='127.0.0.1', port=5000)
