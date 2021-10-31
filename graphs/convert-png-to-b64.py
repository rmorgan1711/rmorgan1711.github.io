#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%%
import base64

#%%

b64_str = None
with open('logo.png', 'rb') as img_file:
    b64_str = base64.b64encode(img_file.read())
    
print(b64_str)