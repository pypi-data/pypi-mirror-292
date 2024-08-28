# from cbr_website_beta.cbr__fastapi.CBR__Fast_API import cbr_fast_api
#
# app  = cbr_fast_api.app()

import sys
import traceback
from fastapi import FastAPI, HTTPException

app = FastAPI()

try:
    from cbr_website_beta.cbr__fastapi.CBR__Fast_API import cbr_fast_api
    app = cbr_fast_api.app()
except Exception as e:
    error_message =  f"Catastrophic ERROR: Failed to initialize the CBR application due to the error: {str(e)}"
    traceback_details = traceback.format_exc()
    print(traceback_details, file=sys.stderr)

    # Define a basic error handler route to return the error message
    @app.get("/")
    def read_root():
        return error_message

    # Optionally, you can add more routes to handle other parts of your application