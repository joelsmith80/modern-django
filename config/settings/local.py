from .base import *

DEBUG = env.bool('DJANGO_DEBUG', default=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default="g7&2l3k)0$tr!=rgrefxo6om@tqz+@340-w*i5*2v(nzm_+zsd")

