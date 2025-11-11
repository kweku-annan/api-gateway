#!/usr/bin/env python3
"""JWT authentication middleware."""
from functools import wraps
from flask import request, current_app
from api.models.request_models import StandardResponse
import jwt