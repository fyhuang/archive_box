from flask import render_template

from . import app, workspace, factory

@app.route("/")
def index() -> str:
    collections = [{"id": key, "name": value["display_name"]}
            for key, value in workspace.config.get("collections", {}).items()]

    scanner_state = factory.new_scanner_state()
    scanned_files = scanner_state.get_all_scanned()

    return render_template(
        'index.html',
        collections=collections,
        scanned_files=scanned_files,
    )
