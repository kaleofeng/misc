#!/bin/bash

cat << EOF > ../app/config/api.js
module.exports = ({ env }) => ({
  responses: {
    privateAttributes: ['created_by', 'updated_by', 'created_at', 'updated_at'],
  },
});

EOF
