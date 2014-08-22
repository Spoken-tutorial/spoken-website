from django.dispatch import Signal

mask_on = Signal(providing_args=['mask_username',])

mask_off = Signal(providing_args=['mask_username',])
