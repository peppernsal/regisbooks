import webpy

import secret_keys

def handler(app: webpy.App, *args):
	from flask import redirect

	if app.debug: return redirect(secret_keys.TEST_REGISBOOKS_AUTH_URL)

	return redirect(secret_keys.AUTH_URL)
