#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
import base64

#%%

b64_utf8 = None
with open('logo.png', 'rb') as img_file:
    b64_bytes = base64.b64encode(img_file.read())
    b64_utf8 = b64_bytes.decode('utf-8')
    
with open('logo_b64.txt', 'w') as f:
    f.write(b64_utf8)
