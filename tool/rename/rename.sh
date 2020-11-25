#!/bin/bash
ls | sed -r -n "s#(.*)(\.\w+)#mv '\1\2' '\1'#gp" | sh
