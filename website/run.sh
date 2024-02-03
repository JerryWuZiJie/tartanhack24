cd database
rm data.db
sqlite3 data.db << EOF
.read schema.sql
EOF
cd ..
flask run
