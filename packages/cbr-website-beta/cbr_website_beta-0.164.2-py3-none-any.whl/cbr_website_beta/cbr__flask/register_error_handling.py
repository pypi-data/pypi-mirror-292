import traceback

from flask                                                          import render_template, Flask
from werkzeug.exceptions                                            import NotFound
from cbr_website_beta._cbr_shared.dynamo_db.DyDB__CBR_Logging       import DyDB__CBR_Logging
from cbr_website_beta.cbr__flask.decorators.allow_annonymous        import allow_anonymous
from cbr_website_beta.config.Server_Config__CBR_Website import server_config__cbr_website
from osbot_utils.utils.Dev                                          import pprint
from osbot_utils.utils.Objects                                      import type_full_name, obj_info


def register_error_handling(app: Flask):

    dydb_cbr_logging = DyDB__CBR_Logging()

    @app.errorhandler(Exception)
    def internal_server_error(exception):
        if type(exception) is NotFound:
            return render_template('home/page-404.html', error=str(exception)), 404
        if server_config__cbr_website.dev__capture_exceptions():
            dydb_cbr_logging.log_exception(exception)
        error_message = f'{type(exception)} error: {exception}'
        return render_template('home/page-500.html', error=error_message), 500

    @app.route('/web/raise_exception')
    @allow_anonymous
    def cause_error():
        # This will cause an error and trigger the error handler
        return 1 / 0